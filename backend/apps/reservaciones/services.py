from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import Reservacion, ReservacionHuespedes, Consumo, Pago
from apps.habitaciones.models import Habitacion
from apps.habitaciones.services import cambiar_estado as cambiar_estado_habitacion
from apps.huespedes.models import Huesped
from apps.bitacora.services import registrar_actividad

def _calcular_totales(reservacion, calcular_consumos=False):
    reservacion.numero_noches = (reservacion.fecha_salida - reservacion.fecha_entrada).days
    reservacion.total_habitacion = reservacion.numero_noches * reservacion.id_habitacion.precio_por_noche
    if calcular_consumos and reservacion.pk:
        reservacion.monto_total_consumos = reservacion.consumos.aggregate(s=models.Sum('total'))['s'] or Decimal('0.00')
    else:
        reservacion.monto_total_consumos = Decimal('0.00')
    reservacion.monto_total_final = reservacion.total_habitacion + reservacion.monto_total_consumos
    reservacion.saldo_pendiente = reservacion.monto_total_final - reservacion.monto_pagado

def _validar_solapamiento(habitacion_id, fecha_entrada, fecha_salida, excluir_reserva=None):
    qs = Reservacion.objects.filter(
        id_habitacion_id=habitacion_id,
        estado__in=['Confirmada', 'EnCurso'],
        fecha_entrada__lt=fecha_salida,
        fecha_salida__gt=fecha_entrada
    )
    if excluir_reserva:
        qs = qs.exclude(pk=excluir_reserva.pk)
    return not qs.exists()

def _validar_limite_credito(huesped, nuevo_total):
    if not huesped.limite_credito or huesped.limite_credito == 0:
        return
    # Sumar saldos pendientes de crédito
    pendiente = Reservacion.objects.filter(
        id_huesped_titular=huesped,
        modalidad_pago='Crédito',
        estado='Finalizada',
        saldo_pendiente__gt=0
    ).aggregate(total=models.Sum('saldo_pendiente'))['total'] or Decimal('0.00')
    if pendiente + nuevo_total > huesped.limite_credito:
        raise ValidationError('Supera el límite de crédito autorizado.')

