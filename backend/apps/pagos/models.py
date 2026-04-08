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
        ('efectivo_usd', 'Efectivo USD'),
        ('efectivo_ves', 'Efectivo Bs.'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('pago_movil', 'Pago Móvil'),
        ('zelle', 'Zelle'),
        ('binance', 'Binance Pay'),
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
    RF07: Cierre de caja diario por recepcionista.
    Consolida todos los ingresos del día desglosados por método de pago.
    Genera un PDF firmado como respaldo.
    """
    recepcionista = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cierres_caja'
    )
    fecha = models.DateField()

    # Desglose por método de pago
    efectivo_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    efectivo_ves = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transferencias = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tarjetas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pago_movil = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    zelle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    binance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)

    # RF07: Control del PDF generado
    pdf_generado = models.BooleanField(default=False)
    pdf_url = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cierres_caja'
        # Un recepcionista solo puede hacer un cierre por día
        unique_together = ['recepcionista', 'fecha']
        ordering = ['-fecha']
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f'Cierre {self.fecha} - {self.recepcionista.username} (${self.total_caja})'

    def calcular_total(self):
        """Suma todos los métodos de pago y actualiza el total."""
        self.total_caja = (
            self.efectivo_usd + self.efectivo_ves +
            self.transferencias + self.tarjetas +
            self.pago_movil + self.zelle + self.binance
        )
        return self.total_caja