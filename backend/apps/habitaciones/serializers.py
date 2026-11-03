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

    def validate_numero(self, value):
        # Verificar que el número sea único
        instance = self.instance
        qs = Habitacion.objects.filter(numero=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe una habitación con ese número.')
        return value

    def validate(self, data):
        # Validar que la capacidad máxima sea mayor o igual a las camas
        cantidad = data.get('cantidad_camas', getattr(self.instance, 'cantidad_camas', 0))
        capacidad = data.get('capacidad_maxima', getattr(self.instance, 'capacidad_maxima', 0))
        if capacidad < cantidad:
            raise serializers.ValidationError({
                'capacidad_maxima': 'La capacidad máxima no puede ser menor que la cantidad de camas.'
            })
        return data


class CambioEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Habitacion.ESTADO)
    notas = serializers.CharField(required=False, allow_blank=True)
    es_emergencia = serializers.BooleanField(default=False)
    pasar_a_limpia = serializers.BooleanField(default=False)
