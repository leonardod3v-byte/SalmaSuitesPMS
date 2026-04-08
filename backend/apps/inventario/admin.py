from django.contrib import admin
from .models import Producto, MovimientoInventario


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'categoria', 'precio_venta',
        'stock_actual', 'stock_minimo', 'sin_stock', 'stock_bajo', 'activo'
    ]
    list_filter = ['categoria', 'sin_stock', 'stock_bajo', 'activo']
    search_fields = ['nombre']


@admin.register(MovimientoInventario)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'registrado_por', 'created_at']
    list_filter = ['tipo', 'created_at']
    search_fields = ['producto__nombre']