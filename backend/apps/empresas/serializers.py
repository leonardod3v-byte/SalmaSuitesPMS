from rest_framework import serializers
from .models import Empresa
from apps.utils import (
    validar_email, validar_telefono, validar_nombre,
    validar_rif, validar_direccion,
)


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

    def validate_rif(self, value):
        return validar_rif(value)

    def validate_nombre(self, value):
        return validar_nombre(value, campo="nombre")

    def validate_telefono(self, value):
        return validar_telefono(value)

    def validate_email(self, value):
        return validar_email(value)

    def validate_direccion_fiscal(self, value):
        return validar_direccion(value)
