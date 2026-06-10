from django.db import transaction, models
from django.core.exceptions import ValidationError
from .models import Producto, InventarioMovimiento

# Productos -------------------------------------------------------

def listar_productos(categoria=None, estado=None):
    qs = Producto.objects.filter(activo=True)
    if categoria:
        qs = qs.filter(categoria=categoria)
    if estado == 'Bajo':
        qs = qs.filter(stock_actual__lte=models.F('stock_minimo'), stock_actual__gt=0)
    elif estado == 'Agotado':
        qs = qs.filter(stock_actual=0)
    elif estado == 'Normal':
        qs = qs.filter(stock_actual__gt=models.F('stock_minimo'))
    return qs

def obtener_producto(pk):
    return Producto.objects.get(pk=pk)

def crear_producto(**datos):
    producto = Producto(**datos)
    producto.full_clean()
    producto.save()
    return producto

def actualizar_producto(producto, datos):
    for campo, valor in datos.items():
        if campo not in ['id', 'stock_actual']:
            setattr(producto, campo, valor)
    producto.full_clean()
    producto.save()
    return producto

def desactivar_producto(producto):
    producto.activo = False
    producto.save()

# Movimientos -----------------------------------------------------

@transaction.atomic
def registrar_entrada(producto_id, cantidad, motivo, usuario):
    producto = Producto.objects.select_for_update().get(pk=producto_id)
    producto.stock_actual += cantidad
    producto.save()
    movimiento = InventarioMovimiento.objects.create(
        producto=producto,
        tipo='entrada',
        cantidad=cantidad,
        motivo=motivo,
        id_usuario=usuario
    )
    return movimiento

@transaction.atomic
def registrar_ajuste(producto_id, cantidad, motivo, usuario):
    """
    cantidad positiva = aumento, negativa = disminución.
    """
    producto = Producto.objects.select_for_update().get(pk=producto_id)
    nuevo_stock = producto.stock_actual + cantidad
    if nuevo_stock < 0:
        raise ValidationError('Stock insuficiente para realizar este ajuste.')
    producto.stock_actual = nuevo_stock
    producto.save()
    movimiento = InventarioMovimiento.objects.create(
        producto=producto,
        tipo='ajuste',
        cantidad=cantidad,
        motivo=motivo,
        id_usuario=usuario
    )
    return movimiento

@transaction.atomic
def registrar_salida_consumo(producto_id, cantidad, reserva_id, usuario=None):
    """
    Llamado desde el servicio de consumos cuando se selecciona un producto del inventario.
    """
    producto = Producto.objects.select_for_update().get(pk=producto_id)
    if producto.stock_actual < cantidad:
        raise ValidationError(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}')
    producto.stock_actual -= cantidad
    producto.save()
    movimiento = InventarioMovimiento.objects.create(
        producto=producto,
        tipo='salida',
        cantidad=cantidad,
        motivo=f'Consumo Reserva #{reserva_id}',
        id_usuario=usuario
    )
    return movimiento

def listar_movimientos(producto_id=None):
    qs = InventarioMovimiento.objects.select_related('producto', 'id_usuario').order_by('-fecha')
    if producto_id:
        qs = qs.filter(producto_id=producto_id)
    return qs

# Alertas ---------------------------------------------------------

def productos_bajos():
    """Retorna la cantidad de productos con stock bajo o agotado."""
    return Producto.objects.filter(
        activo=True,
        stock_actual__lte=models.F('stock_minimo')
    ).count()