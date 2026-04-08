from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def dashboard_stats(request):
    """
    RF02: Cards resumen del dashboard.
    Retorna ocupación, reservas, ingresos y VIPs del día.
    """
    from apps.habitaciones.models import Habitacion
    from apps.reservaciones.models import Reserva
    from apps.pagos.models import Pago

    hoy = timezone.now().date()
    ayer = hoy - timedelta(days=1)

    # ── Ocupación ──────────────────────────────────────────
    total_habitaciones = Habitacion.objects.count()
    ocupadas = Habitacion.objects.filter(estado='ocupada').count()
    ocupacion_pct = round((ocupadas / total_habitaciones) * 100) if total_habitaciones else 0

    ocupadas_ayer = Habitacion.objects.filter(
        reservas__fecha_entrada__lte=ayer,
        reservas__fecha_salida__gt=ayer,
        reservas__estado='pagada'
    ).count()
    trend_ocupacion = calcular_trend(ocupadas, ocupadas_ayer)

    # ── Reservas hoy ───────────────────────────────────────
    reservas_hoy = Reserva.objects.filter(
        fecha_entrada=hoy
    ).count()

    check_ins_pendientes = Reserva.objects.filter(
        fecha_entrada=hoy,
        estado__in=['confirmada', 'pagada']
    ).count()

    check_outs_pendientes = Reserva.objects.filter(
        fecha_salida=hoy,
        estado='pagada'
    ).count()

    # ── Ingresos del día ───────────────────────────────────
    ingresos_hoy = Pago.objects.filter(
        fecha__date=hoy
    ).aggregate(total=Sum('monto'))['total'] or 0

    ingresos_ayer = Pago.objects.filter(
        fecha__date=ayer
    ).aggregate(total=Sum('monto'))['total'] or 0

    trend_ingresos = calcular_trend(float(ingresos_hoy), float(ingresos_ayer))

    # ── Huéspedes VIP hoy ──────────────────────────────────
    vip_hoy = Reserva.objects.filter(
        fecha_entrada=hoy,
        huesped__es_vip=True
    ).count()

    return Response({
        'ocupacion': {
            'porcentaje': ocupacion_pct,
            'ocupadas': ocupadas,
            'total': total_habitaciones,
            'trend': trend_ocupacion,
        },
        'reservas_hoy': {
            'total': reservas_hoy,
            'check_ins_pendientes': check_ins_pendientes,
            'check_outs_pendientes': check_outs_pendientes,
        },
        'ingresos_dia': {
            'monto': float(ingresos_hoy),
            'trend': trend_ingresos,
        },
        'vip_hoy': {
            'total': vip_hoy,
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ocupacion_semanal(request):
    from apps.habitaciones.models import Habitacion

    DIAS_ES = {
        0: 'Lun', 1: 'Mar', 2: 'Mié',
        3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'
    }

    hoy   = timezone.now().date()
    total = Habitacion.objects.count()
    dias  = []
    valores = []

    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=i)

        ocupadas = Habitacion.objects.filter(
            reservas__fecha_entrada__lte=fecha,
            reservas__fecha_salida__gt=fecha,
            reservas__estado__in=['pagada', 'confirmada', 'sin_pagar']
        ).distinct().count()

        pct = round((ocupadas / total) * 100) if total else 0

        dias.append(DIAS_ES[fecha.weekday()])
        valores.append(pct)

    return Response({'dias': dias, 'valores': valores})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitaciones_grid(request):
    """
    RF02: Estado de todas las habitaciones para el grid del dashboard.
    """
    from apps.habitaciones.models import Habitacion

    habitaciones = Habitacion.objects.select_related('tipo').all()

    data = []
    for hab in habitaciones:
        # Mapear estados del backend a estados simples para el frontend
        estado_map = {
            'libre': 'libre',
            'limpia': 'libre',
            'sucia': 'mantenimiento',
            'ocupada': 'ocupada',
            'mantenimiento': 'mantenimiento',
            'construccion': 'mantenimiento',
        }
        data.append({
            'num': hab.numero,
            'estado': estado_map.get(hab.estado, 'ocupada'),
            'estado_real': hab.estado,
            'tipo': hab.tipo.nombre,
            'piso': hab.piso,
        })

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def actividades_dashboard(request):
    """
    RF02: Timeline de últimas acciones para el dashboard.
    """
    from apps.reservaciones.models import Actividad
    from apps.reservaciones.serializers import ActividadSerializer

    actividades = Actividad.objects.select_related(
        'usuario', 'habitacion', 'huesped'
    ).all()[:15]

    serializer = ActividadSerializer(actividades, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def alertas_dashboard(request):
    """
    Consolida todas las alertas activas del sistema:
    - Habitaciones en mantenimiento
    - Stock bajo o sin stock
    - Check-outs pendientes de hoy
    - Reservas sin pagar con fecha de entrada hoy
    """
    from apps.habitaciones.models import Habitacion
    from apps.inventario.models import Producto
    from apps.reservaciones.models import Reserva

    hoy = timezone.now().date()

    # Habitaciones en mantenimiento
    en_mantenimiento = Habitacion.objects.filter(
        estado__in=['mantenimiento', 'construccion']
    ).values('numero', 'estado')

    # Productos con stock bajo o sin stock
    productos_alerta = Producto.objects.filter(
        activo=True
    ).filter(
        Q(sin_stock=True) | Q(stock_bajo=True)
    ).values('nombre', 'stock_actual', 'sin_stock')

    # Check-outs pendientes hoy
    checkouts_pendientes = Reserva.objects.filter(
        fecha_salida=hoy,
        estado__in=['confirmada', 'pagada']
    ).select_related('huesped', 'habitacion').values(
        'id',
        'huesped__nombre',
        'huesped__apellido',
        'habitacion__numero'
    )

    # Reservas sin pagar con entrada hoy
    sin_pagar_hoy = Reserva.objects.filter(
        fecha_entrada=hoy,
        estado='sin_pagar'
    ).count()

    return Response({
        'habitaciones_mantenimiento': list(en_mantenimiento),
        'productos_alerta': list(productos_alerta),
        'checkouts_pendientes': list(checkouts_pendientes),
        'reservas_sin_pagar_hoy': sin_pagar_hoy,
        'total_alertas': (
            len(en_mantenimiento) +
            len(productos_alerta) +
            len(checkouts_pendientes) +
            sin_pagar_hoy
        )
    })


def calcular_trend(valor_hoy, valor_ayer):
    """
    Calcula el porcentaje de cambio entre hoy y ayer.
    Retorna un dict con el valor formateado y si subió o bajó.
    """
    if valor_ayer == 0:
        return {'valor': '+100%', 'subio': True}

    diferencia = ((valor_hoy - valor_ayer) / valor_ayer) * 100
    subio = diferencia >= 0
    valor_str = f'+{abs(round(diferencia))}%' if subio else f'-{abs(round(diferencia))}%'

    return {'valor': valor_str, 'subio': subio}