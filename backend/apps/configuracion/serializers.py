from rest_framework import serializers
from .models import Ocupacion


class OcupacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ocupacion
        fields = ['id', 'nombre', 'color']
        read_only_fields = ['id']
