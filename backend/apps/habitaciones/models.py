from django.db import models

class Habitacion(models.Model):
    CATEGORIA_TIPO = [
        ('Uni-Familiar', 'Uni-Familiar'),
        ('Doble Individual', 'Doble Individual'),
        ('Doble Matrimonial', 'Doble Matrimonial'),
        ('Matrimonial', 'Matrimonial'),
        ('Triple Individual', 'Triple Individual'),
        ('Suite', 'Suite'),
        ('Queen', 'Queen'),
    ]
    ESTADO = [
        ('Disponible', 'Disponible'),
        ('Ocupada', 'Ocupada'),
        ('Limpieza', 'Limpieza'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Obra', 'Obra'),
    ]

    numero = models.CharField(max_length=10, unique=True)
    piso = models.PositiveSmallIntegerField()
    cantidad_camas = models.PositiveSmallIntegerField()
    capacidad_maxima = models.PositiveSmallIntegerField()
    categoria_tipo = models.CharField(max_length=25, choices=CATEGORIA_TIPO)
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    precio_empresa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Si se deja vacío, se usará el precio normal")

    estado = models.CharField(max_length=15, choices=ESTADO, default='Disponible')
    notas = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    class Meta:
        db_table = 'habitaciones'
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return f"Habitación {self.numero} - {self.categoria_tipo}"
