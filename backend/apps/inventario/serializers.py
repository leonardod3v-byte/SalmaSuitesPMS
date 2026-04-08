from rest_framework import serializers
from .models import Producto, MovimientoInventario


class ProductoSerializer(serializers.ModelSerializer):
    estado_stock = serializers.CharField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'descripcion',
            'precio_venta', 'precio_costo',
            'stock_actual', 'stock_minimo', 'stock_maximo',
            'sin_stock', 'stock_bajo', 'estado_stock',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sin_stock', 'stock_bajo', 'created_at', 'updated_at']


class ProductoListSerializer(serializers.ModelSerializer):
    """Versión reducida para listados."""
    estado_stock = serializers.CharField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'precio_venta',
            'stock_actual', 'stock_minimo', 'estado_stock', 'activo'
        ]


class MovimientoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    registrado_por_nombre = serializers.CharField(
        source='registrado_por.username',
        read_only=True
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'producto', 'producto_nombre', 'tipo',
            'cantidad', 'stock_anterior', 'stock_nuevo',
            'motivo', 'registrado_por_nombre', 'created_at'
        ]
        read_only_fields = ['stock_anterior', 'stock_nuevo', 'created_at']