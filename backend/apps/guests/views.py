from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Huesped
from .serializers import HuespedSerializer, HuespedListSerializer
from utils import paginar_queryset_funcion

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def huespedes_list(request):
    """
    GET: Lista todos los huéspedes con paginación integrada y búsqueda indexada.
    POST: Registra un nuevo huésped.
    """
    if request.method == 'GET':
        qs = Huesped.objects.all().order_by('-id')

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(numero_documento__icontains=search)
            )

        return paginar_queryset_funcion(request, qs, HuespedListSerializer, page_size=20)

    if request.method == 'POST':
        serializer = HuespedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def huespedes_detail(request, pk):
    """
    Operaciones individuales sobre huéspedes.
    """
    try:
        huesped = Huesped.objects.prefetch_related('reservas').get(pk=pk)
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = HuespedSerializer(huesped)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = HuespedSerializer(huesped, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar registros.'}, status=status.HTTP_403_FORBIDDEN)
        huesped.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def huesped_detail(request, pk):
    """
    Controlador para recuperar, actualizar o eliminar un huésped específico.
    """
    try:
        # Si es GET, pre-cargamos sus reservaciones para optimizar posibles sub-vistas
        if request.method == 'GET':
            huesped = Huesped.objects.prefetch_related('reservas').get(pk=pk)
            serializer = HuespedSerializer(huesped)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            huesped = Huesped.objects.get(pk=pk)
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = HuespedSerializer(huesped, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar registros de huéspedes.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validación de seguridad: No eliminar si tiene reservas activas o deudas
        tiene_reservas_activas = huesped.reservas.filter(estado__in=['sin_pagar', 'confirmada', 'check_in']).exists()
        if tiene_reservas_activas:
            return Response({'error': 'No se puede eliminar un huésped con reservaciones activas o pendientes.'}, status=status.HTTP_400_BAD_REQUEST)
        
        huesped.delete()
        return Response({'message': 'Huésped eliminado exitosamente.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def buscar_huesped_por_documento(request):
    """
    Consulta rápida y directa de un huésped mediante su documento de identidad.
    Útil para autocompletar formularios de reserva en el frontend sin paginación masiva.
    """
    documento = request.query_params.get('documento') or request.query_params.get('search')
    
    if not documento:
        return Response(
            {'error': 'El parámetro "documento" es obligatorio para realizar la búsqueda.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Búsqueda exacta indexada por documento
        huesped = Huesped.objects.get(documento=documento)
        serializer = HuespedSerializer(huesped)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Huesped.DoesNotExist:
        return Response(
            {'error': f'No se encontró ningún huésped registrado con el documento: {documento}'}, 
            status=status.HTTP_404_NOT_FOUND
        )