@transaction.atomic
def crear_reservacion(
    id_huesped_titular,
    id_habitacion,
    fecha_entrada,
    fecha_salida,
    modalidad_pago,
    requiere_factura=False,
    acompanantes=None,
    metodo_pago_inicial=None,
    numero_referencia_inicial='',
    monto_abonado=Decimal('0.00'),
    usuario=None
):
    # Validar huésped titular
    try:
        titular = Huesped.objects.get(pk=id_huesped_titular)
    except Huesped.DoesNotExist:
        raise ValidationError('Huésped titular no encontrado.')
    from apps.huespedes.services import validar_disponibilidad_huesped
    if not validar_disponibilidad_huesped(titular.id):
        raise ValidationError('El huésped ya posee una estancia activa.')

    # Validar acompañantes (se asume que acompanantes es lista de ids)
    if acompanantes:
        for acomp_id in acompanantes:
            if not validar_disponibilidad_huesped(acomp_id):
                raise ValidationError(f'El acompañante con id {acomp_id} ya posee una estancia activa.')
            if acomp_id == titular.id:
                raise ValidationError('Un acompañante no puede ser el titular.')

    total_personas = 1 + (len(acompanantes) if acompanantes else 0)

    # Validar habitación
    try:
        habitacion = Habitacion.objects.get(pk=id_habitacion)
    except Habitacion.DoesNotExist:
        raise ValidationError('Habitación no encontrada.')
    if habitacion.estado != 'Limpia':
        raise ValidationError('La habitación no está disponible.')
    if habitacion.capacidad_maxima < total_personas:
        raise ValidationError('La habitación no tiene capacidad suficiente.')

    # Validar fechas
    if fecha_entrada >= fecha_salida:
        raise ValidationError('La fecha de salida debe ser posterior a la de entrada.')

    # Validar solapamiento
    if not _validar_solapamiento(habitacion.id, fecha_entrada, fecha_salida):
        raise ValidationError('La habitación ya está reservada en esas fechas.')

    # Validar modalidad de pago
    if modalidad_pago == 'Crédito' and not titular.credito_autorizado:
        raise ValidationError('El huésped no tiene crédito autorizado.')

    # Crear reserva
    reserva = Reservacion(
        id_huesped_titular=titular,
        id_habitacion=habitacion,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        modalidad_pago=modalidad_pago,
        requiere_factura=requiere_factura,
        estado='Confirmada'
    )
    _calcular_totales(reserva, calcular_consumos=False)
    reserva.save()

    # Insertar titular en tabla intermedia
    ReservacionHuespedes.objects.create(
        id_reservacion=reserva,
        id_huesped=titular,
        rol='Titular'
    )
    # Insertar acompañantes
    if acompanantes:
        for acomp_id in acompanantes:
            acomp = Huesped.objects.get(pk=acomp_id)
            ReservacionHuespedes.objects.create(
                id_reservacion=reserva,
                id_huesped=acomp,
                rol='Acompañante'
            )

    # Manejar pago inicial
    if modalidad_pago == 'Contado':
        # Pago total inmediato
        Pago.objects.create(
            id_reservacion=reserva,
            monto=reserva.total_habitacion,
            metodo_pago=metodo_pago_inicial,
            numero_referencia=numero_referencia_inicial,
            id_usuario=usuario
        )
        reserva.monto_pagado = reserva.total_habitacion
        reserva.saldo_pendiente = Decimal('0.00')
        reserva.metodo_pago_inicial = metodo_pago_inicial
        reserva.numero_referencia_inicial = numero_referencia_inicial
    elif modalidad_pago == 'Abono':
        if monto_abonado > 0:
            Pago.objects.create(
                id_reservacion=reserva,
                monto=monto_abonado,
                metodo_pago=metodo_pago_inicial,
                numero_referencia=numero_referencia_inicial,
                id_usuario=usuario
            )
            reserva.monto_pagado = monto_abonado
        else:
            reserva.monto_pagado = Decimal('0.00')
        reserva.saldo_pendiente = reserva.total_habitacion - reserva.monto_pagado
        reserva.metodo_pago_inicial = metodo_pago_inicial
        reserva.numero_referencia_inicial = numero_referencia_inicial
    elif modalidad_pago == 'Crédito':
        _validar_limite_credito(titular, reserva.total_habitacion)
        reserva.monto_pagado = Decimal('0.00')
        reserva.saldo_pendiente = reserva.total_habitacion

    reserva.save()
    registrar_actividad('Creación Reserva', f'Reserva #{reserva.id} creada para {titular}', usuario, f'Reserva-{reserva.id}')
    return reserva


@transaction.atomic
def realizar_checkin(reserva_id, usuario):
    reserva = Reservacion.objects.select_for_update().get(pk=reserva_id)
    if reserva.estado != 'Confirmada':
        raise ValidationError('La reserva no está confirmada.')
    habitacion = reserva.id_habitacion
    if habitacion.estado != 'Limpia':
        raise ValidationError('La habitación ya no está limpia.')

    cambiar_estado_habitacion(habitacion, 'Ocupada')
    reserva.estado = 'EnCurso'
    reserva.fecha_checkin_real = timezone.now()
    reserva.save()
    registrar_actividad('Check‑in', f'Check‑in habitación {habitacion.numero} - {reserva.id_huesped_titular}', usuario, f'Reserva-{reserva.id}')
    return reserva


@transaction.atomic
def realizar_checkout(reserva_id, usuario):
    reserva = Reservacion.objects.select_for_update().get(pk=reserva_id)
    if reserva.estado != 'EnCurso':
        raise ValidationError('La reserva no está en curso.')

    # Verificar saldo si no es crédito
    if reserva.modalidad_pago in ['Contado', 'Abono'] and reserva.saldo_pendiente > 0:
        raise ValidationError('El saldo pendiente debe ser 0 para cerrar la reserva.')

    cambiar_estado_habitacion(reserva.id_habitacion, 'Sucia')
    reserva.estado = 'Finalizada'
    reserva.fecha_checkout_real = timezone.now()
    reserva.save()
    registrar_actividad('Check‑out', f'Check‑out habitación {reserva.id_habitacion.numero} - {reserva.id_huesped_titular}', usuario, f'Reserva-{reserva.id}')
    return reserva


