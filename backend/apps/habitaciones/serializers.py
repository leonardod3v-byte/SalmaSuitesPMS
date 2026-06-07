from rest_framework import serializers
from .models import TipoHabitacion, Habitacion, HistorialEstadoHabitacion


class TipoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacion
        fields = '__all__'


class HabitacionSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    tipo_precio = serializers.DecimalField(
        source='tipo.precio_base_noche',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    # Capacidad máxima desde el tipo
    capacidad_maxima = serializers.IntegerField(source='tipo.capacidad_maxima', read_only=True)

    class Meta:
        model = Habitacion
        fields = [
            'id', 'numero', 'piso', 'estado', 'tiene_minibar',
            'qr_code', 'notas', 'tipo', 'tipo_nombre', 'tipo_precio',
            'capacidad_maxima',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['qr_code', 'created_at', 'updated_at']


class HistorialSerializer(serializers.ModelSerializer):
    cambiado_por_nombre = serializers.CharField(source='cambiado_por.username', read_only=True)

    class Meta:
        model = HistorialEstadoHabitacion
        fields = ['id', 'estado_anterior', 'estado_nuevo', 'cambiado_por_nombre', 'nota', 'created_at']