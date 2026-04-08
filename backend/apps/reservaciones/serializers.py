from rest_framework import serializers
from .models import Reserva, Consumo, Actividad
from apps.guests.serializers import HuespedListSerializer
from apps.habitaciones.serializers import HabitacionSerializer


class ConsumoSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    registrado_por_nombre = serializers.CharField(
        source='registrado_por.username',
        read_only=True
    )

    class Meta:
        model = Consumo
        fields = [
            'id', 'producto', 'cantidad', 'precio_unitario',
            'noches_asociadas', 'total', 'nota',
            'registrado_por_nombre', 'fecha_consumo'
        ]
        read_only_fields = ['fecha_consumo']


class ReservaListSerializer(serializers.ModelSerializer):
    """
    Versión reducida para listados y referencias desde otras apps.
    """
    huesped_nombre = serializers.CharField(source='huesped.nombre_completo', read_only=True)
    huesped_documento = serializers.CharField(source='huesped.documento_formateado', read_only=True)
    habitacion_numero = serializers.CharField(source='habitacion.numero', read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    noches = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'estado', 'fecha_entrada', 'fecha_salida', 'noches',
            'huesped_nombre', 'huesped_documento',
            'habitacion_numero', 'monto_total', 'monto_pagado',
            'saldo_pendiente', 'metodo_pago', 'created_at'
        ]


class ReservaSerializer(serializers.ModelSerializer):
    """
    Versión completa con todos los datos y consumos anidados.
    """
    huesped_data = HuespedListSerializer(source='huesped', read_only=True)
    habitacion_data = HabitacionSerializer(source='habitacion', read_only=True)
    consumos = ConsumoSerializer(many=True, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    noches = serializers.IntegerField(read_only=True)
    creada_por_nombre = serializers.CharField(source='creada_por.username', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'estado', 'fecha_entrada', 'fecha_salida',
            'hora_check_in', 'hora_check_out', 'noches',
            'huesped', 'huesped_data',
            'habitacion', 'habitacion_data', 'habitacion_original',
            'metodo_pago', 'referencia_pago',
            'monto_total', 'monto_pagado', 'saldo_pendiente',
            'requiere_factura_seniat', 'datos_factura',
            'no_show_motivo', 'no_show_fecha',
            'notas', 'consumos', 'creada_por_nombre',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ActividadSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    habitacion_numero = serializers.CharField(source='habitacion.numero', read_only=True)

    class Meta:
        model = Actividad
        fields = [
            'id', 'tipo', 'descripcion', 'detalle',
            'habitacion_numero', 'usuario_nombre', 'created_at'
        ]