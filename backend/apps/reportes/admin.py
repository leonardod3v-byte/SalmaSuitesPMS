from django.contrib import admin
from .models import ReporteGenerado


@admin.register(ReporteGenerado)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'formato', 'nombre_archivo', 'generado_por', 'created_at']
    list_filter = ['tipo', 'formato']