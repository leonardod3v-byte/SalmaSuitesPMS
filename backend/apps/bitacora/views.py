from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .serializers import ActividadLogSerializer, CierreCajaSerializer
from . import services

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_actividades(request):
    limit = int(request.query_params.get('limit', 20))
    actividades = services.listar_actividades(limit=limit)
    serializer = ActividadLogSerializer(actividades, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cierres_caja(request):
    if request.method == 'GET':
        cierres = services.listar_cierres()
        serializer = CierreCajaSerializer(cierres, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Solo admin puede cerrar caja (se valida en el permiso o en la vista)
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede cerrar caja.'}, status=status.HTTP_403_FORBIDDEN)
        fecha = request.data.get('fecha')
        if not fecha:
            return Response({'error': 'Fecha requerida (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cierre = services.realizar_cierre_caja(fecha, request.user)
            return Response(CierreCajaSerializer(cierre).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_cierre(request, fecha):
    from .models import CierreCaja
    try:
        cierre = CierreCaja.objects.get(fecha=fecha)
        serializer = CierreCajaSerializer(cierre)
        return Response(serializer.data)
    except CierreCaja.DoesNotExist:
        return Response({'error': 'No hay cierre para esa fecha.'}, status=status.HTTP_404_NOT_FOUND)