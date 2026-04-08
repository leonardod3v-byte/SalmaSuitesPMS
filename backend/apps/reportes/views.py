from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import ReporteGenerado
from .utils import (
    generar_pdf_consumos_huesped,
    generar_pdf_reservas_activas,
    generar_pdf_ingresos,
    generar_excel_reservas,
    generar_excel_ingresos,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reporte_consumos_huesped(request, huesped_id):
    """
    RF09: Genera y descarga PDF de consumos de un huésped.
    Parámetro opcional: ?reserva=5 para filtrar por reserva específica.
    Parámetro de formato: ?formato=excel
    """
    from apps.guests.models import Huesped
    from apps.reservaciones.models import Reserva

    try:
        huesped = Huesped.objects.get(pk=huesped_id)
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado.'}, status=404)

    reserva = None
    reserva_id = request.query_params.get('reserva')
    if reserva_id:
        try:
            reserva = Reserva.objects.get(pk=reserva_id)
        except Reserva.DoesNotExist:
            pass

    buffer = generar_pdf_consumos_huesped(huesped, reserva)

    nombre = f'consumos_{huesped.numero_documento}.pdf'
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'

    ReporteGenerado.objects.create(
        tipo='consumos_huesped',
        formato='pdf',
        nombre_archivo=nombre,
        generado_por=request.user,
        parametros={'huesped_id': huesped_id, 'reserva_id': reserva_id}
    )

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reporte_reservas_activas(request):
    """
    RF09: Genera PDF o Excel con todas las reservas activas.
    Parámetro: ?formato=pdf o ?formato=excel
    """
    formato = request.query_params.get('formato', 'pdf')

    if formato == 'excel':
        buffer = generar_excel_reservas()
        nombre = 'reservas_activas.xlsx'
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        buffer = generar_pdf_reservas_activas()
        nombre = 'reservas_activas.pdf'
        content_type = 'application/pdf'

    response = HttpResponse(buffer, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'

    ReporteGenerado.objects.create(
        tipo='reservas_activas',
        formato=formato,
        nombre_archivo=nombre,
        generado_por=request.user
    )

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reporte_ingresos(request):
    """
    RF09/RF14: Genera reporte de ingresos por período.
    Parámetros requeridos: ?fecha_inicio=2026-03-01&fecha_fin=2026-03-14
    Parámetro opcional: ?formato=excel
    """
    fecha_inicio = request.query_params.get('fecha_inicio')
    fecha_fin = request.query_params.get('fecha_fin')
    formato = request.query_params.get('formato', 'pdf')

    if not fecha_inicio or not fecha_fin:
        return Response(
            {'error': 'fecha_inicio y fecha_fin son requeridos. Formato: YYYY-MM-DD'},
            status=400
        )

    if formato == 'excel':
        buffer = generar_excel_ingresos(fecha_inicio, fecha_fin)
        nombre = f'ingresos_{fecha_inicio}_{fecha_fin}.xlsx'
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        buffer = generar_pdf_ingresos(fecha_inicio, fecha_fin)
        nombre = f'ingresos_{fecha_inicio}_{fecha_fin}.pdf'
        content_type = 'application/pdf'

    response = HttpResponse(buffer, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'

    ReporteGenerado.objects.create(
        tipo='ingresos_periodo',
        formato=formato,
        nombre_archivo=nombre,
        generado_por=request.user,
        parametros={'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
    )

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def historial_reportes(request):
    """Lista los últimos reportes generados."""
    if request.user.role == 'admin':
        reportes = ReporteGenerado.objects.select_related('generado_por').all()[:50]
    else:
        reportes = ReporteGenerado.objects.filter(generado_por=request.user)[:20]

    data = [{
        'id': r.id,
        'tipo': r.tipo,
        'formato': r.formato,
        'nombre_archivo': r.nombre_archivo,
        'generado_por': r.generado_por.username,
        'created_at': r.created_at,
    } for r in reportes]

    return Response(data)