from django.db import models

class Huesped(models.Model):
    TIPO_DOCUMENTO = [
        ('V', 'V'),
        ('E', 'E'),
        ('J', 'J'),
        ('P', 'P'),
    ]
    CATEGORIA = [
        ('VIP', 'VIP'),
        ('Estándar', 'Estándar'),
    ]
    TIPO_CLIENTE_PROFESION = [
        ('Particular', 'Particular'),
        ('Militar', 'Militar'),
        ('Político', 'Político'),
        ('Artista', 'Artista'),
        ('Empresario', 'Empresario'),
        ('Deportista', 'Deportista'),
        ('Diplomático', 'Diplomático'),
        ('Médico', 'Médico'),
        ('Religioso', 'Religioso'),
        ('Turista', 'Turista'),
        ('Ejecutivo de Ventas', 'Ejecutivo de Ventas'),
        ('Comerciante', 'Comerciante'),
    ]
    ESTADO_CIVIL = [
        ('Soltero', 'Soltero'),
        ('Casado', 'Casado'),
        ('Divorciado', 'Divorciado'),
        ('Viudo', 'Viudo'),
        ('Concubino', 'Concubino'),
    ]

    tipo_documento = models.CharField(max_length=1, choices=TIPO_DOCUMENTO)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    edad = models.PositiveSmallIntegerField(editable=False)  # se calculará en el save
    nacionalidad = models.CharField(max_length=50)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    procedencia = models.CharField(max_length=100)
    tipo_cliente_profesion = models.CharField(max_length=30, choices=TIPO_CLIENTE_PROFESION)
    categoria = models.CharField(max_length=10, choices=CATEGORIA, default='Estándar')
    credito_autorizado = models.BooleanField(default=False)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'huespedes'
        verbose_name = 'Huésped'
        verbose_name_plural = 'Huéspedes'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def save(self, *args, **kwargs):
        # Calcular edad automáticamente a partir de la fecha de nacimiento
        from datetime import date
        hoy = date.today()
        self.edad = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        super().save(*args, **kwargs)