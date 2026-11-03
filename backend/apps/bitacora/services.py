from django.db import transaction, models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import ActividadLog, CierreCaja
from apps.reservaciones.models import Pago

def registrar_actividad(tipo, descripcion, usuario, id_referencia=''):
    ActividadLog.objects.create(
        tipo=tipo,
        descripcion=descripcion,
        id_usuario=usuario,
        id_referencia=id_referencia
    )

def listar_actividades(limit=20):
    return ActividadLog.objects.select_related('id_usuario').order_by('-fecha_hora')[:limit]

def realizar_cierre_caja(fecha, usuario):
    """
    Calcula los totales de pagos del día y crea un registro de cierre.
    Bloquea la creación de pagos en esa fecha si el cierre ya existe.
    """
    if CierreCaja.objects.filter(fecha=fecha).exists():
        raise ValidationError('El cierre de caja para esta fecha ya fue realizado.')

    pagos_del_dia = Pago.objects.filter(fecha_hora__date=fecha)

    total_efectivo = pagos_del_dia.filter(metodo_pago='Efectivo').aggregate(t=models.Sum('monto'))['t'] or 0
    total_tarjeta = pagos_del_dia.filter(metodo_pago='Tarjeta').aggregate(t=models.Sum('monto'))['t'] or 0
    total_pago_movil = pagos_del_dia.filter(metodo_pago='PagoMovil').aggregate(t=models.Sum('monto'))['t'] or 0
    total_general = total_efectivo + total_tarjeta + total_pago_movil

    with transaction.atomic():
        cierre = CierreCaja.objects.create(
            fecha=fecha,
            total_efectivo=total_efectivo,
            total_tarjeta=total_tarjeta,
            total_pago_movil=total_pago_movil,
            total_general=total_general,
            id_usuario=usuario
        )
        registrar_actividad('Cierre de caja', f'Cierre de caja del {fecha}', usuario, f'Cierre-{cierre.id}')
    return cierre

def listar_cierres():
    return CierreCaja.objects.select_related('id_usuario').order_by('-fecha')
