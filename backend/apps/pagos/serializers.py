from rest_framework import serializers
from .models import Pago, CierreCaja


class PagoSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.CharField(
        source='registrado_por.username',
        read_only=True
    )
    reserva_info = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = [
            'id', 'reserva', 'reserva_info', 'monto', 'metodo',
            'concepto', 'referencia', 'nota',
            'registrado_por_nombre', 'fecha'
        ]
        read_only_fields = ['fecha']

    def get_reserva_info(self, obj):
        return {
            'id': obj.reserva.id,
            'huesped': obj.reserva.huesped.nombre_completo,
            'habitacion': obj.reserva.habitacion.numero,
        }


class CierreCajaSerializer(serializers.ModelSerializer):
    recepcionista_nombre = serializers.CharField(
        source='recepcionista.username',
        read_only=True
    )

    class Meta:
        model = CierreCaja
        fields = [
            'id', 'fecha', 'recepcionista', 'recepcionista_nombre',
            'efectivo_usd', 'efectivo_ves', 'transferencias',
            'tarjetas', 'pago_movil', 'zelle', 'binance',
            'total_caja', 'observaciones',
            'pdf_generado', 'pdf_url', 'created_at'
        ]
        read_only_fields = ['total_caja', 'pdf_generado', 'pdf_url', 'created_at']