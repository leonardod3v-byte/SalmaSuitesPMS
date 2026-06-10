from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Habitacion
from .serializers import HabitacionSerializer, CambioEstadoSerializer
from . import services


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def lista_habitaciones(request):
    if request.method == 'GET':
        estado = request.query_params.get('estado')
        habitaciones = services.listar_habitaciones(estado=estado)
        serializer = HabitacionSerializer(habitaciones, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        print("DATA:", request.data)
        print("FILES:", request.FILES)
        serializer = HabitacionSerializer(data=request.data)
        if serializer.is_valid():
            habitacion = serializer.save()
            return Response(HabitacionSerializer(habitacion).data, status=status.HTTP_201_CREATED)
        print("ERRORS:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def detalle_habitacion(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)

    if request.method == 'GET':
        serializer = HabitacionSerializer(habitacion)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = HabitacionSerializer(habitacion, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_estado_habitacion(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    serializer = CambioEstadoSerializer(data=request.data)
    if serializer.is_valid():
        estado = serializer.validated_data['estado']
        notas = serializer.validated_data.get('notas', '')
        es_emergencia = serializer.validated_data.get('es_emergencia', False)
        pasar_a_limpia = serializer.validated_data.get('pasar_a_limpia', False)

        try:
            if estado == 'Limpia':
                services.marcar_como_limpia(habitacion)
            elif estado in ['Mantenimiento', 'Obra']:
                if estado == 'Mantenimiento':
                    services.iniciar_mantenimiento(habitacion, notas, es_emergencia)
                else:
                    services.iniciar_obra(habitacion, notas, es_emergencia)
            elif estado in ['Sucia', 'Limpia'] and habitacion.estado in ['Mantenimiento', 'Obra']:
                services.finalizar_mantenimiento_obra(habitacion, pasar_a_limpia)
            else:
                services.cambiar_estado(habitacion, estado, notas=notas, es_emergencia=es_emergencia, pasar_a_limpia=pasar_a_limpia)

            return Response(HabitacionSerializer(habitacion).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_disponibilidad(request, pk):
    disponible = services.esta_disponible(pk)
    return Response({'disponible': disponible})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_disponibles_view(request):
    habitaciones = services.listar_disponibles()
    serializer = HabitacionSerializer(habitaciones, many=True)
    return Response(serializer.data)