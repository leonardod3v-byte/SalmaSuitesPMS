from rest_framework import serializers
from .models import Empresa
import re

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

    def validate_rif(self, value):
        if not re.match(r'^[VEJPG]-\d{8}-\d$', value):
            raise serializers.ValidationError("El formato del RIF debe ser J-12345678-9.")
        return value.upper()
