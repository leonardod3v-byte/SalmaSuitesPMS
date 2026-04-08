from rest_framework import serializers
from .models import Huesped


class HuespedSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    documento_formateado = serializers.CharField(read_only=True)

    class Meta:
        model = Huesped
        fields = [
            'id', 'tipo_documento', 'numero_documento',
            'nombre', 'apellido', 'nombre_completo', 'documento_formateado',
            'telefono', 'email', 'es_vip', 'notas', 'acompanantes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class HuespedListSerializer(serializers.ModelSerializer):
    """
    Versión reducida para listados, sin campos pesados.
    """
    nombre_completo = serializers.CharField(read_only=True)
    documento_formateado = serializers.CharField(read_only=True)

    class Meta:
        model = Huesped
        fields = [
            'id', 'nombre_completo', 'documento_formateado',
            'telefono', 'email', 'es_vip', 'created_at'
        ]