def agregar_consumo(reserva_id, tipo, descripcion, cantidad, precio_unitario, producto=None, usuario=None):
    reserva = Reservacion.objects.get(pk=reserva_id)
    if reserva.estado != 'EnCurso':
        raise ValidationError('Solo se pueden cargar consumos a reservas en curso.')
    with transaction.atomic():
        consumo = Consumo.objects.create(
            id_reservacion=reserva,
            tipo_consumo=tipo,
            descripcion=descripcion,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            producto=producto
        )
        # Actualizar totales
        _calcular_totales(reserva, calcular_consumos=True)
        reserva.save()
        registrar_actividad('Consumo', f'Consumo {tipo} por ${consumo.total} agregado a reserva #{reserva.id}', usuario, f'Consumo-{consumo.id}')
        return consumo


def registrar_pago_extra(reserva_id, monto, metodo_pago, numero_referencia='', usuario=None):
    reserva = Reservacion.objects.get(pk=reserva_id)
    # Permitir pagos en Confirmada (si abono/crédito) y EnCurso (todas)
    if reserva.estado not in ['Confirmada', 'EnCurso']:
        # También permitir en Finalizada si crédito y saldo >0
        if not (reserva.estado == 'Finalizada' and reserva.modalidad_pago == 'Crédito' and reserva.saldo_pendiente > 0):
            raise ValidationError('No se pueden registrar pagos en este estado.')
    with transaction.atomic():
        pago = Pago.objects.create(
            id_reservacion=reserva,
            monto=monto,
            metodo_pago=metodo_pago,
            numero_referencia=numero_referencia,
            id_usuario=usuario
        )
        reserva.monto_pagado += monto
        reserva.saldo_pendiente = reserva.monto_total_final - reserva.monto_pagado
        reserva.save()
        registrar_actividad('Pago', f'Pago de ${monto} ({metodo_pago}) a reserva #{reserva.id}', usuario, f'Pago-{pago.id}')
        return pago


def cancelar_reservacion(reserva_id, motivo, acta='', usuario=None):
    reserva = Reservacion.objects.get(pk=reserva_id)
    if reserva.estado != 'Confirmada':
        raise ValidationError('Solo se pueden cancelar reservas confirmadas.')
    reserva.estado = 'Cancelada'
    reserva.motivo_cancelacion = motivo
    reserva.acta = acta
    reserva.save()
    registrar_actividad('Cancelación', f'Reserva #{reserva.id} cancelada: {motivo}', usuario, f'Reserva-{reserva.id}')
    return reserva


def marcar_noshow(reserva_id, motivo, acta='', usuario=None):
    reserva = Reservacion.objects.get(pk=reserva_id)
    if reserva.estado != 'Confirmada':
        raise ValidationError('Solo se pueden marcar como No‑show reservas confirmadas.')
    if reserva.fecha_entrada > timezone.now().date():
        raise ValidationError('No se puede marcar No‑show antes de la fecha de entrada.')
    reserva.estado = 'NoShow'
    reserva.motivo_cancelacion = motivo
    reserva.acta = acta
    reserva.save()
    registrar_actividad('No‑show', f'Reserva #{reserva.id} no-show: {motivo}', usuario, f'Reserva-{reserva.id}')
    return reserva


def obtener_resumen_para_checkout(reserva):
    return {
        'total_habitacion': str(reserva.total_habitacion),
        'total_consumos': str(reserva.monto_total_consumos),
        'total_final': str(reserva.monto_total_final),
        'monto_pagado': str(reserva.monto_pagado),
        'saldo_pendiente': str(reserva.saldo_pendiente),
    }