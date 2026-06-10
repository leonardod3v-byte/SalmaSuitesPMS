from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Huesped
from .serializers import HuespedSerializer
from . import services

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lista_huespedes(request):
    if request.method == 'GET':
        qs = Huesped.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(numero_documento__icontains=search)
            )

        categoria = request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria=categoria)
            
        solo_alojados = request.query_params.get('solo_alojados')
        if solo_alojados == '1':
            from apps.reservaciones.models import Reservacion
            ids_alojados = Reservacion.objects.filter(
                estado='EnCurso'
            ).values_list('id_huesped_titular_id', flat=True)
            qs = qs.filter(id__in=ids_alojados)

        serializer = HuespedSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = HuespedSerializer(data=request.data)
        if serializer.is_valid():
            huesped = serializer.save()
            return Response(HuespedSerializer(huesped).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def detalle_huesped(request, pk):
    huesped = get_object_or_404(Huesped, pk=pk)

    if request.method == 'GET':
        serializer = HuespedSerializer(huesped)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = HuespedSerializer(huesped, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_disponibilidad(request, pk):
    try:
        disponible = services.validar_disponibilidad_huesped(pk)
        return Response({'disponible': disponible})
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado'}, status=status.HTTP_404_NOT_FOUND)