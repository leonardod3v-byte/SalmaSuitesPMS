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
    """
    from apps.guests.models import Huesped
    from apps.reservaciones.models import Reserva

    try:
        # SQL N+1 Blindado: prefetch_related para jalar consumos adjuntos de golpe
        huesped = Huesped.objects.prefetch_related('reservas__consumos').get(pk=huesped_id)
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    reserva_id = request.query_params.get('reserva')
    reserva = None
    if reserva_id:
        try:
            reserva = Reserva.objects.get(pk=reserva_id, huesped=huesped)
        except Reserva.DoesNotExist:
            return Response({'error': 'La reserva no pertenece al huésped especificado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Generación del reporte
    pdf_content = generar_pdf_consumos_huesped(huesped, reserva)
    
    # Registro asíncrono/lineal de auditoría
    ReporteGenerado.objects.create(
        tipo_reporte='consumos_huesped',
        formato='pdf',
        generado_por=request.user,
        parametros_usados=f"huesped_id={huesped_id};reserva_id={reserva_id or 'todas'}"
    )

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="consumos_huesped_{huesped_id}.pdf"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reporte_reservas_activas(request):
    """
    RF09: Descarga reporte de reservas activas (PDF o Excel).
    """
    formato = request.query_params.get('formato', 'pdf').lower()
    
    if formato == 'excel':
        content = generar_excel_reservas()
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = 'reservas_activas.xlsx'
    else:
        content = generar_pdf_reservas_activas()
        content_type = 'application/pdf'
        filename = 'reservas_activas.pdf'

    ReporteGenerado.objects.create(
        tipo_reporte='reservas_activas',
        formato=formato,
        generado_por=request.user,
        parametros_usados="ninguno"
    )

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reporte_ingresos(request):
    """
    RF09: Descarga reporte de ingresos financieros por rango de fechas (PDF o Excel).
    """
    fecha_inicio = request.query_params.get('fecha_inicio')
    fecha_fin = request.query_params.get('fecha_fin')
    formato = request.query_params.get('formato', 'pdf').lower()

    if not fecha_inicio or not fecha_fin:
        return Response({'error': 'Los parámetros fecha_inicio y fecha_fin son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

    if formato == 'excel':
        content = generar_excel_ingresos(fecha_inicio, fecha_fin)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = f'ingresos_{fecha_inicio}_al_{fecha_fin}.xlsx'
    else:
        content = generar_pdf_ingresos(fecha_inicio, fecha_fin)
        content_type = 'application/pdf'
        filename = f'ingresos_{fecha_inicio}_al_{fecha_fin}.pdf'

    ReporteGenerado.objects.create(
        tipo_reporte='ingresos',
        formato=formato,
        generado_por=request.user,
        parametros_usados=f"desde={fecha_inicio};hasta={fecha_fin}"
    )

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def historial_reportes(request):
    """
    RF14/Auditoría: Recupera el histórico indexado de reportes y balances del hotel.
    Soporta filtros por tipo de informe y optimiza la carga del operador responsable (N+1).
    """
    tipo_reporte = request.query_params.get('tipo')
    
    # Inicializamos la consulta base precargando el usuario del staff que ejecutó el reporte
    query = Reporte.objects.select_related('usuario').all().order_by('-fecha_creacion')

    # Aplicamos filtro dinámico si el frontend de SvelteKit lo solicita
    if tipo_reporte:
        query = query.filter(tipo=tipo_reporte)

    # Limitamos a los últimos 50 registros por paginación implícita de seguridad para no saturar la red
    reportes = query[:50]

    historial = []
    for rep in reportes:
        historial.append({
            'id': rep.id,
            'tipo': rep.tipo,           # 'cierre_caja', 'ocupacion_mensual', 'auditoria_fiscal'
            'nombre': rep.nombre if hasattr(rep, 'nombre') else f"Reporte #{rep.id}",
            'fecha_generado': rep.fecha_creacion.isoformat(),
            'datos_consolidados': rep.datos_json if hasattr(rep, 'datos_json') else {}, # Por si guardas el snapshot del JSON
            'archivo_url': rep.archivo.url if hasattr(rep, 'archivo') and rep.archivo else None, # Por si generas PDFs a Media/S3
            'generado_por': {
                'id': rep.usuario.id if rep.usuario else None,
                'username': rep.usuario.username if rep.usuario else 'Sistema',
                'role': rep.usuario.role if rep.usuario else 'Automático'
            }
        })

    return Response({
        'conteo_historial': len(historial),
        'tipo_filtrado': tipo_reporte or 'todos',
        'reportes': historial
    }, status=status.HTTP_200_OK)