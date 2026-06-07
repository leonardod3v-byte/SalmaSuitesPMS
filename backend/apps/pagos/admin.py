from django.contrib import admin
from .models import Pago, CierreCaja

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'monto', 'metodo', 'fecha', 'registrado_por')
    list_filter = ('metodo', 'fecha')
    search_fields = ('reserva__id', 'referencia')

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'recepcionista', 'fecha', 'total_general', 'created_at')
    list_filter = ('fecha', 'recepcionista')
    search_fields = ('recepcionista__username',)
    readonly_fields = ('total_general', 'created_at')