from django.db import models
from apps.huespedes.models import Huesped
from apps.habitaciones.models import Habitacion
from apps.usuarios.models import User
from apps.empresas.models import Empresa

class Reservacion(models.Model):
    ESTADO = [
        ('Confirmada', 'Confirmada'),
        ('EnCurso', 'En Curso'),
        ('Finalizada', 'Finalizada'),
        ('Cancelada', 'Cancelada'),
        ('NoShow', 'No Show'),
    ]
    MODALIDAD_PAGO = [
        ('Contado', 'Contado'),
        ('Abono', 'Abono'),
        ('Crédito', 'Crédito'),
    ]
    METODO_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('PagoMovil', 'Pago Móvil'),
    ]

    id_huesped_titular = models.ForeignKey(Huesped, on_delete=models.PROTECT, related_name='reservaciones_titular')
    id_empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservaciones')
    id_habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name='reservaciones')
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    numero_noches = models.PositiveSmallIntegerField(editable=False)
    total_habitacion = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    estado = models.CharField(max_length=15, choices=ESTADO, default='Confirmada')
    modalidad_pago = models.CharField(max_length=10, choices=MODALIDAD_PAGO)
    metodo_pago_inicial = models.CharField(max_length=10, choices=METODO_PAGO, null=True, blank=True)
    numero_referencia_inicial = models.CharField(max_length=50, blank=True)
    requiere_factura = models.BooleanField(default=False)
    acta = models.TextField(blank=True)
    motivo_cancelacion = models.TextField(blank=True)
    monto_total_consumos = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    monto_total_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    fecha_checkin_real = models.DateTimeField(null=True, blank=True)
    fecha_checkout_real = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'reservaciones'
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'

    def __str__(self):
        return f"Reserva {self.id} - {self.id_huesped_titular}"

    def save(self, *args, **kwargs):
        if self.fecha_entrada and self.fecha_salida:
            self.numero_noches = (self.fecha_salida - self.fecha_entrada).days

            precio_a_usar = self.id_habitacion.precio_por_noche
            if self.id_empresa and self.id_habitacion.precio_empresa:
                precio_a_usar = self.id_habitacion.precio_empresa

            self.total_habitacion = self.numero_noches * precio_a_usar

        super().save(*args, **kwargs)


class ReservacionHuespedes(models.Model):
    ROL = [
        ('Titular', 'Titular'),
        ('Acompañante', 'Acompañante'),
    ]
    id_reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='huespedes_secundarios')
    id_huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT)
    rol = models.CharField(max_length=15, choices=ROL)

    class Meta:
        db_table = 'reservacion_huespedes'
        unique_together = ('id_reservacion', 'id_huesped')
        verbose_name = 'Reservación-Huésped'
        verbose_name_plural = 'Reservaciones-Huéspedes'


class Consumo(models.Model):
    TIPO_CONSUMO = [
        ('Restaurante', 'Restaurante'),
        ('Minibar', 'Minibar'),
        ('Lavandería', 'Lavandería'),
        ('Llamadas', 'Llamadas'),
        ('Otro', 'Otro'),
    ]
    id_reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='consumos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    tipo_consumo = models.CharField(max_length=20, choices=TIPO_CONSUMO)
    producto = models.ForeignKey('inventario.Producto', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'consumos'
        verbose_name = 'Consumo'
        verbose_name_plural = 'Consumos'

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class Pago(models.Model):
    METODO_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('PagoMovil', 'Pago Móvil'),
    ]
    id_reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='pagos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=10, choices=METODO_PAGO)
    numero_referencia = models.CharField(max_length=50, blank=True)
    id_usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pagos'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
