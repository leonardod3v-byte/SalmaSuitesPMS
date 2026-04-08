from django.db import models
from apps.users.models import User


class ReporteGenerado(models.Model):
    """
    Registra cada reporte generado para poder descargarlo después
    sin tener que regenerarlo.
    """
    TIPOS = [
        ('consumos_huesped', 'Consumos por Huésped'),
        ('reservas_activas', 'Reservas Activas'),
        ('ingresos_periodo', 'Ingresos por Período'),
        ('cierre_caja', 'Cierre de Caja'),
        ('inventario', 'Inventario'),
    ]

    FORMATOS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPOS)
    formato = models.CharField(max_length=10, choices=FORMATOS)
    nombre_archivo = models.CharField(max_length=255)
    archivo_url = models.CharField(max_length=500, blank=True)
    generado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    parametros = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reportes_generados'
        ordering = ['-created_at']
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'

    def __str__(self):
        return f'{self.tipo} ({self.formato}) - {self.created_at.strftime("%d/%m/%Y")}'