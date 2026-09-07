from django.db import models
from apps.usuarios.models import User

class Producto(models.Model):
    CATEGORIA = [
        ('Bebida', 'Bebida'),
        ('Snack', 'Snack'),
        ('Comida', 'Comida'),
        ('Lavandería', 'Lavandería'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad = models.CharField(max_length=20)  # ej: unidad, kg, porción
    activo = models.BooleanField(default=True)
    maneja_stock = models.BooleanField(default=True)

    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre


class InventarioMovimiento(models.Model):
    TIPO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    id_usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'inventario_movimientos'
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'