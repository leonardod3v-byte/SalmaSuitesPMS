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
        ('Limpia', 'Limpia'),
        ('Ocupada', 'Ocupada'),
        ('Sucia', 'Sucia'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Obra', 'Obra'),
    ]

    numero = models.CharField(max_length=10, unique=True)
    piso = models.PositiveSmallIntegerField()
    cantidad_camas = models.PositiveSmallIntegerField()
    capacidad_maxima = models.PositiveSmallIntegerField()
    categoria_tipo = models.CharField(max_length=25, choices=CATEGORIA_TIPO)
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO, default='Limpia')
    notas = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    class Meta:
        db_table = 'habitaciones'
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return f"Habitación {self.numero} - {self.categoria_tipo}"