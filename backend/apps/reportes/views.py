from datetime import date, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import services
from .serializers import ResumenDiarioSerializer, IngresoPeriodoSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_diario(request):
    fecha_str = request.query_params.get('fecha')
    if not fecha_str:
        return Response({'error': 'Parámetro fecha requerido (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    # Límite de días para recepción
    if request.user.role == 'recepcionista':
        hoy = date.today()
        limite = hoy - timedelta(days=7)
        if fecha < limite or fecha > hoy:
            return Response({'error': 'Solo puedes consultar los últimos 7 días.'}, status=status.HTTP_403_FORBIDDEN)

    data = services.obtener_detalle_diario(fecha)
    serializer = ResumenDiarioSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ingresos_periodo(request):
    inicio_str = request.query_params.get('inicio')
    fin_str = request.query_params.get('fin')
    if not inicio_str or not fin_str:
        return Response({'error': 'Parámetros inicio y fin requeridos (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        inicio = date.fromisoformat(inicio_str)
        fin = date.fromisoformat(fin_str)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    if inicio > fin:
        return Response({'error': 'La fecha de inicio debe ser anterior o igual a la de fin.'}, status=status.HTTP_400_BAD_REQUEST)

    # Limitar a 366 días máximo para no sobrecargar
    if (fin - inicio).days > 366:
        return Response({'error': 'El rango máximo es de 366 días.'}, status=status.HTTP_400_BAD_REQUEST)

    metodo = request.query_params.get('metodo')  # opcional: Efectivo, Tarjeta, PagoMovil
    data = services.obtener_ingresos_por_periodo(inicio, fin, metodo=metodo)
    serializer = IngresoPeriodoSerializer(data, many=True)
    return Response(serializer.data)