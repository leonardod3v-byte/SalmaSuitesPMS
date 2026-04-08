from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = [
        'tipo', 'canal', 'estado',
        'destinatario_nombre', 'destinatario_telefono',
        'reserva_id', 'created_at'
    ]
    list_filter = ['tipo', 'canal', 'estado']
    search_fields = ['destinatario_nombre', 'destinatario_telefono']