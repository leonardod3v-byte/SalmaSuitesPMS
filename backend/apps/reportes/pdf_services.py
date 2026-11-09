from io import BytesIO
from datetime import date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum
import os


# ─── Datos fijos del hotel ──────────────────────────────────
HOTEL_NOMBRE = "Hotel Salma Suites VIP, C.A."
HOTEL_RIF = "J-400896975"
HOTEL_RTN = "12220"


def _get_logo_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logo_path = os.path.join(base_dir, 'assets', 'logo.png')
    if os.path.exists(logo_path):
        return logo_path
    return None


# --- BLOQUE DE ENCABEZADO ---
def _construir_encabezado(titulo_es, titulo_en, subtitulo_extra="", ancho_util=None):
    styles = getSampleStyleSheet()
    style_title_main = ParagraphStyle('TitleMain', parent=styles['Title'], fontSize=11, leading=13, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    style_subtitle_main = ParagraphStyle('SubTitleMain', parent=styles['Normal'], fontSize=8, leading=10, alignment=TA_RIGHT)
    style_small_left = ParagraphStyle('SmallLeft', parent=styles['Normal'], fontSize=7, leading=9, alignment=TA_LEFT)
    style_small_bold = ParagraphStyle('SmallBold', parent=styles['Normal'], fontSize=7, leading=9, alignment=TA_LEFT, fontName='Helvetica-Bold')

    logo_path = _get_logo_path()
    logo_img = Image(logo_path, width=30 * mm, height=15 * mm) if logo_path else Paragraph("", style_small_left)

    bloque_izq = [
        logo_img,
        Spacer(1, 1 * mm),
        Paragraph(f"<b>RAZÓN SOCIAL: {HOTEL_NOMBRE}</b>", style_small_left),
        Paragraph(f"<b>RIF:</b> {HOTEL_RIF} / <b>RTN:</b> {HOTEL_RTN}", style_small_bold),
    ]

    bloque_der = [
        Spacer(1, 5 * mm),
        Paragraph(titulo_es, style_title_main),
        Paragraph(f"<i>{titulo_en}</i>", style_subtitle_main),
    ]
    if subtitulo_extra:
        bloque_der.append(Paragraph(subtitulo_extra, style_subtitle_main))

    if ancho_util:
        col_widths = [ancho_util * 0.50, ancho_util * 0.50]
    else:
        col_widths = ['50%', '50%']

    header_table = Table([[bloque_izq, bloque_der]], colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return header_table, style_small_left


# --- HOJA DE REGISTRO DE HUÉSPED ---
def generar_hoja_huesped(reserva):
    buffer = BytesIO()
    page_width, page_height = 279 * mm, 216 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    ancho_util = page_width - 30 * mm
    elements = []
    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle('NormalPDF', parent=styles['Normal'], fontSize=7, leading=9)
    style_small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=6, leading=8)
    style_small_bold = ParagraphStyle('SmallBold', parent=styles['Normal'], fontSize=6, leading=8, fontName='Helvetica-Bold')
    style_legal = ParagraphStyle('Legal', parent=styles['Normal'], fontSize=5, leading=6, alignment=TA_JUSTIFY, textColor=colors.HexColor('#555555'))

    entrada = reserva.fecha_entrada
    salida = reserva.fecha_salida
    precio_noche = reserva.id_habitacion.precio_por_noche
    titular = reserva.id_huesped_titular
    acompanantes = reserva.huespedes_secundarios.filter(rol='Acompañante').select_related('id_huesped')

    header_table, _ = _construir_encabezado(
        "TARJETA UNIFICADA DE REGISTRO DE HUÉSPEDES",
        "GUEST REGISTERED CARD",
        ancho_util=ancho_util
    )
    elements.append(header_table)
    elements.append(Spacer(1, 3 * mm))

    # TABLA DE ESTANCIA
    estancia_data = [
        [
            Paragraph('<b>Habitación No.</b><br/><i>Room Nr.</i>', style_small),
            Paragraph('<b>Tipo de Habitación</b><br/><i>Room Type</i>', style_small),
            Paragraph('<b>Fecha de Entrada</b><br/><i>Arrival Date</i>', style_small),
            Paragraph('<b>Fecha de Salida</b><br/><i>Departure Date</i>', style_small),
            Paragraph('<b>N. Pers</b><br/><i>N. Pax</i>', style_small),
            Paragraph('<b>Tarifa</b><br/><i>Room rate</i>', style_small),
            Paragraph('<b>Forma de Pago</b><br/><i>Payment</i>', style_small),
            Paragraph('<b>Medio de Transporte</b><br/><i>Transportation</i>', style_small),
        ],
        [
            Paragraph(reserva.id_habitacion.numero, style_normal),
            Paragraph(reserva.id_habitacion.categoria_tipo, style_normal),
            Paragraph(entrada.strftime('%d/%m/%Y'), style_normal),
            Paragraph(salida.strftime('%d/%m/%Y'), style_normal),
            Paragraph(str(1 + acompanantes.count()), style_normal),
            Paragraph(f"${precio_noche}", style_normal),
            Paragraph(reserva.modalidad_pago, style_normal),
            Paragraph(getattr(titular, 'medio_transporte', None) or "Propio / Own", style_normal),
        ]
    ]

    tabla_estancia = Table(estancia_data, colWidths=[ancho_util * (1/8)] * 8)
    tabla_estancia.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(tabla_estancia)
    elements.append(Spacer(1, 3 * mm))

    # DATOS PERSONALES DEL TITULAR
    def linea_datos(label_es, label_en, valor):
        return Paragraph(f"<b>{label_es}</b> <i>{label_en}</i>: <u>&nbsp;&nbsp;{valor}&nbsp;&nbsp;</u>", style_normal)

    datos_personales = [
        [linea_datos("Nombre Completo /", "Full Name", f"{titular.nombres} {titular.apellidos}"),
            linea_datos("Edad /", "Age", titular.edad),
            linea_datos("C.I. /", "Passport", f"{titular.tipo_documento}-{titular.numero_documento}")],
        [linea_datos("Fecha de Nacimiento /", "Date of Birth", titular.fecha_nacimiento.strftime('%d/%m/%Y') if titular.fecha_nacimiento else '—'),
            linea_datos("Estado Civil /", "Marital Status", titular.estado_civil or '—'),
            linea_datos("Nacionalidad /", "Nationality", titular.nacionalidad or '—')],
        [linea_datos("Dirección /", "Address", titular.direccion or '—'),
            linea_datos("Ocupación /", "Occupation", titular.ocupacion.nombre if titular.ocupacion else '—'),
            Paragraph("", style_normal)],
        [linea_datos("Teléfono /", "Telephone", titular.telefono or '—'),
            linea_datos("Alergias /", "Allergies", getattr(titular, 'alergias', None) or "Ninguna / None"),
            linea_datos("Correo electrónico /", "Email", titular.email or "—")],
    ]

    tabla_personal = Table(datos_personales, colWidths=[ancho_util * 0.45, ancho_util * 0.30, ancho_util * 0.25])
    tabla_personal.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(tabla_personal)
    elements.append(Spacer(1, 4 * mm))

    # FIRMAS
    firma_huesped = Table(
        [[Paragraph("________________________", style_normal)], [Paragraph("<b>Firma /</b> <i>Signature</i>", style_small)]],
        colWidths=[ancho_util * 0.40]
    )
    firma_huesped.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

    firma_recepcion = Table(
        [[Paragraph("________________________", style_normal)], [Paragraph("<b>Firma Recepcionista</b>", style_small)]],
        colWidths=[ancho_util * 0.40]
    )
    firma_recepcion.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

    tabla_firmas_layout = Table([[firma_huesped, "", firma_recepcion]], colWidths=[ancho_util * 0.45, ancho_util * 0.10, ancho_util * 0.45])
    tabla_firmas_layout.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(tabla_firmas_layout)
    elements.append(Spacer(1, 4 * mm))

    # ACOMPAÑANTES
    if acompanantes.exists():
        elements.append(Paragraph("<b>ACOMPAÑANTES / GRUPO ADICIONAL</b>", style_small_bold))
        elements.append(Spacer(1, 1 * mm))

        acomp_data = [[
            Paragraph('<b>Nombre</b><br/><i>Name</i>', style_small),
            Paragraph('<b>Apellido</b><br/><i>Surname</i>', style_small),
            Paragraph('<b>C.I.</b><br/><i>Passport</i>', style_small),
            Paragraph('<b>Nacionalidad</b><br/><i>Nationality</i>', style_small),
            Paragraph('<b>Edad</b><br/><i>Age</i>', style_small),
            Paragraph('<b>Dirección</b><br/><i>Address</i>', style_small),
            Paragraph('<b>Firma</b><br/><i>Signature</i>', style_small),
        ]]

        for acomp in acompanantes:
            h = acomp.id_huesped
            acomp_data.append([
                Paragraph(f"{h.nombres}", style_normal),
                Paragraph(f"{h.apellidos}", style_normal),
                Paragraph(f"{h.tipo_documento}-{h.numero_documento}", style_normal),
                Paragraph(f"{h.nacionalidad or '—'}", style_normal),
                Paragraph(f"{h.edad or '—'}", style_normal),
                Paragraph(f"{h.direccion or '—'}", style_normal),
                Paragraph("", style_normal),
            ])

        for _ in range(max(0, 3 - acompanantes.count())):
            acomp_data.append([Paragraph("", style_normal)] * 7)

        tabla_acomp = Table(acomp_data, colWidths=[
            ancho_util * 0.18, ancho_util * 0.18, ancho_util * 0.15,
            ancho_util * 0.12, ancho_util * 0.08, ancho_util * 0.19, ancho_util * 0.10
        ])
        tabla_acomp.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('MINIMUMROWHEIGHT', (0, 1), (-1, -1), 10 * mm),
        ]))
        elements.append(tabla_acomp)
        elements.append(Spacer(1, 4 * mm))

    # TEXTO LEGAL
    texto_legal = (
        "<b>CONDICIONES GENERALES DEL CONTRATO.</b> El día y la hora de comienzo y terminación de este contrato se regirá por la reservación efectuada por el HUESPED con anticipación. "
        "El HUESPED deberá devolver la habitación en las condiciones que le fue entregada en el momento del Check In, y, en caso de no hacerlo Hotel Salma Suites VIP C.A., tiene el derecho de hacer desocupar la habitación y depositar las pertenencias del huésped, a riesgo y por cuenta del mismo en un lugar seguro del establecimiento. "
        "El HUESPED deberá pagar oportunamente la tarifa anunciada. "
        "El HUESPED deberá hacer uso de las cajas de seguridad para guardar sus pertenencias de valor. "
        "Hotel Salma Suites VIP C.A., no se hace responsable por los objetos de valor perdidos y/o dejados dentro de las habitaciones o espacios comunes. "
        "El HUESPED deberá acatar las Normas Internas del Establecimiento. "
        "El HUESPED tiene derecho a recibir la información detallada de todos y cada uno de los servicios incluidos en la tarifa. "
        "El HUESPED tiene derecho a recibir los servicios contratados de acuerdo con la categoría y clasificación otorgados y con la mayor cortesía y eficiencia por parte del personal."
    )
    elements.append(Paragraph(texto_legal, style_legal))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# --- REGISTRO SEMANAL DE RESERVACIONES ---
