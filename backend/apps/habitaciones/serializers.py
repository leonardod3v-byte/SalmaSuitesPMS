from rest_framework import serializers
from .models import Habitacion
import re


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
        # Validar formato: alfanumérico con guiones, 1-10 caracteres
        if not value:
            raise serializers.ValidationError("El número de habitación es obligatorio.")
        value = value.strip()
        if not re.match(r'^[A-Za-z0-9\-]{1,10}$', value):
            raise serializers.ValidationError(
                "El número solo puede contener letras, números y guiones (máximo 10 caracteres)."
            )

        # Verificar unicidad
        instance = self.instance
        qs = Habitacion.objects.filter(numero=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe una habitación con ese número.')

        return value

    def validate_piso(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("El piso debe estar entre 1 y 20.")
        return value

    def validate_cantidad_camas(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("La cantidad de camas debe estar entre 1 y 10.")
        return value

    def validate_capacidad_maxima(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("La capacidad máxima debe estar entre 1 y 10.")
        return value

    def validate_precio_por_noche(self, value):
        if value is None:
            raise serializers.ValidationError("El precio por noche es obligatorio.")
        if value < 0:
            raise serializers.ValidationError("El precio por noche debe ser mayor o igual a 0.")
        return value

    def validate_precio_empresa(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El precio empresa debe ser mayor o igual a 0.")
        return value

    def validate_categoria_tipo(self, value):
        tipos_validos = [t[0] for t in Habitacion.CATEGORIA_TIPO]
        if value not in tipos_validos:
            raise serializers.ValidationError(
                f"Categoría no válida. Opciones: {', '.join(tipos_validos)}."
            )
        return value

    def validate_estado(self, value):
        estados_validos = [e[0] for e in Habitacion.ESTADO]
        if value not in estados_validos:
            raise serializers.ValidationError(
                f"Estado no válido. Opciones: {', '.join(estados_validos)}."
            )
        return value

    def validate(self, data):
        # Capacidad >= cantidad de camas
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
