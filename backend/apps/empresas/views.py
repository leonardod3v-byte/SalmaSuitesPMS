from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Empresa
from .serializers import EmpresaSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lista_empresas(request):
    if request.method == 'GET':
        qs = Empresa.objects.filter(activo=True)

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search) |
                Q(rif__icontains=search)
            )

        serializer = EmpresaSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            empresa = serializer.save()
            return Response(EmpresaSerializer(empresa).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def detalle_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)

    if request.method == 'GET':
        serializer = EmpresaSerializer(empresa)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = EmpresaSerializer(empresa, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        empresa.activo = False
        empresa.save()
        return Response({'message': 'Empresa desactivada.'}, status=status.HTTP_200_OK)
