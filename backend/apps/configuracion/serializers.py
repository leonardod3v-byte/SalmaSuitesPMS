from rest_framework import serializers
from .models import Configuracion, Ocupacion

class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = ['clave', 'valor']

class OcupacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ocupacion
        fields = ['id', 'nombre', 'color']
        read_only_fields = ['id']