def generar_registro_reservaciones_semanal(fecha_referencia=None):
    if fecha_referencia is None:
        fecha_referencia = date.today()

    lunes = fecha_referencia - timedelta(days=fecha_referencia.weekday())
    domingo = lunes + timedelta(days=6)
    dias_semana = [lunes + timedelta(days=i) for i in range(7)]
    nombres_dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    from apps.reservaciones.models import Reservacion
    from apps.habitaciones.models import Habitacion
    from apps.configuracion.models import Ocupacion

    habitaciones = Habitacion.objects.all().order_by('piso', 'numero')
    reservas = Reservacion.objects.filter(
        estado__in=['Confirmada', 'EnCurso', 'Finalizada'],
        fecha_entrada__lt=domingo + timedelta(days=1),
        fecha_salida__gt=lunes
    ).select_related('id_huesped_titular', 'id_habitacion')

    mapa = {}
    for r in reservas:
        for dia in dias_semana:
            if r.fecha_entrada <= dia < r.fecha_salida:
                mapa[(r.id_habitacion_id, dia)] = r

    colores_ocupacion = {}
    for ocup in Ocupacion.objects.all():
        colores_ocupacion[ocup.nombre] = ocup.color

    buffer = BytesIO()
    page_width, page_height = 297 * mm, 210 * mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )
    ancho_util = page_width - 30 * mm

    elements = []
    styles = getSampleStyleSheet()

    style_cell = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=6, leading=8)
    style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=6, leading=8, fontName='Helvetica-Bold')
    style_header = ParagraphStyle('Header', parent=styles['Normal'], fontSize=6, leading=8, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.black)
    style_piso = ParagraphStyle('Piso', parent=styles['Normal'], fontSize=6, leading=8, fontName='Helvetica-Bold')
    style_leyenda = ParagraphStyle('Leyenda', parent=styles['Normal'], fontSize=5, leading=7)

    header_table, _ = _construir_encabezado(
        "REGISTRO DE RESERVACIONES SEMANAL",
        "WEEKLY BOOKING REGISTER",
        f"Semana del {lunes.strftime('%d/%m/%Y')} al {domingo.strftime('%d/%m/%Y')}",
        ancho_util=ancho_util
    )
    elements.append(header_table)
    elements.append(Spacer(1, 4 * mm))

    if colores_ocupacion:
        leyenda_items = []
        for tipo, color_hex in colores_ocupacion.items():
            leyenda_items.append(f'<font color="{color_hex}"><b>■</b></font> {tipo}')
        leyenda_html = ' &nbsp;&nbsp;|&nbsp;&nbsp; '.join(leyenda_items)
        elements.append(Paragraph(leyenda_html, style_leyenda))
        elements.append(Spacer(1, 2 * mm))

    col_widths = [ancho_util * 0.10] + [ancho_util * 0.09] * 7 + [ancho_util * 0.18]
    headers = [Paragraph('<b>Habitación</b>', style_header)]
    for i, dia in enumerate(dias_semana):
        headers.append(Paragraph(f'<b>{nombres_dias[i]}</b><br/>{dia.strftime("%d/%m")}', style_header))
    headers.append(Paragraph('<b>Huésped Titular</b>', style_header))

    datos = [headers]
    piso_actual = None
    for hab in habitaciones:
        if hab.piso != piso_actual:
            piso_actual = hab.piso
            datos.append([Paragraph(f'<b>PISO {hab.piso}</b>', style_piso)] + [''] * 8)

        fila = [Paragraph(f'<b>{hab.numero}</b><br/><font size="5">{hab.categoria_tipo}</font>', style_cell)]
        for dia in dias_semana:
            r = mapa.get((hab.id, dia))
            if r:
                ocup_nombre = r.id_huesped_titular.ocupacion.nombre if r.id_huesped_titular.ocupacion else 'Otro'
                color = colores_ocupacion.get(ocup_nombre, '#000000')

                if r.fecha_entrada == dia:
                    simbolo = '▶ LLEGADA'
                elif r.fecha_salida == dia + timedelta(days=1):
                    simbolo = '✔ SALIDA'
                else:
                    simbolo = '● OCUPADO'

                fila.append(Paragraph(f'<font color="{color}" size="6"><b>{simbolo}</b></font>', style_cell))
            else:
                fila.append(Paragraph('', style_cell))

        huesped_str = ''
        for dia in dias_semana:
            r = mapa.get((hab.id, dia))
            if r:
                huesped_str = f'{r.id_huesped_titular.nombres} {r.id_huesped_titular.apellidos}'
                break
        fila.append(Paragraph(huesped_str or '', style_cell_bold))
        datos.append(fila)

    tabla = Table(datos, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (-2, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(tabla)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# --- CIERRE DE CAJA DIARIO ---
def generar_cierre_caja_pdf(fecha):
    from apps.reservaciones.models import Pago
    from apps.bitacora.models import CierreCaja

    pagos = Pago.objects.filter(fecha_hora__date=fecha).select_related('id_reservacion__id_huesped_titular').order_by('fecha_hora')
    total_efectivo = pagos.filter(metodo_pago='Efectivo').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_tarjeta = pagos.filter(metodo_pago='Tarjeta').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_pago_movil = pagos.filter(metodo_pago='PagoMovil').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_general = total_efectivo + total_tarjeta + total_pago_movil

    buffer = BytesIO()
    page_width, page_height = 210 * mm, 297 * mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )
    ancho_util = page_width - 30 * mm

    elements = []
    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle('NormalPDF', parent=styles['Normal'], fontSize=8, leading=10)
    style_bold = ParagraphStyle('BoldPDF', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold')
    style_header = ParagraphStyle('HeaderPDF', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold', textColor=colors.black)
    style_card_label = ParagraphStyle('CardLabel', parent=styles['Normal'], fontSize=7, leading=9, alignment=TA_CENTER)
    style_card_value = ParagraphStyle('CardValue', parent=styles['Normal'], fontSize=12, leading=14, fontName='Helvetica-Bold', alignment=TA_CENTER)

    header_table, _ = _construir_encabezado(
        "CIERRE DE CAJA DIARIO",
        "DAILY CASH CLOSING",
        f"Fecha: {fecha.strftime('%d/%m/%Y')}",
        ancho_util=ancho_util
    )
    elements.append(header_table)
    elements.append(Spacer(1, 4 * mm))

    card_width = ancho_util / 4
    tarjetas_labels = [
        Paragraph('<b>TOTAL GENERAL</b>', style_card_label),
        Paragraph('<b>EFECTIVO</b>', style_card_label),
        Paragraph('<b>TARJETA</b>', style_card_label),
        Paragraph('<b>PAGO MÓVIL</b>', style_card_label),
    ]
    tarjetas_valores = [
        Paragraph(f'${total_general:,.2f}', style_card_value),
        Paragraph(f'${total_efectivo:,.2f}', style_card_value),
        Paragraph(f'${total_tarjeta:,.2f}', style_card_value),
        Paragraph(f'${total_pago_movil:,.2f}', style_card_value),
    ]
    tabla_tarjetas = Table([tarjetas_labels, tarjetas_valores], colWidths=[card_width] * 4)
    tabla_tarjetas.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(tabla_tarjetas)
    elements.append(Spacer(1, 4 * mm))

    elements.append(Paragraph(f'<b>Cantidad de transacciones:</b> {pagos.count()}', style_bold))
    elements.append(Spacer(1, 4 * mm))

    detalle_data = [[
        Paragraph('<b>Hora</b>', style_header),
        Paragraph('<b>Reserva</b>', style_header),
        Paragraph('<b>Huésped</b>', style_header),
        Paragraph('<b>Método</b>', style_header),
        Paragraph('<b>Referencia</b>', style_header),
        Paragraph('<b>Monto</b>', style_header),
    ]]

    for p in pagos:
        detalle_data.append([
            Paragraph(p.fecha_hora.strftime('%H:%M'), style_normal),
            Paragraph(f'#{p.id_reservacion_id}', style_normal),
            Paragraph(str(p.id_reservacion.id_huesped_titular), style_normal),
            Paragraph(p.metodo_pago, style_normal),
            Paragraph(p.numero_referencia or '—', style_normal),
            Paragraph(f'${p.monto:,.2f}', style_normal),
        ])

    col_widths_detalle = [ancho_util * 0.10, ancho_util * 0.10, ancho_util * 0.30, ancho_util * 0.15, ancho_util * 0.15, ancho_util * 0.15]
    tabla_detalle = Table(detalle_data, colWidths=col_widths_detalle, repeatRows=1)
    tabla_detalle.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(tabla_detalle)

    elements.append(Spacer(1, 10 * mm))
    firmas_data = [
        [Paragraph('________________________', style_normal), Paragraph('________________________', style_normal)],
        [Paragraph('<b>Firma del Cajero</b>', style_normal), Paragraph('<b>Firma del Supervisor</b>', style_normal)],
    ]
    tabla_firmas = Table(firmas_data, colWidths=[ancho_util * 0.50] * 2)
    tabla_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(tabla_firmas)

    doc.build(elements)
    buffer.seek(0)
    return buffer
