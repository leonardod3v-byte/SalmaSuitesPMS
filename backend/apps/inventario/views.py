from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F  # Importa F para expresiones atómicas
from django.db import transaction  # Importa transaction para bloques atómicos

from .models import Producto, MovimientoInventario
from .serializers import ProductoSerializer, ProductoListSerializer, MovimientoSerializer


def registrar_movimiento(producto, tipo, cantidad_movimiento, usuario, motivo=''):
    """
    Función auxiliar para registrar cualquier movimiento de inventario
    y actualizar el stock del producto automáticamente de forma atómica.
    Debe ser llamada dentro de un bloque transaction.atomic()
    con una instancia de producto obtenida via select_for_update().

    'cantidad_movimiento' puede ser positiva (entrada/ajuste de aumento) o negativa (salida/ajuste de disminución).
    """
    # Se asegura que 'producto' viene con el stock más reciente y está bloqueado.
    stock_anterior = producto.stock_actual

    # Usa F() para una actualización atómica en la base de datos.
    producto.stock_actual = F('stock_actual') + cantidad_movimiento
    producto.save(update_fields=['stock_actual'])  # Guarda solo el campo stock_actual

    # Refresca la instancia del producto para obtener el valor del stock actualizado
    # ANTES de crear el registro de movimiento, para que stock_nuevo sea exacto.
    producto.refresh_from_db()
    stock_nuevo = producto.stock_actual

    MovimientoInventario.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=abs(cantidad_movimiento),  # Siempre se guarda la cantidad en positivo en el MovimientoInventario
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        motivo=motivo,
        registrado_por=usuario
    )

    return stock_anterior, stock_nuevo  # Retorna ambos para flexibilidad en las vistas


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
    # 3. Validación estricta
    cantidad_str = request.data.get('cantidad')
    if not cantidad_str:
        return Response({'error': 'La cantidad es requerida.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cantidad = int(cantidad_str)
    except ValueError:
        return Response({'error': 'La cantidad debe ser un número entero válido.'}, status=status.HTTP_400_BAD_REQUEST)
    if cantidad <= 0:
        return Response({'error': 'La cantidad debe ser un número entero positivo.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. Envuelve la lógica en transaction.atomic() y usa select_for_update()
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=pk)  # Bloquea el producto para evitar race conditions

            # 2. La función registrar_movimiento ahora usa F() internamente y retorna el stock anterior y nuevo
            stock_antes, stock_despues = registrar_movimiento(
                producto=producto,
                tipo='entrada',
                cantidad_movimiento=cantidad,  # Cantidad positiva para entrada
                usuario=request.user,
                motivo=request.data.get('motivo', 'Entrada de stock')
            )

        return Response({
            'message': f'Stock actualizado correctamente.',
            'stock_anterior': stock_antes,
            'stock_nuevo': stock_despues
        })
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Captura errores generales que puedan ocurrir dentro de la transacción.
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ajuste_stock(request, pk):
    """
    Ajuste manual del stock (pérdidas, correcciones, etc.).
    Body: { "stock_nuevo": 15, "motivo": "Corrección de inventario" }
    """
    # 3. Validación estricta
    stock_nuevo_str = request.data.get('stock_nuevo')
    if stock_nuevo_str is None:
        return Response({'error': 'El nuevo stock es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        stock_nuevo_target = int(stock_nuevo_str)
    except ValueError:
        return Response({'error': 'El nuevo stock debe ser un número entero válido.'}, status=status.HTTP_400_BAD_REQUEST)
    if stock_nuevo_target < 0:
        return Response({'error': 'El nuevo stock debe ser un número entero no negativo.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. Envuelve la lógica en transaction.atomic() y usa select_for_update()
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=pk)  # Bloquea el producto
            
            # Calcular la diferencia entre el stock deseado y el actual (bloqueado)
            diferencia = stock_nuevo_target - producto.stock_actual
            tipo = 'ajuste' if diferencia >= 0 else 'perdida'  # La lógica para tipo se mantiene

            # 2. La función registrar_movimiento ahora usa F() internamente y retorna el stock anterior y nuevo
            _, new_stock = registrar_movimiento(  # Se ignora old_stock si no se necesita en la respuesta
                producto=producto,
                tipo=tipo,
                cantidad_movimiento=diferencia,  # Puede ser positivo o negativo
                usuario=request.user,
                motivo=request.data.get('motivo', 'Ajuste manual')
            )

        return Response({
            'message': 'Stock ajustado correctamente.',
            'stock_nuevo': new_stock
        })
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Captura errores generales que puedan ocurrir dentro de la transacción.
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
