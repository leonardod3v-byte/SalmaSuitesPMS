from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Configuracion, Ocupacion
from .serializers import ConfiguracionSerializer, OcupacionSerializer
from . import services


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


class OcupacionViewSet(viewsets.ModelViewSet):
    queryset = Ocupacion.objects.all().order_by('nombre')
    serializer_class = OcupacionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
