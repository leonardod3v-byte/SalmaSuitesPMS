from rest_framework import serializers
from .models import Pago
from .models import Pago, CierreCaja


class PagoSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.CharField(
        source='registrado_por.username',
        read_only=True
    )
    reserva_info = serializers.SerializerMethodField()

    # Permitir referencia vacía o nula (para efectivo, etc.)
    referencia = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100
    )

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


class PagoListSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.CharField(source='registrado_por.username', read_only=True)

    class Meta:
        model = Pago
        fields = [
            'id', 'monto', 'metodo', 'concepto', 'referencia',
            'registrado_por_nombre', 'fecha'
        ]


class CierreCajaSerializer(serializers.ModelSerializer):
    recepcionista_nombre = serializers.CharField(source='recepcionista.username', read_only=True)

    class Meta:
        model = CierreCaja
        fields = [
            'id', 'fecha', 'recepcionista', 'recepcionista_nombre',
            'total_efectivo', 'total_tarjeta', 'total_pago_movil',
            'total_general', 'observaciones',
            'pdf_generado', 'pdf_url', 'created_at'
        ]
        read_only_fields = ['total_general', 'pdf_generado', 'pdf_url', 'created_at']