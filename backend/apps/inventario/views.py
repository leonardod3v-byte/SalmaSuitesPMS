from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Producto, MovimientoInventario
from .serializers import ProductoSerializer, ProductoListSerializer, MovimientoSerializer


def registrar_movimiento(producto, tipo, cantidad, usuario, motivo=''):
    """
    Función auxiliar para registrar cualquier movimiento de inventario
    y actualizar el stock del producto automáticamente.
    """
    stock_anterior = producto.stock_actual
    stock_nuevo = max(0, stock_anterior + cantidad)

    MovimientoInventario.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        motivo=motivo,
        registrado_por=usuario
    )

    producto.stock_actual = stock_nuevo
    producto.save()

    return stock_nuevo


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def productos_list(request):
    """
    GET: Lista productos con filtros opcionales.
         /api/inventario/?categoria=bebida
         /api/inventario/?alerta=true  (solo los que tienen stock bajo)
         /api/inventario/?search=agua
    POST: Crea un nuevo producto (solo admin).
    """
    if request.method == 'GET':
        qs = Producto.objects.filter(activo=True)

        categoria = request.query_params.get('categoria')
        alerta = request.query_params.get('alerta')
        search = request.query_params.get('search')

        if categoria:
            qs = qs.filter(categoria=categoria)
        if alerta == 'true':
            qs = qs.filter(Q(sin_stock=True) | Q(stock_bajo=True))
        if search:
            qs = qs.filter(nombre__icontains=search)

        serializer = ProductoListSerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if request.user.role != 'admin':
            return Response(
                {'error': 'Solo el administrador puede crear productos.'},
                status=403
            )
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def producto_detail(request, pk):
    """
    GET: Detalle del producto con sus últimos movimientos.
    PUT: Editar datos del producto.
    DELETE: Desactivar producto (no se elimina físicamente).
    """
    try:
        producto = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=404)

    if request.method == 'GET':
        serializer = ProductoSerializer(producto)
        movimientos = MovimientoInventario.objects.filter(
            producto=producto
        ).select_related('registrado_por')[:15]
        movimientos_serializer = MovimientoSerializer(movimientos, many=True)

        return Response({
            'producto': serializer.data,
            'movimientos': movimientos_serializer.data
        })

    if request.method == 'PUT':
        serializer = ProductoSerializer(producto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response(
                {'error': 'Solo el administrador puede desactivar productos.'},
                status=403
            )
        # Desactivar en lugar de borrar para mantener historial
        producto.activo = False
        producto.save()
        return Response({'message': 'Producto desactivado correctamente.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def entrada_stock(request, pk):
    """
    Registra una entrada de stock (reabastecimiento).
    Body: { "cantidad": 20, "motivo": "Compra semanal" }
    """
    try:
        producto = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=404)

    cantidad = request.data.get('cantidad')
    if not cantidad or int(cantidad) <= 0:
        return Response({'error': 'La cantidad debe ser mayor a 0.'}, status=400)

    nuevo_stock = registrar_movimiento(
        producto=producto,
        tipo='entrada',
        cantidad=int(cantidad),
        usuario=request.user,
        motivo=request.data.get('motivo', 'Entrada de stock')
    )

    return Response({
        'message': f'Stock actualizado correctamente.',
        'stock_anterior': nuevo_stock - int(cantidad),
        'stock_nuevo': nuevo_stock
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ajuste_stock(request, pk):
    """
    Ajuste manual del stock (pérdidas, correcciones, etc.).
    Body: { "stock_nuevo": 15, "motivo": "Corrección de inventario" }
    """
    try:
        producto = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=404)

    stock_nuevo = request.data.get('stock_nuevo')
    if stock_nuevo is None or int(stock_nuevo) < 0:
        return Response({'error': 'stock_nuevo debe ser un número positivo.'}, status=400)

    diferencia = int(stock_nuevo) - producto.stock_actual
    tipo = 'ajuste' if diferencia >= 0 else 'perdida'

    registrar_movimiento(
        producto=producto,
        tipo=tipo,
        cantidad=diferencia,
        usuario=request.user,
        motivo=request.data.get('motivo', 'Ajuste manual')
    )

    return Response({
        'message': 'Stock ajustado correctamente.',
        'stock_nuevo': producto.stock_actual
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def alertas_stock(request):
    """
    RF13: Retorna todos los productos con stock bajo o sin stock.
    Se usa en el dashboard para mostrar alertas.
    """
    sin_stock = Producto.objects.filter(activo=True, sin_stock=True)
    stock_bajo = Producto.objects.filter(activo=True, stock_bajo=True, sin_stock=False)

    return Response({
        'sin_stock': ProductoListSerializer(sin_stock, many=True).data,
        'stock_bajo': ProductoListSerializer(stock_bajo, many=True).data,
        'total_alertas': sin_stock.count() + stock_bajo.count()
    })