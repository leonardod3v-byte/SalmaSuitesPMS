from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from datetime import date, timedelta

from . import services
from .serializers import ResumenDiarioSerializer, IngresoPeriodoSerializer
from .pdf_services import generar_hoja_huesped, generar_registro_reservaciones_semanal, generar_cierre_caja_pdf
from apps.reservaciones.models import Reservacion

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

    if (fin - inicio).days > 366:
        return Response({'error': 'El rango máximo es de 366 días.'}, status=status.HTTP_400_BAD_REQUEST)

    metodo = request.query_params.get('metodo')
    data = services.obtener_ingresos_por_periodo(inicio, fin, metodo=metodo)
    serializer = IngresoPeriodoSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hoja_huesped_pdf(request, reserva_id):
    reserva = get_object_or_404(Reservacion, pk=reserva_id)
    buffer = generar_hoja_huesped(reserva)

    nombre_huesped = f"{reserva.id_huesped_titular.nombres}_{reserva.id_huesped_titular.apellidos}".replace(' ', '_')
    filename = f'Hoja_Registro_{nombre_huesped}_{date.today().isoformat()}.pdf'

    return FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def registro_reservaciones_pdf(request):
    fecha_str = request.query_params.get('fecha')
    if fecha_str:
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            fecha = date.today()
    else:
        fecha = date.today()

    buffer = generar_registro_reservaciones_semanal(fecha)
    filename = f'Registro_Semanal_{fecha.isoformat()}.pdf'

    return FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cierre_caja_pdf(request):
    fecha_str = request.query_params.get('fecha')
    if not fecha_str:
        return Response({'error': 'Parámetro fecha requerido (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    buffer = generar_cierre_caja_pdf(fecha)
    filename = f'Cierre_Caja_{fecha.isoformat()}.pdf'

    return FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
