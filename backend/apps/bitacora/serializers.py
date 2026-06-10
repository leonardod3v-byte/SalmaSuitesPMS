from rest_framework import serializers
from .models import ActividadLog, CierreCaja

class ActividadLogSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(source='id_usuario.username')

    class Meta:
        model = ActividadLog
        fields = ['id', 'fecha_hora', 'usuario', 'tipo', 'descripcion', 'id_referencia']

class CierreCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CierreCaja
        fields = '__all__'
        read_only_fields = ['id_usuario', 'fecha_hora_cierre']