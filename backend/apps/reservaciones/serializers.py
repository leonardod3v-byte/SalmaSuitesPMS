from rest_framework import serializers
from .models import Reservacion, ReservacionHuespedes, Consumo, Pago
from apps.huespedes.models import Huesped


class HuespedBasicoSerializer(serializers.ModelSerializer):
    ocupacion_nombre = serializers.SerializerMethodField()
    ocupacion_color = serializers.SerializerMethodField()

    class Meta:
        model = Huesped
        fields = [
            'id', 'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
            'fecha_nacimiento', 'edad', 'nacionalidad', 'estado_civil',
            'telefono', 'email', 'direccion', 'alergias',
            'ocupacion_nombre', 'ocupacion_color',
        ]

    def get_ocupacion_nombre(self, obj):
        return obj.ocupacion.nombre if obj.ocupacion else None

    def get_ocupacion_color(self, obj):
        return obj.ocupacion.color if obj.ocupacion else None


class ReservacionHuespedesSerializer(serializers.ModelSerializer):
    huesped_detalle = HuespedBasicoSerializer(source='id_huesped', read_only=True)

    class Meta:
        model = ReservacionHuespedes
        fields = ['id', 'id_huesped', 'rol', 'huesped_detalle']


class ReservacionSerializer(serializers.ModelSerializer):
    habitacion_numero = serializers.CharField(source='id_habitacion.numero', read_only=True)
    habitacion_tipo = serializers.CharField(source='id_habitacion.categoria_tipo', read_only=True)
    huesped_nombre = serializers.SerializerMethodField(read_only=True)
    huesped_documento = serializers.SerializerMethodField(read_only=True)
    huesped_titular_detalle = HuespedBasicoSerializer(source='id_huesped_titular', read_only=True)

    ocupacion_nombre = serializers.SerializerMethodField(read_only=True)
    ocupacion_color = serializers.SerializerMethodField(read_only=True)

    empresa_nombre = serializers.CharField(source='id_empresa.nombre', read_only=True, default=None)
    empresa_rif = serializers.CharField(source='id_empresa.rif', read_only=True, default=None)

    acompanantes = serializers.SerializerMethodField()

    class Meta:
        model = Reservacion
        fields = [
            'id', 'id_huesped_titular', 'id_habitacion', 'id_empresa',
            'fecha_entrada', 'fecha_salida', 'numero_noches', 'total_habitacion',
            'estado', 'modalidad_pago', 'metodo_pago_inicial', 'numero_referencia_inicial',
            'requiere_factura', 'acta', 'motivo_cancelacion',
            'monto_total_consumos', 'monto_total_final', 'monto_pagado', 'saldo_pendiente',
            'fecha_checkin_real', 'fecha_checkout_real',
            'habitacion_numero', 'habitacion_tipo',
            'huesped_nombre', 'huesped_documento', 'huesped_titular_detalle',
            'ocupacion_nombre', 'ocupacion_color',
            'empresa_nombre', 'empresa_rif',
            'acompanantes',
        ]
        read_only_fields = [
            'numero_noches', 'total_habitacion', 'monto_total_consumos',
            'monto_total_final', 'monto_pagado', 'saldo_pendiente',
            'fecha_checkin_real', 'fecha_checkout_real'
        ]

    def get_huesped_nombre(self, obj):
        return f"{obj.id_huesped_titular.nombres} {obj.id_huesped_titular.apellidos}"

    def get_huesped_documento(self, obj):
        return f"{obj.id_huesped_titular.tipo_documento}-{obj.id_huesped_titular.numero_documento}"

    def get_ocupacion_nombre(self, obj):
        if obj.id_huesped_titular and obj.id_huesped_titular.ocupacion:
            return obj.id_huesped_titular.ocupacion.nombre
        return "Sin Ocupación"

    def get_ocupacion_color(self, obj):
        if obj.id_huesped_titular and obj.id_huesped_titular.ocupacion:
            return obj.id_huesped_titular.ocupacion.color
        return "#9E9E9E"

    def get_acompanantes(self, obj):
        qs = obj.huespedes_secundarios.filter(rol='Acompañante').select_related('id_huesped__ocupacion')
        return ReservacionHuespedesSerializer(qs, many=True).data


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
