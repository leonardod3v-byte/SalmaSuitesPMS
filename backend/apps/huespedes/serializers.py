from rest_framework import serializers
from .models import Huesped

class HuespedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huesped
        fields = '__all__'
        read_only_fields = ['edad']  # se calcula automáticamente

    def validate(self, data):
        tipo = data.get('tipo_documento')
        numero = data.get('numero_documento')
        instance = self.instance  # None si es creación

        if tipo and numero:
            qs = Huesped.objects.filter(tipo_documento=tipo, numero_documento=numero)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'numero_documento': 'Ya existe un huésped con ese tipo y número de documento.'}
                )
        return data