from django.contrib import admin
from .models import Huesped


@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ['documento_formateado', 'nombre_completo', 'telefono', 'email', 'es_vip', 'created_at']
    list_filter = ['es_vip', 'tipo_documento']
    search_fields = ['nombre', 'apellido', 'numero_documento', 'email']