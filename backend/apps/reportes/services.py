from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Q
from apps.reservaciones.models import Pago
from apps.bitacora.models import CierreCaja

def obtener_detalle_diario(fecha: date):
    pagos = Pago.objects.filter(fecha_hora__date=fecha).select_related(
        'id_reservacion__id_huesped_titular'
    ).order_by('fecha_hora')

    detalle = []
    for pago in pagos:
        detalle.append({
            'hora': pago.fecha_hora.time(),
            'reserva_id': pago.id_reservacion_id,
            'huesped': str(pago.id_reservacion.id_huesped_titular),
            'metodo_pago': pago.metodo_pago,
            'numero_referencia': pago.numero_referencia or '',
            'monto': pago.monto,
        })

    total_efectivo = pagos.filter(metodo_pago='Efectivo').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_tarjeta = pagos.filter(metodo_pago='Tarjeta').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_pago_movil = pagos.filter(metodo_pago='PagoMovil').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_general = total_efectivo + total_tarjeta + total_pago_movil

    cerrado = CierreCaja.objects.filter(fecha=fecha).exists()

    return {
        'total_general': total_general,
        'total_efectivo': total_efectivo,
        'total_tarjeta': total_tarjeta,
        'total_pago_movil': total_pago_movil,
        'cantidad_transacciones': len(detalle),
        'cerrado': cerrado,
        'detalle': detalle,
    }


def obtener_ingresos_por_periodo(inicio: date, fin: date, metodo=None):
    """
    Retorna lista de { fecha, total, efectivo, tarjeta, pago_movil } agrupado por día.
    """
    qs = Pago.objects.filter(fecha_hora__date__gte=inicio, fecha_hora__date__lte=fin)
    if metodo:
        qs = qs.filter(metodo_pago=metodo)

    # Agrupar por día
    resultados = []
    # Para asegurar todos los días del rango, iteramos día a día
    dias = (fin - inicio).days
    for i in range(dias + 1):
        dia = inicio + timedelta(days=i)
        pagos_dia = qs.filter(fecha_hora__date=dia)
        total_efectivo = pagos_dia.filter(metodo_pago='Efectivo').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
        total_tarjeta = pagos_dia.filter(metodo_pago='Tarjeta').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
        total_pago_movil = pagos_dia.filter(metodo_pago='PagoMovil').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
        total = total_efectivo + total_tarjeta + total_pago_movil

        # Solo incluir si hay pagos o si se quiere mostrar todos los días (se puede decidir en frontend)
        resultados.append({
            'fecha': dia,
            'total': total,
            'efectivo': total_efectivo,
            'tarjeta': total_tarjeta,
            'pago_movil': total_pago_movil,
        })
    return resultados