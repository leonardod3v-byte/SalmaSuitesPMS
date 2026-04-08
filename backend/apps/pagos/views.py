from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Q

from .models import Pago, CierreCaja
from .serializers import PagoSerializer, CierreCajaSerializer
from apps.reservaciones.models import Reserva
from apps.reservaciones.views import registrar_actividad


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def pagos_list(request):
    """
    GET: Lista pagos con filtros opcionales.
         /api/pagos/?metodo=zelle
         /api/pagos/?reserva=5
         /api/pagos/?fecha=2026-03-14
    POST: Registra un nuevo pago para una reserva.
    """
    if request.method == 'GET':
        qs = Pago.objects.select_related('reserva', 'registrado_por').all()

        metodo = request.query_params.get('metodo')
        reserva_id = request.query_params.get('reserva')
        fecha = request.query_params.get('fecha')

        if metodo:
            qs = qs.filter(metodo=metodo)
        if reserva_id:
            qs = qs.filter(reserva_id=reserva_id)
        if fecha:
            qs = qs.filter(fecha__date=fecha)

        serializer = PagoSerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = PagoSerializer(data=request.data)
        if serializer.is_valid():
            pago = serializer.save(registrado_por=request.user)

            # Actualizar monto pagado en la reserva automáticamente
            reserva = pago.reserva
            total_pagado = Pago.objects.filter(
                reserva=reserva
            ).aggregate(total=Sum('monto'))['total'] or 0

            reserva.monto_pagado = total_pagado

            # Si ya pagó todo, cambiar estado a pagada
            if total_pagado >= reserva.monto_total:
                reserva.estado = 'pagada'

            reserva.save()

            registrar_actividad(
                tipo='pago',
                descripcion=f'Pago ${pago.monto} ({pago.metodo}) - H-{reserva.habitacion.numero}',
                usuario=request.user,
                reserva=reserva,
                habitacion=reserva.habitacion,
                huesped=reserva.huesped
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def resumen_pagos_hoy(request):
    """
    Resumen de ingresos del día agrupados por método de pago.
    Usado en el dashboard y para preparar el cierre de caja.
    """
    hoy = timezone.now().date()
    pagos_hoy = Pago.objects.filter(fecha__date=hoy)

    # Agrupar por método
    resumen = {}
    metodos = [m[0] for m in Pago.METODOS_PAGO]

    for metodo in metodos:
        total = pagos_hoy.filter(metodo=metodo).aggregate(
            total=Sum('monto')
        )['total'] or 0
        resumen[metodo] = float(total)

    total_general = pagos_hoy.aggregate(total=Sum('monto'))['total'] or 0

    return Response({
        'fecha': hoy,
        'desglose': resumen,
        'total': float(total_general)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def generar_cierre_caja(request):
    """
    RF07: Genera el cierre de caja del día para el recepcionista.
    Consolida automáticamente todos los pagos del día.
    Solo se puede hacer un cierre por día por recepcionista.
    """
    hoy = timezone.now().date()

    # Verificar que no exista ya un cierre para hoy
    if CierreCaja.objects.filter(recepcionista=request.user, fecha=hoy).exists():
        return Response(
            {'error': 'Ya existe un cierre de caja para hoy.'},
            status=400
        )

    # Calcular totales por método de pago del día
    pagos_hoy = Pago.objects.filter(
        fecha__date=hoy,
        registrado_por=request.user
    )

    def total_metodo(metodo):
        return pagos_hoy.filter(metodo=metodo).aggregate(
            t=Sum('monto')
        )['t'] or 0

    cierre = CierreCaja(
        recepcionista=request.user,
        fecha=hoy,
        efectivo_usd=total_metodo('efectivo_usd'),
        efectivo_ves=total_metodo('efectivo_ves'),
        transferencias=total_metodo('transferencia'),
        tarjetas=total_metodo('tarjeta'),
        pago_movil=total_metodo('pago_movil'),
        zelle=total_metodo('zelle'),
        binance=total_metodo('binance'),
        observaciones=request.data.get('observaciones', '')
    )
    cierre.calcular_total()
    cierre.save()

    registrar_actividad(
        tipo='cierre_caja',
        descripcion=f'Cierre de caja - {request.user.username} (${cierre.total_caja})',
        usuario=request.user
    )

    serializer = CierreCajaSerializer(cierre)
    return Response(serializer.data, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def historial_cierres(request):
    """
    Lista los cierres de caja.
    Recepcionistas solo ven los suyos, admin ve todos.
    """
    if request.user.role == 'admin':
        cierres = CierreCaja.objects.select_related('recepcionista').all()
    else:
        cierres = CierreCaja.objects.filter(recepcionista=request.user)

    serializer = CierreCajaSerializer(cierres, many=True)
    return Response(serializer.data)