from rest_framework import serializers
from .models import Producto, InventarioMovimiento

class ProductoSerializer(serializers.ModelSerializer):
    estado_stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['stock_actual']

    def get_estado_stock(self, obj):
        if obj.stock_actual == 0:
            return 'Agotado'
        if obj.stock_actual <= obj.stock_minimo:
            return 'Bajo'
        return 'Normal'

class ProductoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'precio_venta', 'stock_minimo', 'unidad', 'activo']

class InventarioMovimientoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.StringRelatedField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.StringRelatedField(source='id_usuario.username', read_only=True)

    class Meta:
        model = InventarioMovimiento
        fields = '__all__'
        read_only_fields = ['fecha', 'id_usuario']

class EntradaSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    motivo = serializers.CharField()

class AjusteSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    motivo = serializers.CharField()