from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from . import services

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpis(request):
    data = services.obtener_kpis()
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ocupacion_semanal(request):
    data = services.obtener_ocupacion_semanal()
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proximos_checkouts(request):
    data = services.proximos_checkouts()
    return Response(data)
