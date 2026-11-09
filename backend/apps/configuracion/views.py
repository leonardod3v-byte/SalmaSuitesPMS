from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Ocupacion
from .serializers import OcupacionSerializer


class OcupacionViewSet(viewsets.ModelViewSet):
    queryset = Ocupacion.objects.all().order_by('nombre')
    serializer_class = OcupacionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
