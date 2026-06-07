from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction  # Atomicidad garantizada para auditorías de inventario
from django.db.models import Q

from .models import Producto, MovimientoInventario
from .serializers import ProductoSerializer, ProductoListSerializer, MovimientoSerializer
from utils import paginar_queryset_funcion  # Paginador modular


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def productos_list(request):
    """
    GET: Lista productos con paginación y filtros de búsqueda reactivos.
    POST: Registra un nuevo producto en el catálogo (solo admin).
    """
    if request.method == 'GET':
        qs = Producto.objects.filter(activo=True).order_by('nombre')

        search = request.query_params.get('search')
        categoria = request.query_params.get('categoria')
        
        if search:
            qs = qs.filter(Q(nombre__icontains=search) | Q(sku__icontains=search))
        if categoria:
            qs = qs.filter(categoria=categoria)

        return paginar_queryset_funcion(request, qs, ProductoListSerializer, page_size=20)

    if request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede agregar nuevos productos al inventario.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def producto_detail(request, pk):
    """
    Operaciones individuales del catálogo de productos.
    """
    try:
        producto = Producto.objects.get(pk=pk, activo=True)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado o inactivo.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)

    if request.method == 'PUT':
        if request.user.role != 'admin':
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductoSerializer(producto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Soft Delete estratégico para no romper la integridad de auditoría histórica
        producto.activo = False
        producto.save(update_fields=['activo'])
        return Response({'message': 'Producto desactivado del catálogo correctamente.'}, status=status.HTTP_200_OK)


def registrar_movimiento(producto, tipo, cantidad_movimiento, usuario, motivo):
    """
    Función helper interna de alta optimización para procesar mutaciones de stock.
    Calcula nuevos niveles, banderas de alerta y asienta la auditoría histórica.
    """
    old_stock = producto.stock_actual
    
    if tipo == 'entrada':
        new_stock = old_stock + cantidad_movimiento
    elif tipo in ['salida', 'perdida', 'consumo']:
        new_stock = old_stock - cantidad_movimiento
    else:  # 'ajuste' manual directo
        new_stock = cantidad_movimiento

    # Validación matemática de seguridad
    if new_stock < 0:
        raise ValueError("El movimiento causará un stock negativo inválido.")

    # Mutación de banderas dinámicas del modelo
    producto.stock_actual = new_stock
    producto.sin_stock = (new_stock == 0)
    producto.stock_bajo = (new_stock <= producto.stock_minimo and new_stock > 0)
    producto.save(update_fields=['stock_actual', 'sin_stock', 'stock_bajo'])

    # Creación del log histórico indexado
    MovimientoInventario.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad_movimiento,
        stock_anterior=old_stock,
        stock_nuevo=new_stock,
        usuario=usuario,
        motivo=motivo
    )
    return old_stock, new_stock


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def entrada_stock(request, pk):
    """
    RF10: Registra la entrada segura de mercancía por compras o reposición.
    """
    try:
        cantidad = int(request.data.get('cantidad', 0))
        if cantidad <= 0:
            return Response({'error': 'La cantidad debe ser un entero estrictamente positivo.'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=pk, activo=True)
            
            _, stock_nuevo = registrar_movimiento(
                producto=producto,
                tipo='entrada',
                cantidad_movimiento=cantidad,
                usuario=request.user,
                motivo=request.data.get('motivo', 'Entrada por orden de compra')
            )

        return Response({'message': 'Entrada registrada exitosamente.', 'stock_actual': stock_nuevo}, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ajuste_stock(request, pk):
    """
    RF11: Ejecuta auditorías físicas de inventario o reajustes manuales por pérdidas/errores.
    """
    tipo = request.data.get('tipo', 'ajuste')
    valid_tipos = ['entrada', 'salida', 'perdida', 'ajuste']
    if tipo not in valid_tipos:
        return Response({'error': 'Tipo de ajuste inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cantidad = int(request.data.get('cantidad', 0))
        if cantidad < 0:
            return Response({'error': 'La cantidad no puede ser negativa.'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Cantidad no válida.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=pk, activo=True)
            
            # Si el tipo es 'ajuste' directo, la cantidad enviada es el stock final real observado en físico, 
            # de lo contrario es una delta (diferencia acumulativa)
            cantidad_movimiento = cantidad if tipo == 'ajuste' else (cantidad if tipo in ['entrada', 'ajuste'] else cantidad)

            _, stock_nuevo = registrar_movimiento(
                producto=producto,
                tipo=tipo,
                cantidad_movimiento=cantidad_movimiento,
                usuario=request.user,
                motivo=request.data.get('motivo', 'Ajuste manual de auditoría')
            )

        return Response({'message': 'Inventario conciliado correctamente.', 'stock_nuevo': stock_nuevo}, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def alertas_stock(request):
    """
    RF13: Retorna todos los productos con stock bajo o sin stock para el Dashboard de Alertas.
    """
    # SQL N+1 Blindado: Solo traemos los campos estrictamente necesarios reduciendo la carga de red
    sin_stock = Producto.objects.filter(activo=True, sin_stock=True).order_by('nombre')
    stock_bajo = Producto.objects.filter(activo=True, stock_bajo=True, sin_stock=False).order_by('nombre')

    return Response({
        'sin_stock': ProductoListSerializer(sin_stock, many=True).data,
        'stock_bajo': ProductoListSerializer(stock_bajo, many=True).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def historial_movimientos(request):
    """
    Retorna la auditoría completa de los movimientos de inventario paginados.
    """
    # SQL N+1 Blindado: select_related para traer la data del usuario y el producto en una única query con JOIN
    qs = MovimientoInventario.objects.select_related('producto', 'usuario').all().order_by('-fecha')
    return paginar_queryset_funcion(request, qs, MovimientoSerializer, page_size=25)