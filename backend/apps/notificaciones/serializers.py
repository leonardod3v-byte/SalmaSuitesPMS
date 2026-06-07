from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    """
    Serializer de alta optimización para el módulo de Notificaciones.
    Formatea fechas de manera uniforme y expone metadatos clave para el frontend.
    """
    fecha_envio_formateada = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        fields = [
            'id', 
            'reserva', 
            'tipo', 
            'canal', 
            'destinatario', 
            'mensaje', 
            'estado', 
            'fecha_envio', 
            'fecha_envio_formateada',
            'intentos', 
            'error_mensaje'
        ]
        # Dejamos todo como read_only porque las notificaciones se generan a través 
        # de servicios/triggers del sistema, no mediante payloads directos del frontend.
        read_only_fields = fields

    def get_fecha_envio_formateada(self, obj):
        """
        Retorna la fecha formateada legible para tablas o componentes de SvelteKit.
        """
        if obj.fecha_envio:
            return obj.fecha_envio.strftime("%Y-%m-%d %H:%M:%S")
        return "Pendiente"