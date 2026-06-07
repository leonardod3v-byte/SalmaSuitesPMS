from django.db import models
from apps.users.models import User
from apps.guests.models import Huesped
from apps.habitaciones.models import Habitacion


class Reserva(models.Model):
    """
    Modelo principal de reservas (RF05).
    Maneja el ciclo completo: desde la creación hasta check-out o no-show.
    """
    TIPOS_CLIENTE = [
        ('particular',  'Particular'),
        ('militar',     'Militar / GN'),
        ('politico',    'Político / Gov.'),
        ('artista',     'Artista / Medios'),
        ('empresarial', 'Empresarial'),
        ('deportista',  'Deportista'),
        ('diplomatico', 'Diplomático'),
        ('medico',      'Médico'),
        ('religioso',   'Religioso'),
        ('turista',     'Turista / Agencia'),
        ('ejecutivo_ventas', 'Ejecutivo de Ventas'),
        ('comerciante', 'Comerciante'),
    ]


    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('sin_pagar', 'Sin Pagar'),
        ('confirmada', 'Confirmada'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
        ('no_show', 'No-Show'),
    ]

    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('pago_movil', 'Pago Móvil'),
    ]

    # Relaciones principales
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,
        related_name='reservas'
    )
    huesped = models.ForeignKey(
        Huesped,
        on_delete=models.PROTECT,
        related_name='reservas'
    )
    creada_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reservas_creadas'
    )

    # Fechas y horas (RF05)
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    hora_check_in = models.TimeField(null=True, blank=True)
    hora_check_out = models.TimeField(null=True, blank=True)

    # Estado y pago (RF05)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, blank=True)
    referencia_pago = models.CharField(max_length=100, blank=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    modalidad_pago = models.CharField(
    max_length=20,
    choices=[('contado','Contado'),('abono','Abono'),('credito','Crédito')],
    default='contado'
    )
    requiere_factura = models.BooleanField(default=False)
    datos_fiscales = models.JSONField(default=dict, blank=True)

    # RF05: Factura Seniat
    requiere_factura_seniat = models.BooleanField(default=False)
    # Guarda RIF, razón social y dirección fiscal si aplica
    datos_factura = models.JSONField(default=dict, blank=True)

    # RF05: Si se cambia de habitación, guardar cuál era la original
    habitacion_original = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_originales'
    )

    # RF08: Datos del acta No-Show
    no_show_motivo = models.TextField(blank=True)
    no_show_fecha = models.DateTimeField(null=True, blank=True)
    no_show_registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actas_no_show'
    )

    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tipo_cliente = models.CharField(
    max_length=20, choices=TIPOS_CLIENTE, default='particular'
    )

    class Meta:
        db_table = 'reservas'
        ordering = ['-created_at']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'Reserva #{self.id} - {self.huesped} (H-{self.habitacion.numero})'

    @property
    def saldo_pendiente(self):
        """Cuánto falta por pagar."""
        return self.monto_total - self.monto_pagado

    @property
    def noches(self):
        """Cantidad de noches de la reserva."""
        return (self.fecha_salida - self.fecha_entrada).days


class Consumo(models.Model):
    """
    Registra cada producto o servicio consumido por el huésped (RF06).
    Vinculado a la reserva activa.
    Ej: minibar, lavandería, room service, etc.
    """
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='consumos'
    )
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    # A qué noches aplica este consumo (RF06)
    noches_asociadas = models.PositiveIntegerField(
        default=1,
        help_text='Número de noches a las que aplica este consumo'
    )

    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    nota = models.TextField(blank=True)
    fecha_consumo = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consumos'
        ordering = ['-fecha_consumo']
        verbose_name = 'Consumo'
        verbose_name_plural = 'Consumos'

    def __str__(self):
        return f'{self.producto} x{self.cantidad} - Reserva #{self.reserva.id}'

    @property
    def total(self):
        return self.cantidad * self.precio_unitario


class Actividad(models.Model):
    """
    Timeline de acciones del sistema (RF02).
    Cada vez que ocurre algo importante se registra aquí
    para mostrarlo en el dashboard.
    """
    TIPOS = [
        ('check_in', 'Check-in'),
        ('check_out', 'Check-out'),
        ('reserva_creada', 'Reserva Creada'),
        ('reserva_modificada', 'Reserva Modificada'),
        ('reserva_cancelada', 'Reserva Cancelada'),
        ('no_show', 'No-Show Registrado'),
        ('consumo', 'Consumo Registrado'),
        ('pago', 'Pago Registrado'),
        ('cambio_habitacion', 'Cambio de Habitación'),
        ('cambio_estado', 'Cambio de Estado'),
        ('cierre_caja', 'Cierre de Caja'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPOS)
    descripcion = models.CharField(max_length=200)
    detalle = models.TextField(blank=True)

    # Relaciones opcionales, cualquiera puede ser null
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    huesped = models.ForeignKey(
        Huesped,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'actividades'
        ordering = ['-created_at']
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'{self.tipo} - {self.descripcion}'