from django.contrib import admin
from .models import Reserva, Consumo, Actividad


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'huesped', 'habitacion', 'estado', 'fecha_entrada', 'fecha_salida', 'monto_total']
    list_filter = ['estado', 'metodo_pago', 'fecha_entrada']
    search_fields = ['huesped__nombre', 'huesped__apellido', 'habitacion__numero']


@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cantidad', 'precio_unitario', 'reserva', 'fecha_consumo']
    list_filter = ['fecha_consumo']


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'descripcion', 'usuario', 'created_at']
    list_filter = ['tipo']