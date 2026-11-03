from django.db import models

class Configuracion(models.Model):
    clave = models.CharField(max_length=50, primary_key=True)
    valor = models.TextField()

    class Meta:
        db_table = 'configuracion'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'

    def __str__(self):
        return self.clave


class Ocupacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#3b82f6', help_text="Color hex (ej: #3b82f6)")

    class Meta:
        db_table = 'ocupaciones'
        verbose_name = 'Ocupación'
        verbose_name_plural = 'Ocupaciones'

    def __str__(self):
        return self.nombre
