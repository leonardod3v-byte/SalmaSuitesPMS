from rest_framework import serializers
from .models import Configuracion, ColoresTipoCliente, ColoresEstadoHabitacion

class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = ['clave', 'valor']

class ColoresTipoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColoresTipoCliente
        fields = '__all__'

class ColoresEstadoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColoresEstadoHabitacion
        fields = '__all__'