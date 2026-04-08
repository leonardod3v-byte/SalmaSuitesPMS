from django.db import models
from apps.users.models import User


class Producto(models.Model):
    """
    RF13: Inventario básico de productos del hotel.
    Maneja stock mínimo y máximo con alertas automáticas.
    """
    CATEGORIAS = [
        ('bebida', 'Bebida'),
        ('comida', 'Comida'),
        ('snack', 'Snack'),
        ('licor', 'Licor'),
        ('higiene', 'Higiene'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(
        default=5,
        help_text='Si el stock baja de este número se genera una alerta'
    )
    stock_maximo = models.PositiveIntegerField(
        default=50,
        help_text='Cantidad máxima recomendada para este producto'
    )

    # Se actualiza automáticamente en el save()
    sin_stock = models.BooleanField(default=False)
    stock_bajo = models.BooleanField(default=False)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'productos'
        ordering = ['categoria', 'nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f'{self.nombre} ({self.categoria}) - Stock: {self.stock_actual}'

    def save(self, *args, **kwargs):
        # Actualizar alertas automáticamente al guardar
        self.sin_stock = self.stock_actual == 0
        self.stock_bajo = self.stock_actual <= self.stock_minimo
        super().save(*args, **kwargs)

    @property
    def estado_stock(self):
        """Retorna el estado visual del stock para el frontend."""
        if self.stock_actual == 0:
            return 'sin_stock'
        if self.stock_actual <= self.stock_minimo:
            return 'stock_bajo'
        if self.stock_actual >= self.stock_maximo:
            return 'stock_alto'
        return 'normal'


class MovimientoInventario(models.Model):
    """
    Registra cada entrada o salida de stock.
    Así puedes ver el historial completo de movimientos.
    """
    TIPOS = [
        ('entrada', 'Entrada de stock'),
        ('salida', 'Salida por consumo'),
        ('ajuste', 'Ajuste manual'),
        ('perdida', 'Pérdida o daño'),
    ]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    cantidad = models.IntegerField(
        help_text='Positivo para entradas, negativo para salidas'
    )
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movimientos_inventario'
        ordering = ['-created_at']
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'

    def __str__(self):
        return f'{self.tipo} | {self.producto.nombre} | {self.cantidad:+d}'