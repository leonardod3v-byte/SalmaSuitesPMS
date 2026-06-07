from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Huesped
from .serializers import HuespedSerializer, HuespedListSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def huespedes_list(request):
    """
    GET: Lista todos los huéspedes.
        Soporta búsqueda por nombre, apellido o documento:
        /api/huespedes/?search=garcia
        /api/huespedes/?vip=true
    POST: Registra un nuevo huésped.
    """
    if request.method == 'GET':
        qs = Huesped.objects.all()

        # Búsqueda general
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(numero_documento__icontains=search) |
                Q(email__icontains=search)
            )

        # Filtro VIP
        vip = request.query_params.get('vip')
        if vip == 'true':
            qs = qs.filter(es_vip=True)

        serializer = HuespedListSerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = HuespedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def huesped_detail(request, pk):
    """
    GET: Detalle completo del huésped incluyendo su historial de reservas.
    PUT: Actualizar datos del huésped.
    DELETE: Eliminar huésped (solo admin).
    """
    try:
        huesped = Huesped.objects.get(pk=pk)
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado.'}, status=404)

    if request.method == 'GET':
        serializer = HuespedSerializer(huesped)

        # Traer historial de reservas si la app reservaciones existe
        historial = []
        try:
            from apps.reservaciones.models import Reserva
            from apps.reservaciones.serializers import ReservaListSerializer
            reservas = Reserva.objects.filter(huesped=huesped).order_by('-created_at')[:10]
            historial = ReservaListSerializer(reservas, many=True).data
        except Exception:
            pass

        return Response({
            'huesped': serializer.data,
            'historial_reservas': historial
        })

    if request.method == 'PUT':
        serializer = HuespedSerializer(huesped, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar huéspedes.'}, status=403)
        huesped.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def buscar_huesped_por_documento(request):
    """
    Busca un huésped específico por su documento.
    Útil al hacer check-in para autocompletar datos.
    Ej: /api/huespedes/buscar/?documento=V-12345678
    """
    documento = request.query_params.get('documento')
    if not documento:
        return Response({'error': 'Parámetro documento requerido.'}, status=400)

    # Separar tipo y número si viene con guión (V-12345678)
    partes = documento.upper().replace(' ', '').split('-')
    try:
        if len(partes) == 2:
            huesped = Huesped.objects.get(
                tipo_documento=partes[0],
                numero_documento=partes[1]
            )
        else:
            huesped = Huesped.objects.get(numero_documento=partes[0])
    except Huesped.DoesNotExist:
        return Response({'encontrado': False}, status=404)

    serializer = HuespedSerializer(huesped)
    return Response({'encontrado': True, 'huesped': serializer.data})