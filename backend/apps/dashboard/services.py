from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q

from apps.habitaciones.models import Habitacion
from apps.reservaciones.models import Reservacion
from apps.reservaciones.models import Pago
from apps.huespedes.models import Huesped
from apps.inventario.services import productos_bajos


def obtener_kpis():
    hoy = date.today()

    # Ocupación real
    total_habitaciones = Habitacion.objects.count()
    en_mantenimiento_obra = Habitacion.objects.filter(estado__in=['Mantenimiento', 'Obra']).count()
    disponibles = total_habitaciones - en_mantenimiento_obra
    ocupadas = Habitacion.objects.filter(estado='Ocupada').count()
    ocupacion_pct = round((ocupadas / disponibles) * 100, 1) if disponibles > 0 else 0

    # Check-in hoy
    checkins_hoy = Reservacion.objects.filter(fecha_checkin_real__date=hoy, estado='EnCurso').count()

    # Flujo de caja hoy
    pagos_hoy = Pago.objects.filter(fecha_hora__date=hoy)
    total_efectivo = pagos_hoy.filter(metodo_pago='Efectivo').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_tarjeta = pagos_hoy.filter(metodo_pago='Tarjeta').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_pago_movil = pagos_hoy.filter(metodo_pago='PagoMovil').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    flujo_total = total_efectivo + total_tarjeta + total_pago_movil

    from apps.reservaciones.models import ReservacionHuespedes

    vip_ids = Reservacion.objects.filter(
        estado='EnCurso'
    ).values_list('id_huesped_titular_id', flat=True).distinct()

    acompanantes_ids = ReservacionHuespedes.objects.filter(
        id_reservacion__estado='EnCurso',
        rol='Acompañante'
    ).values_list('id_huesped_id', flat=True).distinct()

    todos_ids = set(vip_ids) | set(acompanantes_ids)
    total_vip = Huesped.objects.filter(id__in=todos_ids, categoria='VIP').count()

    try:
        productos_bajos_count = productos_bajos()
    except Exception:
        productos_bajos_count = 0

    return {
        'ocupacion': {
            'porcentaje': ocupacion_pct,
            'ocupadas': ocupadas,
            'disponibles': disponibles,
            'total': total_habitaciones,
            'mantenimiento_obra': en_mantenimiento_obra,
        },
        'checkins_hoy': checkins_hoy,
        'flujo_caja': {
            'total': str(flujo_total),
            'efectivo': str(total_efectivo),
            'tarjeta': str(total_tarjeta),
            'pago_movil': str(total_pago_movil),
        },
        'vip_alojados': total_vip,
        'productos_bajos': productos_bajos_count,
    }


def obtener_ocupacion_semanal():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)

    total_habitaciones = Habitacion.objects.count()
    en_mantenimiento_obra = Habitacion.objects.filter(estado__in=['Mantenimiento', 'Obra']).count()
    disponibles_base = total_habitaciones - en_mantenimiento_obra

    resultados = []
    for i in range(7):
        dia = lunes + timedelta(days=i)
        if dia <= hoy:
            ocupadas = Habitacion.objects.filter(
                reservaciones__fecha_entrada__lte=dia,
                reservaciones__fecha_salida__gte=dia + timedelta(days=1),
                reservaciones__estado__in=['EnCurso', 'Finalizada', 'Confirmada']
            ).distinct().count()
        else:
            ocupadas = Habitacion.objects.filter(
                reservaciones__fecha_entrada__lte=dia,
                reservaciones__fecha_salida__gte=dia + timedelta(days=1),
                reservaciones__estado='Confirmada'
            ).distinct().count()

        pct = round((ocupadas / disponibles_base) * 100, 1) if disponibles_base > 0 else 0
        resultados.append({
            'dia': dia.strftime('%A'),
            'fecha': dia.isoformat(),
            'ocupadas': ocupadas,
            'disponibles': disponibles_base,
            'porcentaje': pct,
        })

    promedio = round(sum(r['porcentaje'] for r in resultados) / 7, 1)
    return {'semana': lunes.isoformat(), 'dias': resultados, 'promedio': promedio}


def proximos_checkouts():
    hoy = date.today()
    reservas = Reservacion.objects.filter(
        estado='EnCurso',
        fecha_salida=hoy
    ).select_related('id_huesped_titular', 'id_habitacion')
    data = []
    for r in reservas:
        data.append({
            'id': r.id,
            'huesped': str(r.id_huesped_titular),
            'habitacion': r.id_habitacion.numero,
            'fecha_salida': str(r.fecha_salida),
        })
    return {'total': len(data), 'reservas': data}
