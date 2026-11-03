from django.db import models
from apps.configuracion.models import Ocupacion

class Huesped(models.Model):
    TIPO_DOCUMENTO = [('V', 'V'), ('E', 'E'), ('J', 'J'), ('P', 'P')]
    CATEGORIA = [('VIP', 'VIP'), ('Estándar', 'Estándar')]
    ESTADO_CIVIL = [('Soltero', 'Soltero'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Viudo', 'Viudo'), ('Concubino', 'Concubino')]

    tipo_documento = models.CharField(max_length=1, choices=TIPO_DOCUMENTO)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    edad = models.PositiveSmallIntegerField(editable=False)
    nacionalidad = models.CharField(max_length=50)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    direccion = models.TextField(blank=True, help_text="Dirección de habitación")
    ocupacion = models.ForeignKey('configuracion.Ocupacion', on_delete=models.SET_NULL, null=True, blank=True)
    alergias = models.TextField(blank=True, help_text="Alergias conocidas")

    categoria = models.CharField(max_length=10, choices=CATEGORIA, default='Estándar')
    credito_autorizado = models.BooleanField(default=False)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    medio_transporte = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'huespedes'
        verbose_name = 'Huésped'
        verbose_name_plural = 'Huéspedes'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def save(self, *args, **kwargs):
        from datetime import date
        hoy = date.today()
        self.edad = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        super().save(*args, **kwargs)
