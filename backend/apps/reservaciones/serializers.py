from rest_framework import serializers
from .models import Reservacion, ReservacionHuespedes, Consumo, Pago

class ReservacionSerializer(serializers.ModelSerializer):
    # Campos anidados para el frontend
    habitacion_numero = serializers.CharField(source='id_habitacion.numero', read_only=True)
    habitacion_tipo = serializers.CharField(source='id_habitacion.categoria_tipo', read_only=True)
    huesped_nombre = serializers.SerializerMethodField(read_only=True)
    huesped_documento = serializers.SerializerMethodField(read_only=True)
    tipo_cliente = serializers.CharField(source='id_huesped_titular.tipo_cliente_profesion', read_only=True)

    class Meta:
        model = Reservacion
        fields = '__all__'
        read_only_fields = [
            'numero_noches', 'total_habitacion', 'monto_total_consumos',
            'monto_total_final', 'monto_pagado', 'saldo_pendiente',
            'fecha_checkin_real', 'fecha_checkout_real'
        ]

    def get_huesped_nombre(self, obj):
        return f"{obj.id_huesped_titular.nombres} {obj.id_huesped_titular.apellidos}"

    def get_huesped_documento(self, obj):
        return f"{obj.id_huesped_titular.tipo_documento}-{obj.id_huesped_titular.numero_documento}"


class ReservacionHuespedesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservacionHuespedes
        fields = '__all__'

class ConsumoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True, default=None)
    producto_precio = serializers.CharField(source='producto.precio_venta', read_only=True, default=None)

    class Meta:
        model = Consumo
        fields = '__all__'
        read_only_fields = ['total']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'