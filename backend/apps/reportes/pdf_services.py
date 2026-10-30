from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum
import os


def _get_config():
    from apps.configuracion.models import Configuracion
    config = {}
    for c in Configuracion.objects.all():
        config[c.clave] = c.valor
    return config


def _get_logo_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logo_path = os.path.join(base_dir, 'assets', 'logo.png')
    if os.path.exists(logo_path):
        return logo_path

    config = _get_config()
    logo_nombre = config.get('logo', '')
    if logo_nombre:
        if logo_nombre.lower().endswith('.svg'):
            logo_nombre = logo_nombre[:-4] + '.png'
        ruta_media = os.path.join(settings.MEDIA_ROOT, logo_nombre)
        if os.path.exists(ruta_media):
            return ruta_media
    return None


def _estilo_celdas(background='#ffffff', header=False):
    estilo = [
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(background)),
    ]
    if header:
        estilo.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d1b14')))
    return TableStyle(estilo)


def generar_hoja_huesped(reserva):
    buffer = BytesIO()
    page_width, page_height = 216 * mm, 140 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
    )

    ancho_util = page_width - 24 * mm

    elements = []
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle('Title2', parent=styles['Title'], fontSize=11, leading=13, alignment=TA_CENTER, spaceAfter=2)
    style_subtitle = ParagraphStyle('Sub2', parent=styles['Normal'], fontSize=7, leading=9, alignment=TA_CENTER, textColor=colors.grey)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=6.5, leading=8, fontName='Helvetica-Bold')
    style_small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=6, leading=7)
    style_header = ParagraphStyle('HeaderT', parent=styles['Normal'], fontSize=6, leading=8, fontName='Helvetica-Bold', textColor=colors.white)
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=5, leading=6, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    config = _get_config()
    nombre_hotel = config.get('nombre_hotel', 'Hotel Salma Suite VIP')
    rif = config.get('rif', '')
    direccion = config.get('direccion', '')
    telefono = config.get('telefono', '')

    hoy = date.today()
    entrada = reserva.fecha_entrada
    salida = reserva.fecha_salida
    noches = (salida - entrada).days
    precio_noche = reserva.id_habitacion.precio_por_noche
    total_habitacion = noches * precio_noche
    total_consumos = reserva.monto_total_consumos
    total_general = total_habitacion + total_consumos
    titular = reserva.id_huesped_titular

    # Logo
    logo_path = _get_logo_path()
    if logo_path:
        logo = Image(logo_path, width=25 * mm, height=12 * mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 1 * mm))

    elements.append(Paragraph(f'<b>{nombre_hotel}</b>', style_title))
    if rif:
        elements.append(Paragraph(f'RIF: {rif}', style_subtitle))
    elements.append(Paragraph(f'{direccion}  •  {telefono}', style_subtitle))
    elements.append(Spacer(1, 2 * mm))

    elements.append(Paragraph('<b>HOJA DE REGISTRO DE HUÉSPED</b>', style_title))
    elements.append(Spacer(1, 2 * mm))

    # --- FILA 1: Fecha y Habitación ---
    fila1 = [[
        Paragraph(f'<b>Día:</b> {hoy.day}', style_label),
        Paragraph(f'<b>Mes:</b> {hoy.month}', style_label),
        Paragraph(f'<b>Año:</b> {hoy.year}', style_label),
        Paragraph(f'<b>Nº Hab:</b> {reserva.id_habitacion.numero}', style_label),
    ]]
    tabla_fila1 = Table(fila1, colWidths=[ancho_util * 0.25] * 4)
    tabla_fila1.setStyle(_estilo_celdas(background='#f5f5f5'))
    elements.append(tabla_fila1)
    elements.append(Spacer(1, 1.5 * mm))

    # --- FILA 2: Nombre y Apellido ---
    fila2 = [[
        Paragraph(f'<b>Nombre:</b> {titular.nombres}', style_label),
        Paragraph(f'<b>Apellido:</b> {titular.apellidos}', style_label),
    ]]
    tabla_fila2 = Table(fila2, colWidths=[ancho_util * 0.50] * 2)
    tabla_fila2.setStyle(_estilo_celdas())
    elements.append(tabla_fila2)
    elements.append(Spacer(1, 1.5 * mm))

    # --- FILA 3: Cédula, Edad, Nacionalidad ---
    fila3 = [[
        Paragraph(f'<b>C.I.:</b> {titular.tipo_documento}-{titular.numero_documento}', style_label),
        Paragraph(f'<b>Edad:</b> {titular.edad}', style_label),
        Paragraph(f'<b>Nacionalidad:</b> {titular.nacionalidad}', style_label),
    ]]
    tabla_fila3 = Table(fila3, colWidths=[ancho_util * 0.40, ancho_util * 0.20, ancho_util * 0.40])
    tabla_fila3.setStyle(_estilo_celdas())
    elements.append(tabla_fila3)
    elements.append(Spacer(1, 1.5 * mm))

    # --- FILA 4: Estado Civil, F. Nacimiento, Procedencia ---
    fila4 = [[
        Paragraph(f'<b>Estado Civil:</b> {titular.estado_civil}', style_label),
        Paragraph(f'<b>F. Nac.:</b> {titular.fecha_nacimiento.strftime("%d/%m/%Y")}', style_label),
        Paragraph(f'<b>Procedencia:</b> {titular.procedencia}', style_label),
    ]]
    tabla_fila4 = Table(fila4, colWidths=[ancho_util * 0.33] * 3)
    tabla_fila4.setStyle(_estilo_celdas())
    elements.append(tabla_fila4)
    elements.append(Spacer(1, 1.5 * mm))

    # --- FILA 5: Teléfono, Profesión ---
    fila5 = [[
        Paragraph(f'<b>Teléfono:</b> {titular.telefono}', style_label),
        Paragraph(f'<b>Profesión:</b> {titular.tipo_cliente_profesion}', style_label),
    ]]
    tabla_fila5 = Table(fila5, colWidths=[ancho_util * 0.40, ancho_util * 0.60])
    tabla_fila5.setStyle(_estilo_celdas())
    elements.append(tabla_fila5)
    elements.append(Spacer(1, 2 * mm))

    # --- COSTOS ---
    fila_costos1 = [[
        Paragraph(f'<b>Precio/Noche:</b> ${precio_noche}', style_label),
        Paragraph(f'<b>Noches:</b> {noches}', style_label),
        Paragraph(f'<b>Total Habitación:</b> ${total_habitacion}', style_label),
    ]]
    tabla_costos1 = Table(fila_costos1, colWidths=[ancho_util * 0.33] * 3)
    tabla_costos1.setStyle(_estilo_celdas(background='#fff9e6'))
    elements.append(tabla_costos1)
    elements.append(Spacer(1, 1.5 * mm))

    fila_costos2 = [[
        Paragraph(f'<b>Total Consumos:</b> ${total_consumos}', style_label),
        Paragraph(f'<b>Total General:</b> ${total_general}', style_label),
        Paragraph(f'<b>Modalidad:</b> {reserva.modalidad_pago}', style_label),
    ]]
    tabla_costos2 = Table(fila_costos2, colWidths=[ancho_util * 0.33] * 3)
    tabla_costos2.setStyle(_estilo_celdas(background='#fff9e6'))
    elements.append(tabla_costos2)
    elements.append(Spacer(1, 2 * mm))

    # --- ACOMPAÑANTES ---
    acompanantes = reserva.huespedes_secundarios.filter(rol='Acompañante').select_related('id_huesped')
    if acompanantes.exists():
        elements.append(Paragraph('<b>ACOMPAÑANTES</b>', style_label))
        datos_acomp = [[
            Paragraph('<b>Nombre y Apellido</b>', style_header),
            Paragraph('<b>C.I.</b>', style_header),
            Paragraph('<b>Edad</b>', style_header),
        ]]
        for acomp in acompanantes:
            h = acomp.id_huesped
            datos_acomp.append([
                Paragraph(f'{h.nombres} {h.apellidos}', style_small),
                Paragraph(f'{h.tipo_documento}-{h.numero_documento}', style_small),
                Paragraph(f'{h.edad}', style_small),
            ])
        tabla_acomp = Table(datos_acomp, colWidths=[ancho_util * 0.50, ancho_util * 0.30, ancho_util * 0.20])
        tabla_acomp.setStyle(_estilo_celdas(header=True))
        elements.append(tabla_acomp)
        elements.append(Spacer(1, 2 * mm))

    obs = reserva.acta or titular.observaciones or ''
    if obs:
        elements.append(Paragraph(f'<b>Observaciones:</b> {obs}', style_small))
        elements.append(Spacer(1, 2 * mm))

    elements.append(Spacer(1, 8 * mm))

    firma_ancho = ancho_util * 0.35
    margen_entre_firmas = ancho_util * 0.10
    margen_lateral = ancho_util * 0.10

    datos_firmas = [
        [Paragraph('________________________', style_small), Paragraph('________________________', style_small)],
        [Paragraph('<b>Firma del Huésped</b>', style_small), Paragraph('<b>Firma del Recepcionista</b>', style_small)],
    ]

    tabla_firmas = Table(
        datos_firmas,
        colWidths=[firma_ancho, firma_ancho]
    )
    tabla_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    tabla_firmas_centrada = Table(
        [[tabla_firmas]],
        colWidths=[ancho_util]
    )
    tabla_firmas_centrada.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(tabla_firmas_centrada)

    # --- REVERSO ---
    elements.append(PageBreak())

    elements.append(Paragraph('<b>REGISTRO DE CONSUMOS Y PAGOS</b>', style_title))
    elements.append(Paragraph(f'Huésped: {titular.nombres} {titular.apellidos}', style_small))
    elements.append(Paragraph(f'Habitación: {reserva.id_habitacion.numero}', style_small))
    elements.append(Spacer(1, 2 * mm))

    consumos = reserva.consumos.all().order_by('fecha_hora')
    pagos = reserva.pagos.all().order_by('fecha_hora')

    movimientos = []
    for c in consumos:
        movimientos.append({
            'fecha': c.fecha_hora,
            'descripcion': f'{c.tipo_consumo}: {c.descripcion} (x{c.cantidad})',
            'tipo': 'Consumo',
            'monto': float(c.total),
            'referencia': '',
        })
    for p in pagos:
        movimientos.append({
            'fecha': p.fecha_hora,
            'descripcion': 'Pago registrado',
            'tipo': p.metodo_pago,
            'monto': float(p.monto),
            'referencia': p.numero_referencia or '',
        })
    movimientos.sort(key=lambda x: x['fecha'])

    datos_reverso = [[
        Paragraph('<b>Nº</b>', style_header),
        Paragraph('<b>Fecha</b>', style_header),
        Paragraph('<b>Descripción</b>', style_header),
        Paragraph('<b>Forma Pago</b>', style_header),
        Paragraph('<b>Monto</b>', style_header),
        Paragraph('<b>Ref.</b>', style_header),
    ]]

    for i, m in enumerate(movimientos, 1):
        datos_reverso.append([
            Paragraph(str(i), style_small),
            Paragraph(m['fecha'].strftime('%d/%m %H:%M'), style_small),
            Paragraph(m['descripcion'], style_small),
            Paragraph(m['tipo'], style_small),
            Paragraph(f'${m["monto"]:.2f}', style_small),
            Paragraph(m['referencia'], style_small),
        ])

    tabla_reverso = Table(
        datos_reverso,
        colWidths=[ancho_util * 0.08, ancho_util * 0.18, ancho_util * 0.32, ancho_util * 0.18, ancho_util * 0.14, ancho_util * 0.10]
    )
    tabla_reverso.setStyle(_estilo_celdas(header=True))
    elements.append(tabla_reverso)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_registro_reservaciones_semanal(fecha_referencia=None):
    from datetime import timedelta
    from apps.reservaciones.models import Reservacion
    from apps.habitaciones.models import Habitacion
    from apps.configuracion.models import ColoresTipoCliente

    if fecha_referencia is None:
        fecha_referencia = date.today()

    lunes = fecha_referencia - timedelta(days=fecha_referencia.weekday())
    domingo = lunes + timedelta(days=6)
    dias_semana = [lunes + timedelta(days=i) for i in range(7)]
    nombres_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

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

    colores_tipo = {}
    for color in ColoresTipoCliente.objects.all():
        colores_tipo[color.tipo_cliente_profesion] = color.color

    buffer = BytesIO()
    page_width, page_height = 297 * mm, 210 * mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
    )
    ancho_util = page_width - 24 * mm

    elements = []
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle('TitlePDF', parent=styles['Title'], fontSize=14, leading=16, alignment=TA_CENTER, spaceAfter=2)
    style_subtitle = ParagraphStyle('SubPDF', parent=styles['Normal'], fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.grey)
    style_cell = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=6.5, leading=8)
    style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=6.5, leading=8, fontName='Helvetica-Bold')
    style_header = ParagraphStyle('Header', parent=styles['Normal'], fontSize=7, leading=9, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.white)
    style_piso = ParagraphStyle('Piso', parent=styles['Normal'], fontSize=7, leading=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#b38e5d'))
    style_leyenda = ParagraphStyle('Leyenda', parent=styles['Normal'], fontSize=6, leading=8, textColor=colors.HexColor('#666666'))

    config = _get_config()
    nombre_hotel = config.get('nombre_hotel', 'Hotel Salma Suite VIP')
    rif = config.get('rif', '')
    direccion = config.get('direccion', '')
    telefono = config.get('telefono', '')

    logo_path = _get_logo_path()
    if logo_path:
        logo = Image(logo_path, width=30 * mm, height=15 * mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 2 * mm))

    elements.append(Paragraph(f'<b>{nombre_hotel}</b>', style_title))
    if rif:
        elements.append(Paragraph(f'RIF: {rif}', style_subtitle))
    elements.append(Paragraph(f'{direccion}  •  {telefono}', style_subtitle))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph('<b>REGISTRO DE RESERVACIONES SEMANAL</b>', style_title))
    elements.append(Paragraph(f'Semana del {lunes.strftime("%d/%m/%Y")} al {domingo.strftime("%d/%m/%Y")}', style_subtitle))
    elements.append(Spacer(1, 5 * mm))

    if colores_tipo:
        leyenda_items = []
        for tipo, color_hex in colores_tipo.items():
            leyenda_items.append(f'<font color="{color_hex}">●</font> {tipo}')
        leyenda_html = ' &nbsp;&nbsp;|&nbsp;&nbsp; '.join(leyenda_items)
        elements.append(Paragraph(leyenda_html, style_leyenda))
        elements.append(Spacer(1, 3 * mm))

    col_widths = [ancho_util * 0.10]
    for _ in range(7):
        col_widths.append(ancho_util * 0.09)
    col_widths.append(ancho_util * 0.18)

    headers = [Paragraph('<b>Habitación</b>', style_header)]
    for i, dia in enumerate(dias_semana):
        headers.append(Paragraph(f'<b>{nombres_dias[i][:3]}</b><br/>{dia.strftime("%d/%m")}', style_header))
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
                tipo_cliente = r.id_huesped_titular.tipo_cliente_profesion
                color = colores_tipo.get(tipo_cliente, '#b38e5d')
                if r.fecha_entrada == dia:
                    simbolo = '→'
                elif r.fecha_salida == dia + timedelta(days=1):
                    simbolo = '✓'
                else:
                    simbolo = '●'
                fila.append(Paragraph(f'<font color="{color}">{simbolo}</font>', style_cell))
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
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d1b14')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (-2, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafaf5')]),
    ]))
    elements.append(tabla)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_cierre_caja_pdf(fecha):
    from apps.reservaciones.models import Pago
    from apps.bitacora.models import CierreCaja

    pagos = Pago.objects.filter(fecha_hora__date=fecha).select_related('id_reservacion__id_huesped_titular').order_by('fecha_hora')
    total_efectivo = pagos.filter(metodo_pago='Efectivo').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_tarjeta = pagos.filter(metodo_pago='Tarjeta').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_pago_movil = pagos.filter(metodo_pago='PagoMovil').aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_general = total_efectivo + total_tarjeta + total_pago_movil
    cerrado = CierreCaja.objects.filter(fecha=fecha).exists()

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

    style_title = ParagraphStyle('TitlePDF', parent=styles['Title'], fontSize=14, leading=16, alignment=TA_CENTER, spaceAfter=2)
    style_subtitle = ParagraphStyle('SubPDF', parent=styles['Normal'], fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.grey)
    style_normal = ParagraphStyle('NormalPDF', parent=styles['Normal'], fontSize=8, leading=10)
    style_bold = ParagraphStyle('BoldPDF', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold')
    style_header = ParagraphStyle('HeaderPDF', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold', textColor=colors.white)
    style_card_label = ParagraphStyle('CardLabel', parent=styles['Normal'], fontSize=7, leading=9, textColor=colors.HexColor('#827066'), alignment=TA_CENTER)
    style_card_value = ParagraphStyle('CardValue', parent=styles['Normal'], fontSize=12, leading=14, fontName='Helvetica-Bold', alignment=TA_CENTER)
    style_footer = ParagraphStyle('FooterPDF', parent=styles['Normal'], fontSize=6, leading=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    config = _get_config()
    nombre_hotel = config.get('nombre_hotel', 'Hotel Salma Suite VIP')
    rif = config.get('rif', '')
    direccion = config.get('direccion', '')
    telefono = config.get('telefono', '')

    logo_path = _get_logo_path()
    if logo_path:
        logo = Image(logo_path, width=25 * mm, height=12 * mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 2 * mm))

    elements.append(Paragraph(f'<b>{nombre_hotel}</b>', style_title))
    if rif:
        elements.append(Paragraph(f'RIF: {rif}', style_subtitle))
    elements.append(Paragraph(f'{direccion}  •  {telefono}', style_subtitle))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph('<b>CIERRE DE CAJA DIARIO</b>', style_title))
    elements.append(Paragraph(f'Fecha: {fecha.strftime("%d/%m/%Y")}', style_subtitle))

    if cerrado:
        elements.append(Paragraph('<font color="#2d6a4f"><b>✓ CERRADO</b></font>', style_subtitle))
    else:
        elements.append(Paragraph('<font color="#9b2226"><b>⚠ PENDIENTE DE CIERRE</b></font>', style_subtitle))

    elements.append(Spacer(1, 8 * mm))

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
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b38e5d')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d1b14')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fff9e6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(tabla_tarjetas)
    elements.append(Spacer(1, 3 * mm))

    elements.append(Paragraph(f'<b>Cantidad de transacciones:</b> {pagos.count()}', style_bold))
    elements.append(Spacer(1, 5 * mm))

    elements.append(Paragraph('<b>DETALLE DE TRANSACCIONES</b>', style_bold))
    elements.append(Spacer(1, 3 * mm))

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
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d1b14')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafaf5')]),
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
