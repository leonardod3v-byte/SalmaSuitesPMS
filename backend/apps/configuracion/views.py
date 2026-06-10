from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import services
from .serializers import (
    ConfiguracionSerializer,
    ColoresTipoClienteSerializer,
    ColoresEstadoHabitacionSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def configuracion_general(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        config = services.obtener_configuracion()
        return Response(config)

    elif request.method == 'POST':
        for clave, valor in request.data.items():
            services.guardar_configuracion(clave, valor)
        return Response({'message': 'Configuración actualizada.'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def colores_tipo_cliente(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        colores = services.listar_colores_tipo_cliente()
        serializer = ColoresTipoClienteSerializer(colores, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ColoresTipoClienteSerializer(data=request.data)
        if serializer.is_valid():
            services.guardar_color_tipo_cliente(
                serializer.validated_data['tipo_cliente_profesion'],
                serializer.validated_data['color']
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def colores_estado_habitacion(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        colores = services.listar_colores_estado_habitacion()
        serializer = ColoresEstadoHabitacionSerializer(colores, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ColoresEstadoHabitacionSerializer(data=request.data)
        if serializer.is_valid():
            services.guardar_color_estado_habitacion(
                serializer.validated_data['estado'],
                serializer.validated_data['color']
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)