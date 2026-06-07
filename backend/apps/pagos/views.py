from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count

from .models import Pago, CierreCaja
from .serializers import PagoSerializer, CierreCajaSerializer
from apps.reservaciones.models import Reserva
from apps.reservaciones.views import registrar_actividad
from utils import paginar_queryset_funcion


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def pagos_list(request):
    """
    GET: Lista el histórico de pagos con JOINs optimizados y paginación.
    POST: Registra un pago de manera 100% atómica y concurrente.
    """
    if request.method == 'GET':
        # SQL N+1 Blindado: select_related para traer metadatos relacionales en una sola query
        qs = Pago.objects.select_related('reserva', 'registrado_por').all().order_by('-fecha')
        
        metodo = request.query_params.get('metodo')
        reserva_id = request.query_params.get('reserva')
        if metodo:
            qs = qs.filter(metodo=metodo)
        if reserva_id:
            qs = qs.filter(reserva_id=reserva_id)

        return paginar_queryset_funcion(request, qs, PagoListSerializer, page_size=20)

    if request.method == 'POST':
        reserva_id = request.data.get('reserva')
        if not reserva_id:
            return Response({'error': 'El ID de la reserva es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # CANDADO BD: Bloqueamos la fila de la reserva para evitar modificaciones concurrentes de montos
                reserva = Reserva.objects.select_for_update().get(pk=reserva_id)

                serializer = PagoSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                pago = serializer.save(registrado_por=request.user, reserva=reserva)

                # Mutamos las propiedades de la reserva de manera segura usando la lógica denormalizada del modelo
                reserva.monto_pagado += pago.monto
                
                # Actualización de estados del ciclo de vida del pago
                updated_fields_for_reserva = ['monto_pagado']
                if reserva.saldo_pendiente <= 0:
                    if reserva.estado == 'sin_pagar':
                        reserva.estado = 'confirmada'
                        updated_fields_for_reserva.append('estado')
                    elif reserva.estado == 'confirmada':
                        reserva.estado = 'pagada'
                        updated_fields_for_reserva.append('estado')

                if updated_fields_for_reserva:
                    reserva.save(update_fields=updated_fields_for_reserva)
                    reserva.refresh_from_db()

                # Auditoría del Timeline
                registrar_actividad(
                    tipo='pago',
                    descripcion=f'Pago ${pago.monto} ({pago.metodo}) - H-{reserva.habitacion.numero if reserva.habitacion else "N/A"}',
                    usuario=request.user,
                    reserva=reserva,
                    habitacion=reserva.habitacion,
                    huesped=reserva.huesped
                )

                return Response({
                    'message': 'Pago registrado exitosamente',
                    'pago_id': pago.id,
                    'reserva_id': reserva.id,
                    'monto_pagado_reserva': float(reserva.monto_pagado),
                    'saldo_pendiente': float(reserva.saldo_pendiente),
                    'estado_reserva': reserva.estado
                }, status=status.HTTP_201_CREATED)

        except Reserva.DoesNotExist:
            return Response({'error': 'Reserva no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error en la transacción financiera: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ejecutar_cierre_caja(request):
    """
    RF14: Cierre de caja diario por el recepcionista de turno de forma segura.
    """
    if request.user.role != 'recepcionista' and request.user.role != 'admin':
        return Response({'error': 'No tiene permisos para ejecutar el cierre de caja.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        with transaction.atomic():
            # Evita que se dupliquen cierres del mismo turno en ejecuciones asíncronas concurrentes
            cierre_existente = CierreCaja.objects.filter(
                recepcionista=request.user,
                fecha_cierre__date=timezone.now().date()
            ).exists()
            
            if cierre_existente:
                return Response({'error': 'Ya has registrado un cierre de caja para el día de hoy.'}, status=status.HTTP_400_BAD_REQUEST)

            monto_esperado = float(request.data.get('monto_esperado', 0))
            monto_real = float(request.data.get('monto_real', 0))
            observaciones = request.data.get('observaciones', '')

            desfase = monto_real - monto_esperado
            estado_cierre = 'cuadrado' if desfase == 0 else ('sobrante' if desfase > 0 else 'faltante')

            cierre = CierreCaja.objects.create(
                recepcionista=request.user,
                monto_esperado=monto_esperado,
                monto_real=monto_real,
                desfase=desfase,
                estado=estado_cierre,
                observaciones=observaciones
            )

            return Response({
                'message': 'Cierre de caja procesado exitosamente.',
                'cierre': CierreCajaSerializer(cierre).data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({'error': f'Error crítico procesando el arqueo de caja: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def historial_cierres(request):
    """
    RF15: Historial de cierres de caja (Admin ve todos, Recepcionista solo los suyos).
    """
    # SQL N+1 Blindado: select_related para optimizar el JOIN del recepcionista de caja
    if request.user.role == 'admin':
        qs = CierreCaja.objects.select_related('recepcionista').all().order_by('-fecha_cierre')
    else:
        qs = CierreCaja.objects.select_related('recepcionista').filter(recepcionista=request.user).order_by('-fecha_cierre')

    return paginar_queryset_funcion(request, qs, CierreCajaSerializer, page_size=15)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def resumen_pagos_hoy(request):
    """
    RF11/RF12: Retorna un desglose consolidado de los ingresos percibidos el día de hoy.
    Agrupa de manera nativa por método de pago para alimentar las métricas del Dashboard.
    """
    # Definimos el rango de tiempo estricto para "hoy" (desde las 00:00:00 hasta el final del día)
    ahora = timezone.now()
    hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Consulta optimizada agregando sumas por la fecha de registro
    pagos_de_hoy = Pago.objects.filter(fecha__range=(hoy_inicio, hoy_fin))

    # Total general del día
    consolidado = pagos_de_hoy.aggregate(
        monto_total=Sum('monto'),
        transacciones_totales=Count('id')
    )

    monto_total = consolidado['monto_total'] or 0.0
    total_transacciones = consolidado['transacciones_totales'] or 0

    # Desglose agrupado por métodos de pago (efectivo, transferencia, tarjeta, etc.)
    # Esto evita hacer múltiples hits a la base de datos
    desglose_metodos = (
        pagos_de_hoy.values('metodo')
        .annotate(total=Sum('monto'), conteo=Count('id'))
        .order_by('-total')
    )

    return Response({
        'fecha': hoy_inicio.date().isoformat(),
        'ingreso_total_hoy': monto_total,
        'transacciones_hoy': total_transacciones,
        'desglose_por_metodo': list(desglose_metodos)
    }, status=status.HTTP_200_OK)

generar_cierre_caja = ejecutar_cierre_caja