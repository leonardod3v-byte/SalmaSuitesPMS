from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta

from .models import Notificacion
from .serializers import NotificacionSerializer
from .services import (
    notificar_confirmacion_reserva,
    notificar_recordatorio_pago,
    notificar_checkout_pendiente,
    notificar_bienvenida,
    enviar_whatsapp
)
from utils import paginar_queryset_funcion


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def notificaciones_list(request):
    """
    Lista el historial de notificaciones con filtros específicos y paginación senior.
    """
    qs = Notificacion.objects.all().order_by('-fecha_envio')

    estado = request.query_params.get('estado')
    tipo = request.query_params.get('tipo')
    reserva_id = request.query_params.get('reserva')

    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if reserva_id:
        qs = qs.filter(reserva_id=reserva_id)

    # BLINDADO: Paginación para conjuntos de datos masivos (Páginas de 30 registros)
    return paginar_queryset_funcion(request, qs, NotificacionSerializer, page_size=30)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reintentar_notificacion(request, pk):
    """
    Reintenta el envío de una notificación fallida.
    """
    try:
        notificacion = Notificacion.objects.get(pk=pk)
    except Notificacion.DoesNotExist:
        return Response({'error': 'Notificación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if notificacion.estado == 'exitosa':
        return Response({'message': 'Esta notificación ya fue enviada correctamente.'}, status=status.HTTP_400_BAD_REQUEST)

    # Ejecución del reintento según el canal original
    exito = False
    if notificacion.canal == 'whatsapp':
        exito = enviar_whatsapp(notificacion.destinatario, notificacion.mensaje)
    # Aquí puedes expandir para canal 'email' si fuera necesario en el futuro

    if exito:
        notificacion.estado = 'exitosa'
        notificacion.fecha_envio = timezone.now()
        notificacion.error_mensaje = None
        notificacion.save(update_fields=['estado', 'fecha_envio', 'error_mensaje'])
        return Response({'message': 'Notificación reintentada con éxito.'}, status=status.HTTP_200_OK)
    else:
        notificacion.intentos += 1
        notificacion.save(update_fields=['intentos'])
        return Response({'error': 'El reintento volvió a fallar.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def enviar_notificacion_reserva(request, reserva_id):
    """
    RF15: Despacha la notificación por correo electrónico correspondiente a una reserva.
    Construye plantillas dinámicas y blinda el flujo contra fallos en el servicio SMTP.
    """
    try:
        # Pre-cargamos el huésped y la habitación para armar el cuerpo del mensaje de un solo golpe
        reserva = Reserva.objects.select_related('huesped', 'habitacion').get(pk=reserva_id)
    except Reserva.DoesNotExist:
        return Response({'error': 'La reserva especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)

    huesped = reserva.huesped
    if not huesped.email:
        return Response(
            {'error': f'El huésped {huesped.nombre} no tiene una dirección de correo registrada.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Identificamos el tipo de notificación según el estado actual de la reserva
    # o mediante un parámetro opcional enviado en el body (ej: 'bienvenida', 'recordatorio')
    tipo_accion = request.data.get('tipo_plantilla', reserva.estado)
    
    # Configuración de asuntos y cuerpos de mensajes preestablecidos
    asunto = f"Confirmación de Estadía - Salma Suites"
    mensaje_txt = f"Estimado(a) {huesped.nombre},\n\n"

    if tipo_accion == 'confirmada' or tipo_accion == 'sin_pagar':
        asunto = f"Confirmación de Reserva #{reserva.id} - Salma Suites VIP"
        mensaje_txt += (
            f"Su reserva ha sido registrada con éxito.\n"
            f"Detalles:\n"
            f"- Habitación: H-{reserva.habitacion.numero if reserva.habitacion else 'Por asignar'}\n"
            f"- Fecha de Entrada: {reserva.fecha_entrada.strftime('%d/%m/%Y')}\n"
            f"- Fecha de Salida: {reserva.fecha_salida.strftime('%d/%m/%Y')}\n\n"
            f"Gracias por elegirnos."
        )
    elif tipo_accion == 'check_in':
        asunto = f"¡Bienvenido a Salma Suites! - Habitación H-{reserva.habitacion.numero if reserva.habitacion else 'N/A'}"
        mensaje_txt += "Su Check-in se ha procesado correctamente. Esperamos que disfrute de su estancia con nosotros."
    else:
        # Fallback genérico por si es una alerta manual
        mensaje_txt += f"Le escribimos para informarle sobre el estatus de su reserva #{reserva.id} (Estado: {reserva.estado})."

    # Envío asíncrono simulado/bloque protegido para evitar interrupciones en la app
    try:
        # Nota: Asegúrate de tener configurado tu EMAIL_HOST_USER en el settings.py
        email_remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@salmasuites.com')
        
        send_mail(
            subject=asunto,
            message=mensaje_txt,
            from_email=email_remitente,
            recipient_list=[huesped.email],
            fail_silently=False, # Ponlo en True si no quieres que levante excepciones de red SMTP
        )
        
        # Si tienes el helper de auditoría global disponible en esta app, puedes registrar la acción:
        # registrar_actividad('notificacion_enviada', f"Correo enviado a {huesped.email} por Reserva #{reserva.id}", request.user)
        
        return Response({
            'message': f'Notificación enviada con éxito absoluto a {huesped.email}.',
            'reserva_id': reserva.id,
            'plantilla_utilizada': tipo_accion
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # Si falla el SMTP (sin internet, credenciales caídas), el backend responde con un log controlado sin romperse
        return Response({
            'error': 'La notificación no pudo ser entregada a través del servidor de correo.',
            'details': str(e)
        }, status=status.HTTP_502_BAD_GATEWAY)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def enviar_notificacion_personalizada(request):
    """
    RF15: Endpoint de mensajería libre. 
    Permite al staff redactar y despachar correos electrónicos personalizados 
    a cualquier destinatario de forma segura y directa desde el PMS.
    """
    destinatario = request.data.get('email')
    asunto = request.data.get('asunto')
    cuerpo_mensaje = request.data.get('mensaje')

    # Validación de campos obligatorios para evitar payloads corruptos
    if not all([destinatario, asunto, cuerpo_mensaje]):
        return Response(
            {'error': 'Los parámetros "email", "asunto" y "mensaje" son estrictamente obligatorios.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Bloque de aislamiento SMTP para proteger la concurrencia del servidor
    try:
        email_remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@salmasuites.com')
        
        send_mail(
            subject=asunto,
            message=cuerpo_mensaje,
            from_email=email_remitente,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        
        # Opcional: Registramos la auditoría de quién envió el correo manual
        # registrar_actividad('notificacion_manual', f"Correo personalizado enviado a {destinatario}: {asunto[:30]}...", request.user)

        return Response({
            'message': f'Mensaje personalizado despachado exitosamente hacia {destinatario}.',
            'asunto': asunto
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # Prevención de caídas: si el servidor SMTP de Supabase/Mailgun/Gmail falla, controlamos el log
        return Response({
            'error': 'El servidor de correo no pudo procesar la entrega en este milisegundo.',
            'details': str(e)
        }, status=status.HTTP_502_BAD_GATEWAY)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def procesar_recordatorios_automaticos(request):
    """
    RF15/Automatización: Escanea la base de datos en busca de reservas confirmadas 
    que inicien mañana para despachar de forma masiva los recordatorios de Check-in.
    """
    hoy_ahora = timezone.now()
    manana_inicio = (hoy_ahora + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    manana_fin = manana_inicio.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Consulta Senior: Traemos reservas de mañana con su huésped cargado en un solo JOIN
    reservas_manana = Reserva.objects.select_related('huesped', 'habitacion').filter(
        estado='confirmada',
        fecha_entrada__range=(manana_inicio, manana_fin)
    )

    enviados_con_exito = 0
    fallidos = 0
    detalles_envio = []

    email_remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@salmasuites.com')

    for reserva in reservas_manana:
        huesped = reserva.huesped
        if not huesped.email:
            fallidos += 1
            continue

        asunto = f"Recordatorio de Check-in: ¡Su estadía en Salma Suites comienza mañana!"
        cuerpo = (
            f"Estimado(a) {huesped.nombre},\n\n"
            f"Le recordamos que su reserva #{reserva.id} está programada para ingresar mañana.\n"
            f"Detalles de su llegada:\n"
            f"- Habitación: H-{reserva.habitacion.numero if reserva.habitacion else 'Por asignar'}\n"
            f"- Fecha de Entrada: {reserva.fecha_entrada.strftime('%d/%m/%Y')}\n\n"
            f"El equipo de Salma Suites le desea un feliz viaje. Nos vemos pronto."
        )

        # Aislamiento por cada iteración para que un correo roto no tumbe todo el lote
        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=email_remitente,
                recipient_list=[huesped.email],
                fail_silently=False,
            )
            enviados_con_exito += 1
            detalles_envio.append({'reserva_id': reserva.id, 'status': 'enviado', 'email': huesped.email})
        except Exception as e:
            fallidos += 1
            detalles_envio.append({'reserva_id': reserva.id, 'status': 'error', 'detalle': str(e)})

    return Response({
        'fecha_procesada': manana_inicio.date().isoformat(),
        'total_reservas_detectadas': reservas_manana.count(),
        'enviados_exitosamente': enviados_con_exito,
        'fallidos': fallidos,
        'log_ejecucion': detalles_envio
    }, status=status.HTTP_200_OK)