from django.db import models
from apps.users.models import User


class TipoHabitacion(models.Model):
    """
    Define los tipos de habitación que maneja el hotel.
    Separado de Habitacion para poder reutilizarlo y editarlo sin tocar cada habitación.
    """
    TIPOS = [
        ('uni_familiar', 'Uni-Familiar'),
        ('doble_individual', 'Doble Individual'),
        ('matrimonial', 'Matrimonial'),
        ('doble_matrimonial', 'Doble Matrimonial'),
        ('triple_individual', 'Triple Individual'),
        ('suite', 'Suite'),
        ('queen', 'Queen'),
    ]

    codigo = models.CharField(max_length=30, choices=TIPOS, unique=True)
    nombre = models.CharField(max_length=100)
    capacidad_maxima = models.PositiveIntegerField()
    precio_base_noche = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = 'tipos_habitacion'
        verbose_name = 'Tipo de Habitación'
        verbose_name_plural = 'Tipos de Habitación'

    def __str__(self):
        return self.nombre


class Habitacion(models.Model):
    """
    Representa cada habitación física del hotel.
    Tiene estados dinámicos según RF03.
    """
    ESTADOS = [
        ('libre', 'Libre'),
        ('limpia', 'Limpia'),
        ('sucia', 'Sucia'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'Mantenimiento'),
        ('construccion', 'En Construcción'),
    ]

    numero = models.CharField(max_length=10, unique=True)
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name='habitaciones')
    piso = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='limpia')
    tiene_minibar = models.BooleanField(default=False)
    qr_code = models.CharField(max_length=50, unique=True, blank=True)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habitaciones'
        ordering = ['piso', 'numero']
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return f'H-{self.numero} ({self.tipo.nombre})'

    def save(self, *args, **kwargs):
        # Genera el código QR automáticamente al crear la habitación (RF12)
        if not self.qr_code:
            import uuid
            self.qr_code = str(uuid.uuid4())[:12].upper()
        super().save(*args, **kwargs)


class HistorialEstadoHabitacion(models.Model):
    """
    Registra cada cambio de estado de una habitación (RF03 - historial de cambios).
    Así puedes auditar quién cambió qué y cuándo.
    """
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    cambiado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    nota = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_habitaciones'
        ordering = ['-created_at']
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'

    def __str__(self):
        return f'{self.habitacion} | {self.estado_anterior} → {self.estado_nuevo}'