from django.db import models
from apps.usuarios.models import User

class ActividadLog(models.Model):
    TIPO = [
        ('Creación Reserva', 'Creación Reserva'),
        ('Check‑in', 'Check‑in'),
        ('Check‑out', 'Check‑out'),
        ('Pago', 'Pago'),
        ('Consumo', 'Consumo'),
        ('Cambio estado habitación', 'Cambio estado habitación'),
        ('Cancelación', 'Cancelación'),
        ('No‑show', 'No‑show'),
        ('Actualización de huésped', 'Actualización de huésped'),
        ('Otra', 'Otra'),
    ]

    fecha_hora = models.DateTimeField(auto_now_add=True)
    id_usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=30, choices=TIPO)
    descripcion = models.TextField()
    id_referencia = models.CharField(max_length=100, blank=True)  # ej: "Reserva-15"

    class Meta:
        db_table = 'actividad_log'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'


class CierreCaja(models.Model):
    fecha = models.DateField(unique=True)
    total_efectivo = models.DecimalField(max_digits=10, decimal_places=2)
    total_tarjeta = models.DecimalField(max_digits=10, decimal_places=2)
    total_pago_movil = models.DecimalField(max_digits=10, decimal_places=2)
    total_general = models.DecimalField(max_digits=10, decimal_places=2)
    id_usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_hora_cierre = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cierres_caja'
        verbose_name = 'Cierre de caja'
        verbose_name_plural = 'Cierres de caja'