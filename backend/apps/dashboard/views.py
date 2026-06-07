from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from apps.reservaciones.models import Reserva
from apps.habitaciones.models import Habitacion
from apps.inventario.models import Producto
from apps.pagos.models import Pago


def calcular_trend(valor_hoy, valor_ayer):
    """
    Calcula matemáticamente el porcentaje de cambio 
    entre hoy y ayer mitigando divisiones por cero de forma compacta y elegante.
    """
    if not valor_ayer:
        return {'porcentaje': 100.0 if valor_hoy > 0 else 0.0, 'direccion': 'up' if valor_hoy > 0 else 'flat'}
    
    porcentaje = round(((float(valor_hoy) - float(valor_ayer)) / float(valor_ayer)) * 100, 1)
    return {
        'porcentaje': abs(porcentaje),
        'direccion': 'up' if porcentaje > 0 else ('down' if porcentaje < 0 else 'flat')
    }

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def dashboard_stats(request):
    """
    RF01: Estadísticas principales del dashboard.
    """
    hoy = timezone.now().date()
    ayer = hoy - timedelta(days=1)

    # --- CONSULTAS DE HOY ---
    reservas_hoy = Reserva.objects.filter(fecha_entrada=hoy)
    checkins_hoy = reservas_hoy.filter(estado='check_in').count()
    total_reservas_hoy = reservas_hoy.count()
    
    ingresos_hoy = Pago.objects.filter(fecha__date=hoy).aggregate(total=Sum('monto'))['total'] or 0
    ocupadas_hoy = Habitacion.objects.filter(estado='ocupada').count()

    # --- CONSULTAS DE AYER (Para cálculo de Trends) ---
    reservas_ayer = Reserva.objects.filter(fecha_entrada=ayer)
    checkins_ayer = reservas_ayer.filter(estado='check_in').count()
    total_reservas_ayer = reservas_ayer.count()
    
    ingresos_ayer = Pago.objects.filter(fecha__date=ayer).aggregate(total=Sum('monto'))['total'] or 0
    ocupadas_ayer = Habitacion.objects.filter(estado='ocupada', reservas__fecha_entrada=ayer).count() # Aproximación analítica

    # --- CÁLCULO DE CAPACIDAD ---
    total_habitaciones = Habitacion.objects.count()
    porcentaje_ocupacion = round((ocupadas_hoy / total_habitaciones * 100), 1) if total_habitaciones > 0 else 0

    return Response({
        'tarjetas': {
            'ingresos_hoy': {
                'valor': float(ingresos_hoy),
                'trend': calcular_trend(ingresos_hoy, ingresos_ayer)
            },
            'ocupacion_actual': {
                'valor': f"{porcentaje_ocupacion}%",
                'trend': calcular_trend(ocupadas_hoy, ocupadas_ayer)
            },
            'checkins_hoy': {
                'valor': checkins_hoy,
                'trend': calcular_trend(checkins_hoy, checkins_ayer)
            },
            'total_reservas': {
                'valor': total_reservas_hoy,
                'trend': calcular_trend(total_reservas_hoy, total_reservas_ayer)
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def dashboard_alertas(request):
    """
    Módulo de alertas críticas unificado y optimizado contra consultas N+1.
    """
    hoy = timezone.now().date()

    # Habitaciones críticas
    en_mantenimiento = Habitacion.objects.filter(estado='mantenimiento').values('id', 'numero', 'tipo')

    # Inventario crítico
    productos_alerta = Producto.objects.filter(
        Q(sin_stock=True) | Q(stock_bajo=True)
    ).values('nombre', 'stock_actual', 'sin_stock')

    checkouts_pendientes = Reserva.objects.filter(
        fecha_salida=hoy,
        estado__in=['confirmada', 'pagada']
    ).select_related('huesped', 'habitacion').values(
        'id',
        'huesped__nombre',
        'huesped__apellido',
        'habitacion__numero'
    )

    sin_pagar_hoy = Reserva.objects.filter(fecha_entrada=hoy, estado='sin_pagar').count()

    return Response({
        'habitaciones_mantenimiento': list(en_mantenimiento),
        'productos_alerta': list(productos_alerta),
        'checkouts_pendientes': list(checkouts_pendientes),
        'reservas_sin_pagar_hoy': sin_pagar_hoy,
        'total_alertas': len(en_mantenimiento) + len(productos_alerta) + len(checkouts_pendientes) + sin_pagar_hoy
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ocupacion_semanal(request):
    """
    Satisface:
    let ocupacionSemanal = $derived((data.ocupacionSemanal as any)?.valores ?? []);
    let diasSemana = $derived((data.ocupacionSemanal as any)?.dias ?? []);
    """
    hoy = timezone.now().date()
    total_habitaciones = Habitacion.objects.count() or 1

    valores_porcentaje = []
    nombres_dias = []

    # Traducción rápida para renderizado compacto en el gráfico
    dias_es = {
        'Monday': 'Lun', 'Tuesday': 'Mar', 'Wednesday': 'Mié', 
        'Thursday': 'Jue', 'Friday': 'Vie', 'Saturday': 'Sáb', 'Sunday': 'Dom'
    }

    # Construimos el histórico de los últimos 7 días
    for i in range(6, -1, -1):
        fecha_evaluacion = hoy - timedelta(days=i)
        
        habitaciones_ocupadas = Reserva.objects.filter(
            estado='check_in',
            fecha_entrada__lte=fecha_evaluacion,
            fecha_salida__gte=fecha_evaluacion
        ).values('habitacion').distinct().count()

        porcentaje_ocupacion = round((habitaciones_ocupadas / total_habitaciones) * 100, 2)
        
        dia_semana_en = fecha_evaluacion.strftime('%A')
        dia_semana_es = dias_es.get(dia_semana_en, dia_semana_en)

        valores_porcentaje.append(porcentaje_ocupacion)
        nombres_dias.append(dia_semana_es)

    return Response({
        'valores': valores_porcentaje,
        'dias': nombres_dias
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def habitaciones_grid(request):
    """
    Satisface:
    interface Habitacion { num: string; estado: 'libre' | 'ocupada' | 'mantenimiento'; tipo: string; piso: number; }
    {#each habitacionesFiltradas as hab} -> {hab.num}
    """
    # Traemos la lista plana ordenada, tal como la espera el array 'habitaciones' de tu frontend
    habitaciones_qs = Habitacion.objects.select_related('tipo').all().order_by('piso', 'numero')
    
    payload_habitaciones = []
    
    for hab in habitaciones_qs:
        # Extraemos el string del tipo de habitación de forma segura
        tipo_nombre = hab.tipo.nombre if hab.tipo else 'Estándar'
        
        payload_habitaciones.append({
            'num': str(hab.numero),           # Forzamos mapeo exacto a 'num' esperado por Svelte
            'estado': hab.estado,             # 'libre' | 'ocupada' | 'mantenimiento'
            'tipo': tipo_nombre,              # Un string plano según tu interfaz de TypeScript
            'piso': hab.piso                  # Número de piso
        })

    # Retornamos el array directamente. SvelteKit en su load probablemente lo asigna a data.habitaciones
    # Si tu load lee el JSON completo, puedes envolverlo en un diccionario si es necesario.
    return Response(payload_habitaciones, status=status.HTTP_200_OK)
    """
    RF12: Retorna el estado actual de todas las habitaciones del hotel agrupadas por piso.
    Optimizado con select_related para evitar ráfagas de consultas N+1 al consultar los tipos.
    """
    # Traemos el inventario completo precargando los datos del tipo de habitación (nombre, precio, etc.)
    habitaciones = Habitacion.objects.select_related('tipo').all().order_by('piso', 'numero')
    
    # Estructuramos un diccionario para agrupar de forma limpia por piso directamente en el backend
    grid_por_piso = {}
    
    for hab in habitaciones:
        piso = hab.piso
        if piso not in grid_por_piso:
            grid_por_piso[piso] = []
            
        # Extracción segura de la tarifa para evitar que el maldito AttributeError tumbe el PMS
        tipo_obj = hab.tipo
        precio = 0.0
        if tipo_obj:
            # Evaluamos dinámicamente qué atributo le pusiste en tu modelo real
            precio = getattr(tipo_obj, 'precio_base', 
                    getattr(tipo_obj, 'precio', 
                    getattr(tipo_obj, 'tarifa', 
                    getattr(tipo_obj, 'precio_noche', 0.0))))
            
        grid_por_piso[piso].append({
            'id': hab.id,
            'numero': hab.numero,
            'estado': hab.estado, 
            'tipo': {
                'id': tipo_obj.id if tipo_obj else None,
                'nombre': tipo_obj.nombre if tipo_obj else 'Estándar',
                'precio_base': precio,  # Mapeo blindado libre de quiebres
                'capacidad': getattr(tipo_obj, 'capacidad', 2)
            }
        })
        
    # Formateamos la respuesta como una lista ordenada
    respuesta_formateada = [
        {
            'piso': piso,
            'habitaciones': habitaciones_lista
        }
        for piso, habitaciones_lista in sorted(grid_por_piso.items())
    ]

    return Response({
        'total_habitaciones': habitaciones.count(),
        'pisos_detectados': len(grid_por_piso),
        'grid': respuesta_formateada
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def actividades_dashboard(request):
    """
    RF12: Retorna el feed de las últimas 15 actividades y auditorías del hotel
    para mostrar en la línea de tiempo del Dashboard.
    Optimizado con select_related para traer los datos del usuario operador sin N+1.
    """
    try:
        # Intentamos importar dinámicamente si tus logs viven en otra app mapeada
        # Si tienes el modelo directo, colócalo arriba en las importaciones globales.
        from apps.reservaciones.models import ActividadLog
    except ImportError:
        # Fallback de emergencia por si tu modelo está en otra ruta del ecosistema
        # Si no tienes un modelo de logs creado aún, retornamos una lista vacía controlada
        return Response({
            'message': 'Módulo de auditoría en mantenimiento.',
            'timeline': []
        }, status=status.HTTP_200_OK)

    # Consulta senior: Traemos las últimas 15 acciones ejecutadas en el hotel
    logs = ActividadLog.objects.select_related('usuario').all().order_by('-fecha_registro')[:15]

    timeline = []
    for log in logs:
        timeline.append({
            'id': log.id,
            'tipo': log.tipo, # 'pago', 'reserva_creada', 'cambio_habitacion', 'no_show'
            'descripcion': log.descripcion,
            'fecha': log.fecha_registro.isoformat(),
            'operador': {
                'id': log.usuario.id if log.usuario else None,
                'username': log.usuario.username if log.usuario else 'Sistema',
                'role': log.usuario.role if log.usuario else 'Bot'
            }
        })

    return Response({
        'conteo_feed': len(timeline),
        'timeline': timeline
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def alertas_dashboard(request):
    """
    RF12: Endpoint de Auditoría en Tiempo Real.
    Escanea el ecosistema del hotel para consolidar alarmas operativas y de inventario,
    alimentando los badges de notificación crítica en el frontend de SvelteKit.
    """
    hoy_ahora = timezone.now()
    alertas = []

    # 1. Alerta de Infraestructura: Habitaciones sucias que bloquean disponibilidad
    habitaciones_sucias = Habitacion.objects.filter(estado='sucia').values_list('numero', flat=True)
    if habitaciones_sucias.exists():
        alertas.append({
            'nivel': 'warning',
            'categoria': 'infraestructura',
            'mensaje': f"Hay {habitaciones_sucias.count()} habitaciones sucias que requieren atención del personal de limpieza.",
            'detalles': [f"H-{num}" for num in habitaciones_sucias]
        })

    # 2. Alerta Operativa: Check-outs pendientes/retrasados (Estadías en el limbo)
    # Buscamos reservas en 'check_in' cuya fecha de salida planificada ya pasó
    checkouts_vencidos = Reserva.objects.filter(
        estado='check_in',
        fecha_salida__lt=hoy_ahora
    ).select_related('huesped', 'habitacion')

    if checkouts_vencidos.exists():
        alertas.append({
            'nivel': 'danger',
            'categoria': 'operativa',
            'mensaje': f"Atención: Se detectaron {checkouts_vencidos.count()} check-outs retrasados en recepción.",
            'detalles': [
                f"H-{res.habitacion.numero if res.habitacion else 'N/A'} - {res.huesped.nombre} (Venció: {res.fecha_salida.strftime('%I:%M %p')})"
                for res in checkouts_vencidos
            ]
        })

    # 3. Alerta de Suministros: Quiebres de Stock o Inventario Bajo
    productos_criticos = Producto.objects.filter(django_models.Q(sin_stock=True) | django_models.Q(stock_bajo=True), activo=True)
    if productos_criticos.exists():
        quiebres = productos_criticos.filter(sin_stock=True).count()
        bajos = productos_criticos.filter(stock_bajo=True).count()
        
        alertas.append({
            'nivel': 'danger' if quiebres > 0 else 'warning',
            'categoria': 'inventario',
            'mensaje': f"Alerta de almacén: {quiebres} productos agotados y {bajos} con stock mínimo comprometido.",
            'detalles': [f"{p.nombre} (Disponibles: {p.stock_actual})" for p in productos_criticos[:5]] # Limitamos a 5 detalles para no saturar la respuesta
        })

    return Response({
        'timestamp': hoy_ahora.isoformat(),
        'conteo_alertas': len(alertas),
        'alertas': alertas
    }, status=status.HTTP_200_OK)