from rest_framework import serializers
from .models import Huesped
from apps.configuracion.serializers import OcupacionSerializer
from datetime import date


class HuespedSerializer(serializers.ModelSerializer):
    ocupacion_detalle = OcupacionSerializer(source='ocupacion', read_only=True)

    class Meta:
        model = Huesped
        fields = [
            'id', 'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
            'fecha_nacimiento', 'edad', 'nacionalidad', 'estado_civil', 'telefono',
            'email', 'direccion', 'ocupacion', 'ocupacion_detalle', 'alergias',
            'categoria', 'credito_autorizado', 'limite_credito', 'observaciones',
            'medio_transporte'
        ]
        read_only_fields = ['edad']
        extra_kwargs = {
            'medio_transporte': {'required': False, 'allow_null': True, 'allow_blank': True},
            'observaciones': {'required': False, 'allow_blank': True},
            'limite_credito': {'required': False, 'allow_null': True},
            'ocupacion': {'required': False, 'allow_null': True},
            'direccion': {'required': False, 'allow_blank': True},
            'alergias': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
            'telefono': {'required': False, 'allow_blank': True},
        }

    def validate_fecha_nacimiento(self, value):
        hoy = date.today()
        if value > hoy:
            raise serializers.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return value

    def validate_email(self, value):
        if value:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError as DjangoValidationError
            try:
                validate_email(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Ingresa un correo electrónico válido.")
        return value

    def validate(self, data):
        tipo = data.get('tipo_documento')
        numero = data.get('numero_documento')
        instance = self.instance

        if tipo and numero:
            qs = Huesped.objects.filter(tipo_documento=tipo, numero_documento=numero)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'numero_documento': 'Ya existe un huésped con ese tipo y número de documento.'}
                )
        return data
