from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import TipoHabitacion, Habitacion, HistorialEstadoHabitacion
from .serializers import TipoHabitacionSerializer, HabitacionSerializer, HistorialSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitaciones_list(request):
    """
    GET: Lista todas las habitaciones con filtros opcionales por estado o piso.
    POST: Crea una nueva habitación (solo admin).
    """
    if request.method == 'GET':
        qs = Habitacion.objects.select_related('tipo').all()

        # Filtros opcionales por query params: /api/habitaciones/?estado=libre&piso=2
        estado = request.query_params.get('estado')
        piso = request.query_params.get('piso')
        if estado:
            qs = qs.filter(estado=estado)
        if piso:
            qs = qs.filter(piso=piso)

        serializer = HabitacionSerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede crear habitaciones.'}, status=403)

        serializer = HabitacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitacion_detail(request, pk):
    """
    GET: Detalle de una habitación con su historial.
    PUT: Editar datos de la habitación.
    DELETE: Eliminar habitación (solo admin).
    """
    try:
        habitacion = Habitacion.objects.select_related('tipo').get(pk=pk)
    except Habitacion.DoesNotExist:
        return Response({'error': 'Habitación no encontrada.'}, status=404)

    if request.method == 'GET':
        serializer = HabitacionSerializer(habitacion)
        historial = HistorialEstadoHabitacion.objects.filter(habitacion=habitacion)[:10]
        historial_serializer = HistorialSerializer(historial, many=True)
        return Response({
            'habitacion': serializer.data,
            'historial': historial_serializer.data
        })

    if request.method in ['PUT', 'PATCH']:
        estado_anterior = habitacion.estado
        serializer = HabitacionSerializer(habitacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Si el estado cambió, registrar en el historial automáticamente
            nuevo_estado = serializer.validated_data.get('estado')
            if nuevo_estado and nuevo_estado != estado_anterior:
                HistorialEstadoHabitacion.objects.create(
                    habitacion=habitacion,
                    estado_anterior=estado_anterior,
                    estado_nuevo=nuevo_estado,
                    cambiado_por=request.user,
                    nota=request.data.get('nota', '')
                )

            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar habitaciones.'}, status=403)
        habitacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def tipos_habitacion_list(request):
    """
    Lista todos los tipos de habitación disponibles.
    """
    tipos = TipoHabitacion.objects.all()
    serializer = TipoHabitacionSerializer(tipos, many=True)
    return Response(serializer.data)