from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Notificacion
from .services import (
    notificar_confirmacion_reserva,
    notificar_recordatorio_pago,
    notificar_checkout_pendiente,
    notificar_bienvenida,
    enviar_whatsapp
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def notificaciones_list(request):
    """
    Lista el historial de notificaciones.
    Filtros opcionales:
    /api/notificaciones/?estado=fallida
    /api/notificaciones/?tipo=recordatorio_pago
    """
    qs = Notificacion.objects.all()

    estado = request.query_params.get('estado')
    tipo = request.query_params.get('tipo')
    reserva_id = request.query_params.get('reserva')

    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if reserva_id:
        qs = qs.filter(reserva_id=reserva_id)

    data = [{
        'id': n.id,
        'tipo': n.tipo,
        'canal': n.canal,
        'estado': n.estado,
        'destinatario': n.destinatario_nombre,
        'telefono': n.destinatario_telefono,
        'mensaje': n.mensaje,
        'error': n.error_detalle,
        'reserva_id': n.reserva_id,
        'created_at': n.created_at,
        'enviada_at': n.enviada_at,
    } for n in qs[:50]]

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def enviar_notificacion_reserva(request, reserva_id):
    """
    Envía manualmente una notificación para una reserva.
    Body: { "tipo": "confirmacion_reserva" }
    Tipos disponibles: confirmacion_reserva, recordatorio_pago,
                       checkout_pendiente, bienvenida
    """
    from apps.reservaciones.models import Reserva

    try:
        reserva = Reserva.objects.select_related(
            'huesped', 'habitacion__tipo'
        ).get(pk=reserva_id)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=404)

    tipo = request.data.get('tipo')

    manejadores = {
        'confirmacion_reserva': notificar_confirmacion_reserva,
        'recordatorio_pago': notificar_recordatorio_pago,
        'checkout_pendiente': notificar_checkout_pendiente,
        'bienvenida': notificar_bienvenida,
    }

    if tipo not in manejadores:
        return Response({
            'error': f'Tipo inválido. Opciones: {", ".join(manejadores.keys())}'
        }, status=400)

    resultado = manejadores[tipo](reserva, usuario=request.user)
    return Response(resultado)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def enviar_notificacion_personalizada(request):
    """
    Envía un mensaje de WhatsApp personalizado a cualquier número.
    Solo disponible para admin.
    Body: { "telefono": "+584241234567", "mensaje": "Hola..." }
    """
    if request.user.role != 'admin':
        return Response(
            {'error': 'Solo el administrador puede enviar mensajes personalizados.'},
            status=403
        )

    telefono = request.data.get('telefono')
    mensaje = request.data.get('mensaje')
    nombre = request.data.get('nombre', 'Destinatario')

    if not telefono or not mensaje:
        return Response({'error': 'telefono y mensaje son requeridos.'}, status=400)

    resultado = enviar_whatsapp(
        telefono=telefono,
        mensaje=mensaje,
        tipo='confirmacion_reserva',
        destinatario_nombre=nombre,
        usuario=request.user
    )

    return Response(resultado)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def procesar_recordatorios_automaticos(request):
    """
    RF11: Procesa y envía todos los recordatorios automáticos del día.
    - Recordatorios de pago: reservas con entrada mañana y saldo pendiente
    - Check-outs: reservas con salida hoy
    Idealmente se llamaría desde un cron job cada mañana.
    """
    from apps.reservaciones.models import Reserva
    from datetime import timedelta

    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)
    resultados = {'recordatorios_pago': 0, 'checkouts': 0, 'errores': 0}

    # Recordatorios de pago para mañana
    reservas_manana = Reserva.objects.filter(
        fecha_entrada=manana,
        estado__in=['confirmada', 'sin_pagar'],
        huesped__telefono__isnull=False
    ).exclude(huesped__telefono='').select_related('huesped', 'habitacion__tipo')

    for reserva in reservas_manana:
        if reserva.saldo_pendiente > 0:
            resultado = notificar_recordatorio_pago(reserva, usuario=request.user)
            if resultado.get('success'):
                resultados['recordatorios_pago'] += 1
            else:
                resultados['errores'] += 1

    # Check-outs pendientes de hoy
    checkouts_hoy = Reserva.objects.filter(
        fecha_salida=hoy,
        estado__in=['confirmada', 'pagada'],
        huesped__telefono__isnull=False
    ).exclude(huesped__telefono='').select_related('huesped', 'habitacion__tipo')

    for reserva in checkouts_hoy:
        resultado = notificar_checkout_pendiente(reserva, usuario=request.user)
        if resultado.get('success'):
            resultados['checkouts'] += 1
        else:
            resultados['errores'] += 1

    return Response({
        'message': 'Recordatorios procesados.',
        'resultados': resultados
    })