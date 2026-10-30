from django.db import models

class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    rif = models.CharField(max_length=20, unique=True)
    direccion_fiscal = models.TextField()
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return f"{self.nombre} ({self.rif})"
