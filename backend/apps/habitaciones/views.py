from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import TipoHabitacion, Habitacion, HistorialEstadoHabitacion
from .serializers import TipoHabitacionSerializer, HabitacionSerializer, HistorialSerializer
from utils import paginar_queryset_funcion


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitaciones_list(request):
    """
    GET: Lista todas las habitaciones con filtros y paginación optimizada.
    POST: Crea una nueva habitación (solo admin).
    """
    if request.method == 'GET':
        # SQL N+1 Blindado: select_related para traer los tipos en un solo JOIN
        qs = Habitacion.objects.select_related('tipo').all().order_by('numero')

        estado = request.query_params.get('estado')
        piso = request.query_params.get('piso')
        if estado:
            qs = qs.filter(estado=estado)
        if piso:
            qs = qs.filter(piso=piso)

        return paginar_queryset_funcion(request, qs, HabitacionSerializer, page_size=30)

    if request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede registrar nuevas habitaciones.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = HabitacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitacion_detail(request, pk):
    """
    Operaciones individuales sobre una habitación específica.
    """
    try:
        habitacion = Habitacion.objects.select_related('tipo').get(pk=pk)
    except Habitacion.DoesNotExist:
        return Response({'error': 'Habitación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = HabitacionSerializer(habitacion)
        return Response(serializer.data)

    if request.method == 'PUT':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede modificar la configuración de las habitaciones.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = HabitacionSerializer(habitacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar habitaciones del sistema.'}, status=status.HTTP_403_FORBIDDEN)
        habitacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cambiar_estado_limpieza(request, pk):
    """
    RF12: Cambia el estado de limpieza de una habitación de forma atómica y concurrente.
    """
    nuevo_estado = request.data.get('estado')
    valid_estados = [e[0] for e in Habitacion.ESTADOS_HABITACION]

    if not nuevo_estado or nuevo_estado not in valid_estados:
        return Response({'error': f'Estado inválido. Opciones: {", ".join(valid_estados)}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # Candado seguro a nivel de BD para evitar que dos hilos pisen el estado simultáneamente
            habitacion = Habitacion.objects.select_for_update().get(pk=pk)
            
            estado_anterior = habitacion.estado
            habitacion.estado = nuevo_estado
            habitacion.save(update_fields=['estado'])  # Optimización SQL: Actualiza solo la columna modificada

            # Registrar en el historial de auditoría
            HistorialEstadoHabitacion.objects.create(
                habitacion=habitacion,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario=request.user,
                motivo=request.data.get('motivo', 'Cambio operativo de rutina')
            )

        return Response({
            'message': f'Habitación {habitacion.numero} cambiada exitosamente de {estado_anterior} a {nuevo_estado}.'
        }, status=status.HTTP_200_OK)

    except Habitacion.DoesNotExist:
        return Response({'error': 'Habitación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def tipos_habitacion_list(request):
    """
    Controlador para los tipos/categorías de habitaciones.
    """
    if request.method == 'GET':
        tipos = TipoHabitacion.objects.all().order_by('nombre')
        serializer = TipoHabitacionSerializer(tipos, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TipoHabitacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)