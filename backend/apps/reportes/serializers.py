from rest_framework import serializers

class PagoDiarioSerializer(serializers.Serializer):
    hora = serializers.TimeField()
    reserva_id = serializers.IntegerField()
    huesped = serializers.CharField()
    metodo_pago = serializers.CharField()
    numero_referencia = serializers.CharField()
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)

class ResumenDiarioSerializer(serializers.Serializer):
    total_general = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_efectivo = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_tarjeta = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_pago_movil = serializers.DecimalField(max_digits=10, decimal_places=2)
    cantidad_transacciones = serializers.IntegerField()
    cerrado = serializers.BooleanField()
    detalle = PagoDiarioSerializer(many=True)

class IngresoPeriodoSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    efectivo = serializers.DecimalField(max_digits=10, decimal_places=2)
    tarjeta = serializers.DecimalField(max_digits=10, decimal_places=2)
    pago_movil = serializers.DecimalField(max_digits=10, decimal_places=2)