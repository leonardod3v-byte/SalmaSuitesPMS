from django.contrib import admin
from .models import Pago, CierreCaja


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'monto', 'metodo', 'concepto', 'referencia', 'registrado_por', 'fecha']
    list_filter = ['metodo', 'concepto', 'fecha']
    search_fields = ['reserva__huesped__nombre', 'referencia']


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'recepcionista', 'total_caja', 'pdf_generado', 'created_at']
    list_filter = ['fecha', 'pdf_generado']