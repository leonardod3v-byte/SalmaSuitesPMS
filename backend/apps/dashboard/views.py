from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta
from rest_framework import status

from apps.reservaciones.models import Reserva
from apps.habitaciones.models import Habitacion
from apps.inventario.models import Producto
from apps.pagos.models import Pago


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def dashboard_stats(request):
    """
    Estadísticas principales del dashboard adaptadas al frontend Svelte.
    """
    hoy = timezone.now().date()
    ayer = hoy - timedelta(days=1)

    # --- CONSULTAS HOY ---
    reservas_hoy_qs = Reserva.objects.filter(fecha_entrada=hoy)
    total_reservas_hoy = reservas_hoy_qs.count()
    checkins_hoy = reservas_hoy_qs.filter(estado='check_in').count()
    
    ingresos_hoy = Pago.objects.filter(fecha__date=hoy).aggregate(total=Sum('monto'))['total'] or 0
    
    total_habitaciones = Habitacion.objects.count()
    ocupadas_hoy = Habitacion.objects.filter(estado='ocupada').count()
    porcentaje_ocupacion = round((ocupadas_hoy / total_habitaciones * 100), 1) if total_habitaciones > 0 else 0

    # --- CONSULTAS AYER (para trends) ---
    ingresos_ayer = Pago.objects.filter(fecha__date=ayer).aggregate(total=Sum('monto'))['total'] or 0
    ocupadas_ayer = Habitacion.objects.filter(estado='ocupada').count()

    # Pendientes de hoy
    check_ins_pendientes = Reserva.objects.filter(fecha_entrada=hoy, estado__in=['confirmada', 'pagada']).count()
    check_outs_pendientes = Reserva.objects.filter(fecha_salida=hoy, estado='check_in').count()

    # VIP (manejo seguro)
    vip_hoy = 0
    try:
        from apps.huespedes.models import Huesped
        vip_hoy = Huesped.objects.filter(
            reservas__fecha_entrada=hoy,
            es_vip=True
        ).distinct().count()
    except (ImportError, AttributeError):
        vip_hoy = 0

    # Función auxiliar para trends
    def calcular_trend(valor_hoy, valor_ayer):
        if not valor_ayer:
            return {'valor': '100%', 'subio': True} if valor_hoy > 0 else {'valor': '0%', 'subio': False}
        diff = valor_hoy - valor_ayer
        porcentaje = round((diff / valor_ayer) * 100, 1)
        return {
            'valor': f"{abs(porcentaje)}%",
            'subio': porcentaje > 0
        }

    return Response({
        'ocupacion': {
            'porcentaje': porcentaje_ocupacion,
            'ocupadas': ocupadas_hoy,
            'total': total_habitaciones,
            'trend': calcular_trend(ocupadas_hoy, ocupadas_ayer)
        },
        'reservas_hoy': {
            'total': total_reservas_hoy,
            'check_ins_pendientes': check_ins_pendientes,
            'check_outs_pendientes': check_outs_pendientes
        },
        'ingresos_dia': {
            'monto': float(ingresos_hoy),
            'trend': calcular_trend(ingresos_hoy, ingresos_ayer)
        },
        'vip_hoy': {
            'total': vip_hoy
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def dashboard_alertas(request):
    """
    Módulo de alertas críticas unificado y optimizado contra consultas N+1.
    """
    hoy = timezone.now().date()

    en_mantenimiento = Habitacion.objects.filter(estado='mantenimiento').values('id', 'numero', 'tipo')

    productos_alerta = Producto.objects.filter(
        Q(sin_stock=True) | Q(stock_bajo=True)
    ).values('nombre', 'stock_actual', 'sin_stock')

    checkouts_pendientes = Reserva.objects.filter(
        fecha_salida=hoy,
        estado__in=['confirmada', 'pagada']
    ).select_related('huesped', 'habitacion').values(
        'id',
        'huesped__nombre',
        'huesped__apellido',
        'habitacion__numero'
    )

    sin_pagar_hoy = Reserva.objects.filter(fecha_entrada=hoy, estado='sin_pagar').count()

    return Response({
        'habitaciones_mantenimiento': list(en_mantenimiento),
        'productos_alerta': list(productos_alerta),
        'checkouts_pendientes': list(checkouts_pendientes),
        'reservas_sin_pagar_hoy': sin_pagar_hoy,
        'total_alertas': len(en_mantenimiento) + len(productos_alerta) + len(checkouts_pendientes) + sin_pagar_hoy
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ocupacion_semanal(request):
    """
    Retorna ocupación de los últimos 7 días.
    """
    hoy = timezone.now().date()
    total_habitaciones = Habitacion.objects.count() or 1

    valores_porcentaje = []
    nombres_dias = []

    dias_es = {
        'Monday': 'Lun', 'Tuesday': 'Mar', 'Wednesday': 'Mié',
        'Thursday': 'Jue', 'Friday': 'Vie', 'Saturday': 'Sáb', 'Sunday': 'Dom'
    }

    for i in range(6, -1, -1):
        fecha_evaluacion = hoy - timedelta(days=i)

        habitaciones_ocupadas = Reserva.objects.filter(
            estado='check_in',
            fecha_entrada__lte=fecha_evaluacion,
            fecha_salida__gte=fecha_evaluacion
        ).values('habitacion').distinct().count()

        porcentaje_ocupacion = round((habitaciones_ocupadas / total_habitaciones) * 100, 2)

        dia_semana_en = fecha_evaluacion.strftime('%A')
        dia_semana_es = dias_es.get(dia_semana_en, dia_semana_en)

        valores_porcentaje.append(porcentaje_ocupacion)
        nombres_dias.append(dia_semana_es)

    return Response({
        'valores': valores_porcentaje,
        'dias': nombres_dias
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitaciones_grid(request):
    """
    Retorna array de habitaciones para el grid del frontend.
    """
    habitaciones_qs = Habitacion.objects.select_related('tipo').all().order_by('piso', 'numero')

    payload = []
    for hab in habitaciones_qs:
        tipo_nombre = hab.tipo.nombre if hab.tipo else 'Estándar'
        payload.append({
            'num': str(hab.numero),
            'estado': hab.estado,
            'tipo': tipo_nombre,
            'piso': hab.piso
        })
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def actividades_dashboard(request):
    """
    Retorna las últimas actividades para el timeline del dashboard.
    Devuelve un array de objetos con 'descripcion' y 'created_at'.
    """
    from apps.reservaciones.models import Actividad

    logs = Actividad.objects.select_related('usuario').all().order_by('-created_at')[:15]

    timeline = []
    for log in logs:
        timeline.append({
            'descripcion': log.descripcion,
            'created_at': log.created_at.isoformat()   # ← CAMBIADO: created_at
        })

    return Response(timeline, status=status.HTTP_200_OK)
    """
    Retorna las últimas actividades para el timeline del dashboard.
    Devuelve un array de objetos con 'descripcion' y 'created_at'.
    """
    from apps.reservaciones.models import Actividad  # ← Cambio importante

    logs = Actividad.objects.select_related('usuario').all().order_by('-fecha_registro')[:15]

    timeline = []
    for log in logs:
        timeline.append({
            'descripcion': log.descripcion,
            'created_at': log.fecha_registro.isoformat()  # ← usa 'fecha_registro'
        })

    return Response(timeline, status=status.HTTP_200_OK)
    """
    Retorna las últimas actividades para el timeline del dashboard.
    Devuelve un array de objetos con 'descripcion' y 'created_at'.
    """
    try:
        from apps.reservaciones.models import ActividadLog
    except ImportError:
        return Response([], status=status.HTTP_200_OK)

    logs = ActividadLog.objects.select_related('usuario').all().order_by('-fecha_registro')[:15]

    timeline = []
    for log in logs:
        timeline.append({
            'descripcion': log.descripcion,
            'created_at': log.fecha_registro.isoformat()
        })

    return Response(timeline, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def alertas_dashboard(request):
    """
    Endpoint de auditoría en tiempo real.
    """
    hoy_ahora = timezone.now()
    alertas = []

    # Habitaciones sucias
    habitaciones_sucias = Habitacion.objects.filter(estado='sucia').values_list('numero', flat=True)
    if habitaciones_sucias.exists():
        alertas.append({
            'nivel': 'warning',
            'categoria': 'infraestructura',
            'mensaje': f"Hay {habitaciones_sucias.count()} habitaciones sucias que requieren atención.",
            'detalles': [f"H-{num}" for num in habitaciones_sucias]
        })

    # Check-outs vencidos
    checkouts_vencidos = Reserva.objects.filter(
        estado='check_in',
        fecha_salida__lt=hoy_ahora
    ).select_related('huesped', 'habitacion')
    if checkouts_vencidos.exists():
        alertas.append({
            'nivel': 'danger',
            'categoria': 'operativa',
            'mensaje': f"Atención: Se detectaron {checkouts_vencidos.count()} check-outs retrasados.",
            'detalles': [
                f"H-{res.habitacion.numero if res.habitacion else 'N/A'} - {res.huesped.nombre} (Venció: {res.fecha_salida.strftime('%I:%M %p')})"
                for res in checkouts_vencidos
            ]
        })

    # Productos críticos
    productos_criticos = Producto.objects.filter(
        Q(sin_stock=True) | Q(stock_bajo=True), activo=True
    )
    if productos_criticos.exists():
        quiebres = productos_criticos.filter(sin_stock=True).count()
        bajos = productos_criticos.filter(stock_bajo=True).count()
        alertas.append({
            'nivel': 'danger' if quiebres > 0 else 'warning',
            'categoria': 'inventario',
            'mensaje': f"Alerta de almacén: {quiebres} productos agotados y {bajos} con stock mínimo.",
            'detalles': [f"{p.nombre} (Disponibles: {p.stock_actual})" for p in productos_criticos[:5]]
        })

    return Response({
        'timestamp': hoy_ahora.isoformat(),
        'conteo_alertas': len(alertas),
        'alertas': alertas
    }, status=status.HTTP_200_OK)