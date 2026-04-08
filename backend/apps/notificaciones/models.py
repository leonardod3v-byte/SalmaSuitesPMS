from django.db import models
from apps.users.models import User


class Notificacion(models.Model):
    """
    Registra cada notificación enviada o pendiente del sistema (RF11).
    Así puedes ver el historial completo y detectar fallos.
    """
    TIPOS = [
        ('confirmacion_reserva', 'Confirmación de Reserva'),
        ('recordatorio_pago', 'Recordatorio de Pago'),
        ('checkout_pendiente', 'Check-out Pendiente'),
        ('bienvenida', 'Bienvenida al Hotel'),
        ('no_show', 'Acta No-Show'),
        ('cierre_caja', 'Cierre de Caja'),
        ('stock_bajo', 'Stock Bajo'),
    ]

    CANALES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('sistema', 'Sistema'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('fallida', 'Fallida'),
        ('leida', 'Leída'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPOS)
    canal = models.CharField(max_length=20, choices=CANALES, default='whatsapp')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    # Destinatario
    destinatario_nombre = models.CharField(max_length=150)
    destinatario_telefono = models.CharField(max_length=20, blank=True)
    destinatario_email = models.EmailField(blank=True)

    # Contenido
    mensaje = models.TextField()
    respuesta_api = models.TextField(
        blank=True,
        help_text='Respuesta de Twilio o del servicio de email'
    )
    error_detalle = models.TextField(blank=True)

    # Referencias opcionales
    reserva_id = models.IntegerField(null=True, blank=True)
    enviada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    enviada_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notificaciones'
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f'{self.tipo} → {self.destinatario_nombre} ({self.estado})'