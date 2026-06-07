from django.db import models


class Huesped(models.Model):
    """
    Representa a cada huésped registrado en el hotel (RF04).
    El tipo de documento sigue el formato venezolano (V, E, J, G, P).
    """
    TIPO_DOCUMENTO = [
        ('V', 'Venezolano (V)'),
        ('E', 'Extranjero (E)'),
        ('J', 'Jurídico (J)'),
        ('G', 'Gubernamental (G)'),
        ('P', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO, default='V')
    numero_documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    es_vip = models.BooleanField(default=False)
    notas = models.TextField(blank=True)
    procedencia = models.CharField(max_length=100, blank=True, null=True)
    profesion = models.CharField(max_length=100, blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    nacionalidad = models.CharField(max_length=50, blank=True, null=True)
    estado_civil = models.CharField(
    max_length=20,
    choices=[('soltero','Soltero'),('casado','Casado'),('divorciado','Divorciado'),('viudo','Viudo')],
    blank=True, null=True
    )
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)

    # RF04: Acompañantes guardados como lista JSON
    # Formato: [{"nombre": "Juan", "documento": "V-12345678", "edad": 30}, ...]
    acompanantes = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'huespedes'
        ordering = ['apellido', 'nombre']
        verbose_name = 'Huésped'
        verbose_name_plural = 'Huéspedes'

    def __str__(self):
        return f'{self.tipo_documento}-{self.numero_documento} | {self.nombre} {self.apellido}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def documento_formateado(self):
        return f'{self.tipo_documento}-{self.numero_documento}'