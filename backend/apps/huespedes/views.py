from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from .models import Huesped
from .serializers import HuespedSerializer
from . import services

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lista_huespedes(request):
    if request.method == 'GET':
        qs = Huesped.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(numero_documento__icontains=search)
            )

        categoria = request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria=categoria)
            
        solo_alojados = request.query_params.get('solo_alojados')
        if solo_alojados == '1':
            from apps.reservaciones.models import Reservacion
            ids_alojados = Reservacion.objects.filter(
                estado='EnCurso'
            ).values_list('id_huesped_titular_id', flat=True)
            qs = qs.filter(id__in=ids_alojados)

        serializer = HuespedSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = HuespedSerializer(data=request.data)
        if serializer.is_valid():
            huesped = serializer.save()
            return Response(HuespedSerializer(huesped).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def detalle_huesped(request, pk):
    huesped = get_object_or_404(Huesped, pk=pk)

    if request.method == 'GET':
        serializer = HuespedSerializer(huesped)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = HuespedSerializer(huesped, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_disponibilidad(request, pk):
    try:
        disponible = services.validar_disponibilidad_huesped(pk)
        return Response({'disponible': disponible})
    except Huesped.DoesNotExist:
        return Response({'error': 'Huésped no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_huespedes_xls(request):
    """
    Exporta todos los huéspedes a un archivo Excel (.xlsx).
    """
    qs = Huesped.objects.all().order_by('apellidos', 'nombres')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Huéspedes'

    # Estilos
    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='2D1B14', end_color='2D1B14', fill_type='solid')
    header_align = Alignment(horizontal='center', vertical='center')
    cell_align = Alignment(vertical='center')
    thin_border = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC'),
    )

    # Título
    ws.merge_cells('A1:J1')
    title_cell = ws['A1']
    title_cell.value = 'REGISTRO GENERAL DE HUÉSPEDES - SALMA SUITE VIP'
    title_cell.font = Font(bold=True, size=14, color='B38E5D')
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30

    # Fecha de generación
    ws.merge_cells('A2:J2')
    fecha_cell = ws['A2']
    fecha_cell.value = f'Generado el: {date.today().strftime("%d/%m/%Y")}'
    fecha_cell.font = Font(italic=True, size=9, color='827066')
    fecha_cell.alignment = Alignment(horizontal='center')
    ws.row_dimensions[2].height = 20

    # Fila vacía
    ws.row_dimensions[3].height = 10

    # Encabezados
    headers = [
        'Nombres', 'Apellidos', 'Tipo Doc', 'Nº Documento',
        'Nacionalidad', 'Teléfono', 'Email', 'Tipo Cliente',
        'Categoría', 'Crédito Autorizado'
    ]

    header_row = 4
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    ws.row_dimensions[header_row].height = 25

    # Datos
    for row_idx, h in enumerate(qs, header_row + 1):
        credito = f'Sí (${h.limite_credito})' if h.credito_autorizado else 'No'
        
        datos_fila = [
            h.nombres,
            h.apellidos,
            h.tipo_documento,
            h.numero_documento,
            h.nacionalidad,
            h.telefono,
            h.email or '—',
            h.tipo_cliente_profesion,
            h.categoria,
            credito,
        ]

        for col_idx, valor in enumerate(datos_fila, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=valor)
            cell.alignment = cell_align
            cell.border = thin_border
            cell.font = Font(size=10)

        # Alternar colores de fila
        if row_idx % 2 == 0:
            for col_idx in range(1, 11):
                ws.cell(row=row_idx, column=col_idx).fill = PatternFill(
                    start_color='FAFAF5', end_color='FAFAF5', fill_type='solid'
                )

    # Anchos de columna
    col_widths = [20, 20, 10, 15, 15, 15, 25, 20, 12, 20]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    # Preparar respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="huespedes_{date.today().strftime("%Y-%m-%d")}.xlsx"'

    wb.save(response)
    return response