import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


# ── Colores del hotel ──────────────────────────────────────────────────────────
DORADO = colors.HexColor('#C9A227')
NEGRO = colors.HexColor('#0A0A0A')
GRIS_CLARO = colors.HexColor('#F5F5F5')
GRIS_MEDIO = colors.HexColor('#A3A3A3')


def get_estilos():
    """Estilos base para los PDFs."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='HotelTitulo',
        fontSize=20,
        textColor=DORADO,
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='HotelSubtitulo',
        fontSize=11,
        textColor=GRIS_MEDIO,
        alignment=TA_CENTER,
        spaceAfter=2,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='HotelSeccion',
        fontSize=12,
        textColor=NEGRO,
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='HotelNormal',
        fontSize=9,
        textColor=NEGRO,
        fontName='Helvetica'
    ))

    return styles


def tabla_estilo_base(tiene_header=True):
    """Estilo base reutilizable para todas las tablas de los PDFs."""
    estilo = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_MEDIO),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]

    if tiene_header:
        estilo += [
            ('BACKGROUND', (0, 0), (-1, 0), NEGRO),
            ('TEXTCOLOR', (0, 0), (-1, 0), DORADO),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ]

    return TableStyle(estilo)


def header_pdf(elements, styles, titulo, subtitulo=''):
    """Agrega el encabezado estándar del hotel a cualquier PDF."""
    elements.append(Paragraph('Salma Suite VIP', styles['HotelTitulo']))
    elements.append(Paragraph('Sistema de Gestión Hotelera', styles['HotelSubtitulo']))

    if subtitulo:
        elements.append(Paragraph(subtitulo, styles['HotelSubtitulo']))

    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width='100%', thickness=1, color=DORADO))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(titulo, styles['HotelSeccion']))
    elements.append(Spacer(1, 8))


# ── PDF: Consumos por huésped ──────────────────────────────────────────────────

def generar_pdf_consumos_huesped(huesped, reserva=None):
    """
    RF09: Genera PDF con todos los consumos de un huésped.
    Si se pasa una reserva específica, filtra solo esa reserva.
    """
    from apps.reservaciones.models import Consumo

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = get_estilos()
    elements = []

    header_pdf(
        elements, styles,
        titulo=f'Consumos - {huesped.nombre_completo}',
        subtitulo=f'Documento: {huesped.documento_formateado} | Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    )

    # Datos del huésped
    info_data = [
        ['Huésped', huesped.nombre_completo, 'Documento', huesped.documento_formateado],
        ['Teléfono', huesped.telefono or 'N/A', 'Email', huesped.email or 'N/A'],
        ['VIP', 'Sí' if huesped.es_vip else 'No', '', ''],
    ]
    tabla_info = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    tabla_info.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, -1), GRIS_CLARO),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_MEDIO),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(tabla_info)
    elements.append(Spacer(1, 12))

    # Consumos
    qs = Consumo.objects.filter(reserva__huesped=huesped)
    if reserva:
        qs = qs.filter(reserva=reserva)

    elementos_tabla = [['Fecha', 'Producto', 'Cant.', 'Precio Unit.', 'Total', 'Nota']]
    total_general = 0

    for consumo in qs:
        total = consumo.total
        total_general += total
        elementos_tabla.append([
            consumo.fecha_consumo.strftime('%d/%m/%Y %H:%M'),
            consumo.producto,
            str(consumo.cantidad),
            f'${consumo.precio_unitario:.2f}',
            f'${total:.2f}',
            consumo.nota or '-'
        ])

    elementos_tabla.append(['', '', '', '', '', ''])
    elementos_tabla.append(['', '', '', 'TOTAL GENERAL', f'${total_general:.2f}', ''])

    tabla = Table(elementos_tabla, colWidths=[1.2*inch, 2*inch, 0.5*inch, 1*inch, 0.8*inch, 1.5*inch])
    tabla.setStyle(tabla_estilo_base())
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (-3, -1), (-1, -1), DORADO),
        ('TEXTCOLOR', (-3, -1), (-1, -1), NEGRO),
        ('FONTNAME', (-3, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(tabla)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ── PDF: Reservas activas ──────────────────────────────────────────────────────

def generar_pdf_reservas_activas():
    """
    RF09: PDF con todas las reservas activas.
    Incluye íconos de estado como texto: ✓ Pagada, ⏳ Pendiente, ✗ No-Show.
    """
    from apps.reservaciones.models import Reserva

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    styles = get_estilos()
    elements = []

    header_pdf(
        elements, styles,
        titulo='Reservas Activas',
        subtitulo=f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    )

    ICONOS_ESTADO = {
        'pagada': '[OK] Pagada',
        'confirmada': '[..] Confirmada',
        'pendiente': '[??] Pendiente',
        'sin_pagar': '[$$] Sin Pagar',
        'cancelada': '[XX] Cancelada',
        'no_show': '[--] No-Show',
    }

    reservas = Reserva.objects.select_related(
        'huesped', 'habitacion'
    ).filter(
        estado__in=['pendiente', 'sin_pagar', 'confirmada', 'pagada']
    ).order_by('fecha_entrada')

    datos = [['#', 'Huésped', 'Documento', 'Hab.', 'Entrada', 'Salida', 'Noches', 'Total', 'Pagado', 'Estado']]

    for r in reservas:
        datos.append([
            str(r.id),
            r.huesped.nombre_completo[:25],
            r.huesped.documento_formateado,
            f'H-{r.habitacion.numero}',
            r.fecha_entrada.strftime('%d/%m/%Y'),
            r.fecha_salida.strftime('%d/%m/%Y'),
            str(r.noches),
            f'${r.monto_total:.2f}',
            f'${r.monto_pagado:.2f}',
            ICONOS_ESTADO.get(r.estado, r.estado),
        ])

    tabla = Table(datos, colWidths=[
        0.4*inch, 2*inch, 1.3*inch, 0.5*inch,
        1*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch, 1.1*inch
    ])
    tabla.setStyle(tabla_estilo_base())
    elements.append(tabla)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ── PDF: Ingresos por período ──────────────────────────────────────────────────

def generar_pdf_ingresos(fecha_inicio, fecha_fin):
    """
    RF09: PDF de ingresos en un rango de fechas.
    Muestra desglose por método de pago y total general.
    """
    from apps.pagos.models import Pago
    from django.db.models import Sum

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = get_estilos()
    elements = []

    header_pdf(
        elements, styles,
        titulo=f'Ingresos: {fecha_inicio} al {fecha_fin}',
        subtitulo=f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    )

    pagos = Pago.objects.filter(fecha__date__range=[fecha_inicio, fecha_fin])

    # Desglose por método
    metodos = [m[0] for m in Pago.METODOS_PAGO]
    datos_metodos = [['Método de Pago', 'Total']]
    total_general = 0

    for metodo in metodos:
        total = pagos.filter(metodo=metodo).aggregate(
            t=Sum('monto')
        )['t'] or 0
        if total > 0:
            datos_metodos.append([metodo.replace('_', ' ').title(), f'${total:.2f}'])
            total_general += float(total)

    datos_metodos.append(['TOTAL GENERAL', f'${total_general:.2f}'])

    tabla_metodos = Table(datos_metodos, colWidths=[3*inch, 2*inch])
    tabla_metodos.setStyle(tabla_estilo_base())
    tabla_metodos.setStyle(TableStyle([
        ('BACKGROUND', (0, -1), (-1, -1), DORADO),
        ('TEXTCOLOR', (0, -1), (-1, -1), NEGRO),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(tabla_metodos)
    elements.append(Spacer(1, 16))

    # Detalle de pagos
    elements.append(Paragraph('Detalle de Pagos', styles['HotelSeccion']))
    elements.append(Spacer(1, 6))

    datos_detalle = [['Fecha', 'Huésped', 'Hab.', 'Concepto', 'Método', 'Monto']]
    for pago in pagos.select_related('reserva__huesped', 'reserva__habitacion').order_by('fecha'):
        datos_detalle.append([
            pago.fecha.strftime('%d/%m/%Y'),
            pago.reserva.huesped.nombre_completo[:20],
            f'H-{pago.reserva.habitacion.numero}',
            pago.concepto,
            pago.metodo.replace('_', ' ').title(),
            f'${pago.monto:.2f}',
        ])

    tabla_detalle = Table(datos_detalle, colWidths=[1*inch, 2*inch, 0.6*inch, 1*inch, 1.2*inch, 0.8*inch])
    tabla_detalle.setStyle(tabla_estilo_base())
    elements.append(tabla_detalle)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ── Excel: Exportar cualquier reporte ─────────────────────────────────────────

def generar_excel_reservas():
    """RF14: Exporta todas las reservas a Excel."""
    from apps.reservaciones.models import Reserva

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Reservas'

    # Estilos
    header_fill = PatternFill(start_color='0A0A0A', end_color='0A0A0A', fill_type='solid')
    header_font = Font(color='C9A227', bold=True, size=10)
    border = Border(
        left=Side(style='thin', color='A3A3A3'),
        right=Side(style='thin', color='A3A3A3'),
        top=Side(style='thin', color='A3A3A3'),
        bottom=Side(style='thin', color='A3A3A3')
    )

    headers = [
        'ID', 'Huésped', 'Documento', 'Habitación',
        'Entrada', 'Salida', 'Noches', 'Estado',
        'Método Pago', 'Total', 'Pagado', 'Saldo'
    ]

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border

    # Datos
    reservas = Reserva.objects.select_related(
        'huesped', 'habitacion'
    ).all().order_by('-created_at')

    fill_par = PatternFill(start_color='F5F5F5', end_color='F5F5F5', fill_type='solid')

    for row_idx, r in enumerate(reservas, 2):
        fill = fill_par if row_idx % 2 == 0 else PatternFill()
        row_data = [
            r.id,
            r.huesped.nombre_completo,
            r.huesped.documento_formateado,
            f'H-{r.habitacion.numero}',
            r.fecha_entrada.strftime('%d/%m/%Y'),
            r.fecha_salida.strftime('%d/%m/%Y'),
            r.noches,
            r.estado,
            r.metodo_pago or 'N/A',
            float(r.monto_total),
            float(r.monto_pagado),
            float(r.saldo_pendiente),
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            cell.border = border
            cell.fill = fill

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_length + 4, 30)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def generar_excel_ingresos(fecha_inicio, fecha_fin):
    """RF14: Exporta ingresos de un período a Excel."""
    from apps.pagos.models import Pago

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'Ingresos {fecha_inicio} - {fecha_fin}'

    header_fill = PatternFill(start_color='0A0A0A', end_color='0A0A0A', fill_type='solid')
    header_font = Font(color='C9A227', bold=True, size=10)
    border = Border(
        left=Side(style='thin', color='A3A3A3'),
        right=Side(style='thin', color='A3A3A3'),
        top=Side(style='thin', color='A3A3A3'),
        bottom=Side(style='thin', color='A3A3A3')
    )

    headers = ['Fecha', 'Huésped', 'Habitación', 'Concepto', 'Método', 'Referencia', 'Monto']

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border

    pagos = Pago.objects.filter(
        fecha__date__range=[fecha_inicio, fecha_fin]
    ).select_related('reserva__huesped', 'reserva__habitacion').order_by('fecha')

    fill_par = PatternFill(start_color='F5F5F5', end_color='F5F5F5', fill_type='solid')
    total = 0

    for row_idx, pago in enumerate(pagos, 2):
        fill = fill_par if row_idx % 2 == 0 else PatternFill()
        total += float(pago.monto)
        row_data = [
            pago.fecha.strftime('%d/%m/%Y %H:%M'),
            pago.reserva.huesped.nombre_completo,
            f'H-{pago.reserva.habitacion.numero}',
            pago.concepto,
            pago.metodo.replace('_', ' ').title(),
            pago.referencia or '-',
            float(pago.monto),
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            cell.border = border
            cell.fill = fill

    # Fila de total
    fila_total = len(pagos) + 2
    ws.cell(row=fila_total, column=6, value='TOTAL').font = Font(bold=True)
    total_cell = ws.cell(row=fila_total, column=7, value=total)
    total_cell.font = Font(bold=True, color='C9A227')
    total_cell.fill = PatternFill(start_color='0A0A0A', end_color='0A0A0A', fill_type='solid')

    for col in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_length + 4, 30)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer