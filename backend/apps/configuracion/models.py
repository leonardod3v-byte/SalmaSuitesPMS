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


class ColoresTipoCliente(models.Model):
    tipo_cliente_profesion = models.CharField(max_length=30, primary_key=True)
    color = models.CharField(max_length=7)

    class Meta:
        db_table = 'colores_tipo_cliente'
        verbose_name = 'Color por tipo de cliente'
        verbose_name_plural = 'Colores por tipo de cliente'


class ColoresEstadoHabitacion(models.Model):
    estado = models.CharField(max_length=15, primary_key=True)
    color = models.CharField(max_length=7)

    class Meta:
        db_table = 'colores_estado_habitacion'
        verbose_name = 'Color por estado de habitación'
        verbose_name_plural = 'Colores por estado de habitación'