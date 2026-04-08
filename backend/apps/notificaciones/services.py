import os
from django.utils import timezone
from .models import Notificacion


def enviar_whatsapp(telefono, mensaje, tipo, destinatario_nombre,
                    reserva_id=None, usuario=None):
    """
    Función central para enviar mensajes de WhatsApp via Twilio.
    Registra el intento y el resultado en la base de datos.
    Siempre crea el registro aunque falle el envío.
    """
    # Crear registro en BD primero
    notif = Notificacion.objects.create(
        tipo=tipo,
        canal='whatsapp',
        estado='pendiente',
        destinatario_nombre=destinatario_nombre,
        destinatario_telefono=telefono,
        mensaje=mensaje,
        reserva_id=reserva_id,
        enviada_por=usuario
    )

    # Verificar que Twilio esté configurado
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

    if not account_sid or not auth_token:
        notif.estado = 'fallida'
        notif.error_detalle = 'Twilio no está configurado en las variables de entorno.'
        notif.save()
        return {'success': False, 'error': 'Twilio no configurado'}

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        # Asegurarse de que el número tenga el prefijo de WhatsApp
        to_number = telefono if telefono.startswith('whatsapp:') else f'whatsapp:{telefono}'

        message = client.messages.create(
            body=mensaje,
            from_=from_number,
            to=to_number
        )

        notif.estado = 'enviada'
        notif.respuesta_api = message.sid
        notif.enviada_at = timezone.now()
        notif.save()

        return {'success': True, 'sid': message.sid}

    except Exception as e:
        notif.estado = 'fallida'
        notif.error_detalle = str(e)
        notif.save()
        return {'success': False, 'error': str(e)}


# ── Plantillas de mensajes ─────────────────────────────────────────────────────

def notificar_confirmacion_reserva(reserva, usuario=None):
    """
    RF11: Envía confirmación de reserva al huésped.
    Se llama automáticamente al crear una reserva.
    """
    if not reserva.huesped.telefono:
        return {'success': False, 'error': 'El huésped no tiene teléfono registrado'}

    mensaje = (
        f'✅ *Reserva Confirmada - Salma Suite VIP*\n\n'
        f'Hola {reserva.huesped.nombre}, tu reserva ha sido confirmada.\n\n'
        f'📋 *Detalles:*\n'
        f'• Habitación: H-{reserva.habitacion.numero} ({reserva.habitacion.tipo.nombre})\n'
        f'• Check-in: {reserva.fecha_entrada.strftime("%d/%m/%Y")}\n'
        f'• Check-out: {reserva.fecha_salida.strftime("%d/%m/%Y")}\n'
        f'• Noches: {reserva.noches}\n'
        f'• Total: ${reserva.monto_total:.2f}\n\n'
        f'Para más información contáctenos. ¡Bienvenido!'
    )

    return enviar_whatsapp(
        telefono=reserva.huesped.telefono,
        mensaje=mensaje,
        tipo='confirmacion_reserva',
        destinatario_nombre=reserva.huesped.nombre_completo,
        reserva_id=reserva.id,
        usuario=usuario
    )


def notificar_recordatorio_pago(reserva, usuario=None):
    """
    RF11: Recordatorio de pago pendiente 24h antes del check-in.
    """
    if not reserva.huesped.telefono:
        return {'success': False, 'error': 'El huésped no tiene teléfono registrado'}

    mensaje = (
        f'⏰ *Recordatorio de Pago - Salma Suite VIP*\n\n'
        f'Hola {reserva.huesped.nombre}, tu check-in es mañana '
        f'{reserva.fecha_entrada.strftime("%d/%m/%Y")}.\n\n'
        f'💰 *Saldo pendiente: ${reserva.saldo_pendiente:.2f}*\n\n'
        f'• Habitación: H-{reserva.habitacion.numero}\n'
        f'• Total reserva: ${reserva.monto_total:.2f}\n'
        f'• Ya pagado: ${reserva.monto_pagado:.2f}\n\n'
        f'Por favor realiza tu pago antes del check-in.\n'
        f'¡Te esperamos!'
    )

    return enviar_whatsapp(
        telefono=reserva.huesped.telefono,
        mensaje=mensaje,
        tipo='recordatorio_pago',
        destinatario_nombre=reserva.huesped.nombre_completo,
        reserva_id=reserva.id,
        usuario=usuario
    )


def notificar_checkout_pendiente(reserva, usuario=None):
    """
    RF11: Notificación de check-out pendiente para el día de salida.
    """
    if not reserva.huesped.telefono:
        return {'success': False, 'error': 'El huésped no tiene teléfono registrado'}

    mensaje = (
        f'🏨 *Check-out Hoy - Salma Suite VIP*\n\n'
        f'Hola {reserva.huesped.nombre}, hoy es tu día de salida.\n\n'
        f'📋 *Resumen:*\n'
        f'• Habitación: H-{reserva.habitacion.numero}\n'
        f'• Check-out: {reserva.fecha_salida.strftime("%d/%m/%Y")}\n'
        f'• Total pagado: ${reserva.monto_pagado:.2f}\n'
        f'• Saldo pendiente: ${reserva.saldo_pendiente:.2f}\n\n'
        f'Por favor acércate a recepción para el check-out.\n'
        f'¡Fue un placer hospedarte!'
    )

    return enviar_whatsapp(
        telefono=reserva.huesped.telefono,
        mensaje=mensaje,
        tipo='checkout_pendiente',
        destinatario_nombre=reserva.huesped.nombre_completo,
        reserva_id=reserva.id,
        usuario=usuario
    )


def notificar_bienvenida(reserva, usuario=None):
    """
    RF11: Mensaje de bienvenida al hacer check-in.
    """
    if not reserva.huesped.telefono:
        return {'success': False, 'error': 'El huésped no tiene teléfono registrado'}

    mensaje = (
        f'🌟 *Bienvenido a Salma Suite VIP*\n\n'
        f'Hola {reserva.huesped.nombre}, ¡bienvenido!\n\n'
        f'🔑 *Tu habitación:* H-{reserva.habitacion.numero}\n'
        f'📅 *Check-out:* {reserva.fecha_salida.strftime("%d/%m/%Y")}\n\n'
        f'Para cualquier solicitud o servicio, '
        f'no dudes en contactar a recepción.\n\n'
        f'¡Disfruta tu estadía!'
    )

    return enviar_whatsapp(
        telefono=reserva.huesped.telefono,
        mensaje=mensaje,
        tipo='bienvenida',
        destinatario_nombre=reserva.huesped.nombre_completo,
        reserva_id=reserva.id,
        usuario=usuario
    )