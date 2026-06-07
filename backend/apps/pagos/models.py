from django.db import models
from apps.users.models import User
from apps.reservaciones.models import Reserva


class Pago(models.Model):
    """
    Registra cada pago realizado por una reserva (RF05).
    Una reserva puede tener múltiples pagos parciales.
    Ej: abono inicial + pago restante al llegar.
    """
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('pago_movil', 'Pago Móvil'),
    ]

    CONCEPTOS = [
        ('estadia', 'Estadía'),
        ('consumo', 'Consumo'),
        ('deposito', 'Depósito'),
        ('abono', 'Abono'),
        ('multa', 'Multa'),
        ('otro', 'Otro'),
    ]

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.PROTECT,
        related_name='pagos'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODOS_PAGO)
    concepto = models.CharField(max_length=20, choices=CONCEPTOS, default='estadia')
    referencia = models.CharField(max_length=100, blank=True)
    nota = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pagos'
        ordering = ['-fecha']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'Pago ${self.monto} ({self.metodo}) - Reserva #{self.reserva.id}'


class CierreCaja(models.Model):
    """
    Cierre de caja diario por recepcionista.
    Consolida los ingresos del día por método de pago.
    No incluye desglose por moneda (solo totales).
    """
    recepcionista = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cierres_caja'
    )
    fecha = models.DateField(auto_now_add=False)  # se asigna manualmente

    # Totales por método de pago (solo los que usas)
    total_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pago_movil = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Totales generales
    total_general = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observaciones = models.TextField(blank=True)

    # PDF generado
    pdf_generado = models.BooleanField(default=False)
    pdf_url = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cierres_caja'
        unique_together = ['recepcionista', 'fecha']  # un cierre por día y usuario
        ordering = ['-fecha']
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f'Cierre {self.fecha} - {self.recepcionista.username} (${self.total_general})'

    def calcular_total(self):
        """Calcula el total general sumando los métodos de pago."""
        self.total_general = (
            self.total_efectivo + self.total_tarjeta + self.total_pago_movil
        )
        return self.total_general

    def save(self, *args, **kwargs):
        """Antes de guardar, calcular total automáticamente."""
        self.calcular_total()
        super().save(*args, **kwargs)