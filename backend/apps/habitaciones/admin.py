from django.contrib import admin
from .models import TipoHabitacion, Habitacion, HistorialEstadoHabitacion


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'capacidad_maxima', 'precio_base_noche']


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'piso', 'tipo', 'estado', 'tiene_minibar', 'qr_code']
    list_filter = ['estado', 'piso', 'tipo']
    search_fields = ['numero']


@admin.register(HistorialEstadoHabitacion)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ['habitacion', 'estado_anterior', 'estado_nuevo', 'cambiado_por', 'created_at']
    list_filter = ['estado_nuevo']