from rest_framework import serializers
from .models import Habitacion

class HabitacionSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField(read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Habitacion
        fields = '__all__'
        read_only_fields = ['id']

    def get_imagen_url(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return None
class CambioEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Habitacion.ESTADO)
    notas = serializers.CharField(required=False, allow_blank=True)
    es_emergencia = serializers.BooleanField(default=False)
    pasar_a_limpia = serializers.BooleanField(default=False)  # solo para finalizar mantenimiento/obra