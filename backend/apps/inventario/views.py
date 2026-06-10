from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import Producto
from .serializers import (
    ProductoSerializer,
    ProductoCreateUpdateSerializer,
    InventarioMovimientoSerializer,
    EntradaSerializer,
    AjusteSerializer
)
from . import services

# Productos -------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def productos_lista(request):
    if request.method == 'GET':
        categoria = request.query_params.get('categoria')
        estado = request.query_params.get('estado')
        productos = services.listar_productos(categoria=categoria, estado=estado)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede crear productos.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductoCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            producto = services.crear_producto(**serializer.validated_data)
            return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'GET':
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede editar productos.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductoCreateUpdateSerializer(producto, data=request.data, partial=True)
        if serializer.is_valid():
            producto = services.actualizar_producto(producto, serializer.validated_data)
            return Response(ProductoSerializer(producto).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede desactivar productos.'}, status=status.HTTP_403_FORBIDDEN)
        services.desactivar_producto(producto)
        return Response({'message': 'Producto desactivado.'}, status=status.HTTP_200_OK)


# Movimientos -----------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movimientos_lista(request):
    # Solo admin puede ver movimientos
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)
    producto_id = request.query_params.get('producto_id')
    movimientos = services.listar_movimientos(producto_id=producto_id)
    serializer = InventarioMovimientoSerializer(movimientos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_entrada_view(request):
    if request.user.role != 'admin':
        return Response({'error': 'Solo el administrador puede registrar entradas.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = EntradaSerializer(data=request.data)
    if serializer.is_valid():
        try:
            movimiento = services.registrar_entrada(
                producto_id=serializer.validated_data['producto_id'],
                cantidad=serializer.validated_data['cantidad'],
                motivo=serializer.validated_data['motivo'],
                usuario=request.user
            )
            return Response(InventarioMovimientoSerializer(movimiento).data, status=status.HTTP_201_CREATED)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_ajuste_view(request):
    if request.user.role != 'admin':
        return Response({'error': 'Solo el administrador puede realizar ajustes.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = AjusteSerializer(data=request.data)
    if serializer.is_valid():
        try:
            movimiento = services.registrar_ajuste(
                producto_id=serializer.validated_data['producto_id'],
                cantidad=serializer.validated_data['cantidad'],
                motivo=serializer.validated_data['motivo'],
                usuario=request.user
            )
            return Response(InventarioMovimientoSerializer(movimiento).data, status=status.HTTP_201_CREATED)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Alertas ---------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def productos_bajos_count(request):
    # Solo admin, pero si se llama desde el dashboard y el recepcionista no debería verlo, se protege
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)
    count = services.productos_bajos()
    return Response({'productos_bajos': count})