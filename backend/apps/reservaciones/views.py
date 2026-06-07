from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction  # Control absoluto de transacciones
from django.db.models import Q

from .models import Reserva, Consumo, Actividad
from .serializers import ReservaSerializer, ReservaListSerializer, ConsumoSerializer, ActividadSerializer
from apps.habitaciones.models import Habitacion
from utils import paginar_queryset_funcion  # Helper central de paginación

def registrar_actividad(tipo, descripcion, usuario, reserva=None, habitacion=None, huesped=None):
    """ Helper interno optimizado para loguear auditorías en el timeline. """
    Actividad.objects.create(
        tipo=tipo, descripcion=descripcion, usuario=usuario,
        reserva=reserva, habitacion=habitacion, huesped=huesped
    )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reservas_list(request):
    """
    GET: Lista reservas mitigando el problema N+1 usando pre-cargas y paginación.
    POST: Crea reservas de manera atómica aislando el estado de la habitación.
    """
    if request.method == 'GET':
        # BLINDADO SQL N+1: Trae llaves foráneas y colecciones ManyToMany de forma óptima
        qs = Reserva.objects.select_related('huesped', 'habitacion', 'habitacion__tipo')\
                            .prefetch_related('consumos', 'pagos')\
                            .all().order_by('-created_at')

        estado = request.query_params.get('estado')
        search = request.query_params.get('search')
        estados_param = request.query_params.get('estados')   # ← NUEVO

        if estado:
            qs = qs.filter(estado=estado)
        if search:
            qs = qs.filter(Q(huesped__nombre__icontains=search) | Q(huesped__apellido__icontains=search))
        if estados_param:
            estados_lista = estados_param.split(',')
            qs = qs.filter(estado__in=estados_lista)

        return paginar_queryset_funcion(request, qs, ReservaListSerializer, page_size=15)

    if request.method == 'POST':
        habitacion_id = request.data.get('habitacion')
        
        try:
            with transaction.atomic():
                # Candado de fila en BD para evitar asignación simultánea destructiva
                habitacion = Habitacion.objects.select_for_update().get(pk=habitacion_id)
                
                if habitacion.estado in ['ocupada', 'mantenimiento']:
                    return Response({'error': 'La habitación seleccionada no se encuentra disponible.'}, status=status.HTTP_400_BAD_REQUEST)

                serializer = ReservaSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                reserva = serializer.save()
                
                # Sincronización del estado de la habitación si entra de inmediato
                if reserva.estado == 'check_in':
                    habitacion.estado = 'ocupada'
                    habitacion.save(update_fields=['estado'])

                registrar_actividad('reserva_creada', f"Reserva #{reserva.id} creada para H-{habitacion.numero}", request.user, reserva, habitacion, reserva.huesped)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Habitacion.DoesNotExist:
            return Response({'error': 'Habitación inválida.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ejecutar_checkin(request, pk):
    """ RF04: Ejecuta el Check-in de forma transaccional y blindada. """
    try:
        with transaction.atomic():
            reserva = Reserva.objects.select_related('habitacion', 'huesped').select_for_update().get(pk=pk)
            
            if reserva.estado != 'sin_pagar' and reserva.estado != 'confirmada':
                return Response({'error': f'No se puede hacer check-in en una reserva con estado: {reserva.estado}'}, status=status.HTTP_400_BAD_REQUEST)
            
            habitacion = reserva.habitacion
            if habitacion.estado in ['ocupada', 'mantenimiento']:
                return Response({'error': 'La habitación está ocupada o bajo mantenimiento actualmente.'}, status=status.HTTP_400_BAD_REQUEST)

            reserva.estado = 'check_in'
            reserva.fecha_entrada_real = timezone.now()
            reserva.save(update_fields=['estado', 'fecha_entrada_real'])

            habitacion.estado = 'ocupada'
            habitacion.save(update_fields=['estado'])

            registrar_actividad('check_in', f"Check-in procesado en H-{habitacion.numero}", request.user, reserva, habitacion, reserva.huesped)
            return Response({'message': 'Check-in procesado exitosamente.', 'estado_reserva': reserva.estado})
            
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ejecutar_checkout(request, pk):
    """ RF05: Procesa el Check-out garantizando la liquidación total de saldos. """
    try:
        with transaction.atomic():
            reserva = Reserva.objects.select_related('habitacion', 'huesped').select_for_update().get(pk=pk)
            
            if reserva.estado != 'check_in' and reserva.estado != 'pagada':
                return Response({'error': 'La reserva no se encuentra en estado activo de hospedaje.'}, status=status.HTTP_400_BAD_REQUEST)

            if reserva.saldo_pendiente > 0:
                return Response({
                    'error': 'Facturación pendiente', 
                    'saldo_pendiente': float(reserva.saldo_pendiente),
                    'detalle': 'El huésped tiene deudas de consumos o noches. Registre el pago completo antes de dar salida.'
                }, status=status.HTTP_400_BAD_REQUEST)

            reserva.estado = 'check_out'
            reserva.fecha_salida_real = timezone.now()
            reserva.save(update_fields=['estado', 'fecha_salida_real'])

            # Pasa automáticamente a limpieza (Flujo operativo estándar)
            habitacion = reserva.habitacion
            habitacion.estado = 'sucia'
            habitacion.save(update_fields=['estado'])

            registrar_actividad('check_out', f"Check-out procesado. H-{habitacion.numero} liberada a limpieza.", request.user, reserva, habitacion, reserva.huesped)
            return Response({'message': 'Check-out finalizado. Habitación marcada para limpieza.'})
            
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def consumos_list(request):
    """ RF07: Registra y lista consumos adicionales de manera paginada. """
    if request.method == 'GET':
        qs = ConsumoInSitu.objects.select_related('reserva', 'producto').all().order_by('-fecha')
        reserva_id = request.query_params.get('reserva')
        if reserva_id:
            qs = qs.filter(reserva_id=reserva_id)
            
        return paginar_queryset_funcion(request, qs, ConsumoSerializer, page_size=20)

    if request.method == 'POST':
        reserva_id = request.data.get('reserva')
        producto_id = request.data.get('producto')
        cantidad = int(request.data.get('cantidad', 1))

        from apps.inventario.models import Producto
        try:
            with transaction.atomic():
                reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
                producto = Producto.objects.select_for_update().get(pk=producto_id, activo=True)

                if producto.stock_actual < cantidad:
                    return Response({'error': f'Stock insuficiente de {producto.nombre}. Disponible: {producto.stock_actual}'}, status=status.HTTP_400_BAD_REQUEST)

                # Descontar stock usando la lógica encapsulada que creamos en el módulo de inventario
                producto.stock_actual -= cantidad
                producto.sin_stock = (producto.stock_actual == 0)
                producto.stock_bajo = (producto.stock_actual <= producto.stock_minimo and producto.stock_actual > 0)
                producto.save(update_fields=['stock_actual', 'sin_stock', 'stock_bajo'])

                # Calcular subtotal denormalizado
                precio_unitario = producto.precio_venta
                subtotal = precio_unitario * cantidad

                consumo = ConsumoInSitu.objects.create(
                    reserva=reserva, producto=producto, cantidad=cantidad,
                    precio_unitario=precio_unitario, subtotal=subtotal
                )

                # Incrementar deuda en la reserva
                reserva.monto_total += subtotal
                reserva.save(update_fields=['monto_total'])

                registrar_actividad('consumo', f"Consumo cargado: {cantidad}x {producto.nombre} a Reserva #{reserva.id}", request.user, reserva, reserva.habitacion, reserva.huesped)
                return Response(ConsumoSerializer(consumo).data, status=status.HTTP_201_CREATED)

        except (Reserva.DoesNotExist, Producto.DoesNotExist):
            return Response({'error': 'Reserva o Producto no válidos.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def actividades_recientes(request):
    """ Retorna la bitácora unificada de auditoría del hotel (Timeline) paginada. """
    qs = Actividad.objects.select_related('usuario', 'habitacion', 'huesped').all().order_by('-fecha')
    return paginar_queryset_funcion(request, qs, ActividadSerializer, page_size=20)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reserva_detail(request, pk):
    """
    Controlador senior para obtener, actualizar o eliminar una reserva específica.
    Aplica JOINs explícitos para optimizar la carga del detalle en el frontend.
    """
    try:
        if request.method == 'GET':
            # BLINDADO SQL N+1: Cargamos de un solo golpe los datos relacionales clave del hotel
            reserva = Reserva.objects.select_related('huesped', 'habitacion', 'habitacion__tipo')\
                                    .prefetch_related('consumos', 'pagos')\
                                    .get(pk=pk)
            serializer = ReservaListSerializer(reserva)  # Usamos ListSerializer para entregar el objeto enriquecido
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            with transaction.atomic():
                reserva = Reserva.objects.select_for_update().get(pk=pk)
    except Reserva.DoesNotExist:
        return Response({'error': 'La reserva solicitada no existe.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ReservaSerializer(reserva, data=request.data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                reserva_editada = serializer.save()
                registrar_actividad(
                    'reserva_actualizada', 
                    f"Reserva #{reserva_editada.id} modificada por el usuario.", 
                    request.user, reserva_editada, reserva_editada.habitacion, reserva_editada.huesped
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador del sistema puede eliminar reservas.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Regla de negocio estricta: No se borran estadías en curso o deudas activas
        if reserva.estado in ['check_in', 'pagada']:
            return Response({
                'error': f'Restricción de Auditoría: No se puede eliminar una reserva en estado: {reserva.estado}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Liberamos la habitación antes de borrar el registro si estaba bloqueada
        with transaction.atomic():
            if reserva.habitacion and reserva.habitacion.estado == 'ocupada' and reserva.estado == 'sin_pagar':
                reserva.habitacion.estado = 'libre'
                reserva.habitacion.save(update_fields=['estado'])
                
            registrar_actividad(
                'reserva_eliminada', 
                f"Reserva #{reserva.id} removida del sistema por el Administrador.", 
                request.user, None, reserva.habitacion, reserva.huesped
            )
            reserva.delete()
            
        return Response({'message': 'Reserva eliminada exitosamente del ecosistema.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def registrar_no_show(request, pk):
    """
    RF04/RF05: Registra el No-Show de una reserva si el huésped no se presenta.
    Libera la habitación de forma atómica y actualiza el estado de la estadía.
    """
    try:
        with transaction.atomic():
            # Bloqueamos la fila de la reserva para evitar escrituras concurrentes
            reserva = Reserva.objects.select_related('habitacion', 'huesped').select_for_update().get(pk=pk)
            
            # Solo se puede marcar No-Show si la reserva estaba confirmada o sin pagar,
            # pero definitivamente NO si ya están hospedados (check_in) o ya se fueron (check_out)
            if reserva.estado in ['check_in', 'check_out', 'no_show', 'cancelada']:
                return Response(
                    {'error': f'No es posible marcar como No-Show una reserva en estado: {reserva.estado}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            reserva.estado = 'no_show'
            reserva.save(update_fields=['estado'])

            # Si la habitación estaba vinculada y guardaba estado de compromiso, la liberamos
            habitacion = reserva.habitacion
            if habitacion and habitacion.estado == 'ocupada':
                # Nota: Si el flujo de tu hotel dicta que pasa a 'sucia' o 'libre', colócalo aquí.
                # Lo estándar para una habitación que nunca se usó es dejarla 'libre' directamente.
                habitacion.estado = 'libre'
                habitacion.save(update_fields=['estado'])

            registrar_actividad(
                'no_show', 
                f"Reserva #{reserva.id} declarada No-Show. H-{habitacion.numero if habitacion else 'N/A'} liberada.", 
                request.user, reserva, habitacion, reserva.huesped
            )
            
            return Response({
                'message': 'Reserva marcada como No-Show exitosamente.',
                'estado_reserva': reserva.estado
            }, status=status.HTTP_200_OK)
            
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def agregar_consumo(request, pk):
    """
    RF07: Endpoint dedicado para cargar consumos vinculados directamente a través del ID de la reserva.
    Realiza la deducción atómica de inventario y actualiza la cuenta del huésped.
    """
    producto_id = request.data.get('producto')
    cantidad = int(request.data.get('cantidad', 1))

    if not producto_id:
        return Response({'error': 'El parámetro "producto" es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

    from apps.inventario.models import Producto
    try:
        with transaction.atomic():
            # Bloqueo de filas simultáneas para evitar inconsistencias de saldo o sobreventa de stock
            reserva = Reserva.objects.select_for_update().get(pk=pk)
            producto = Producto.objects.select_for_update().get(pk=producto_id, activo=True)

            if producto.stock_actual < cantidad:
                return Response(
                    {'error': f'Stock insuficiente de {producto.nombre}. Disponible en inventario: {producto.stock_actual}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Reducción de existencias físicas
            producto.stock_actual -= cantidad
            producto.sin_stock = (producto.stock_actual == 0)
            producto.stock_bajo = (producto.stock_actual <= producto.stock_minimo and producto.stock_actual > 0)
            producto.save(update_fields=['stock_actual', 'sin_stock', 'stock_bajo'])

            # Multiplicación limpia de valores denormalizados
            precio_unitario = producto.precio_venta
            subtotal = precio_unitario * cantidad

            # Persistencia de la línea de consumo in-situ
            consumo = ConsumoInSitu.objects.create(
                reserva=reserva, 
                producto=producto, 
                cantidad=cantidad,
                precio_unitario=precio_unitario, 
                subtotal=subtotal
            )

            # Mutación del estado financiero consolidado de la estadía
            reserva.monto_total += subtotal
            reserva.save(update_fields=['monto_total'])

            registrar_actividad(
                'consumo', 
                f"Consumo cargado mediante endpoint dedicado: {cantidad}x {producto.nombre} a Reserva #{reserva.id}", 
                request.user, reserva, reserva.habitacion, reserva.huesped
            )
            
            return Response(ConsumoSerializer(consumo).data, status=status.HTTP_201_CREATED)

    except (Reserva.DoesNotExist, Producto.DoesNotExist):
        return Response({'error': 'La reserva o el producto seleccionado no son válidos.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cambiar_habitacion(request, pk):
    """
    RF04/RF05: Ejecuta el cambio de habitación de una reserva activa o confirmada.
    Libera la habitación previa, bloquea la nueva de forma atómica y recalcula cargos si aplica.
    """
    nueva_habitacion_id = request.data.get('nueva_habitacion')
    motivo = request.data.get('motivo', 'Cambio solicitado por el huésped')

    if not nueva_habitacion_id:
        return Response(
            {'error': 'El parámetro "nueva_habitacion" es obligatorio.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            # 1. Bloqueamos la fila de la reserva para evitar escrituras concurrentes
            reserva = Reserva.objects.select_related('habitacion', 'huesped').select_for_update().get(pk=pk)
            
            # Restricción lógica: No se cambia de habitación si la reserva ya finalizó o se canceló
            if reserva.estado in ['check_out', 'no_show', 'cancelada']:
                return Response(
                    {'error': f'No es posible mudar de habitación una reserva en estado: {reserva.estado}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            habitacion_antigua = reserva.habitacion

            # 2. Bloqueamos la fila de la nueva habitación para certificar disponibilidad absoluta
            nueva_habitacion = Habitacion.objects.select_for_update().get(pk=nueva_habitacion_id)

            if nueva_habitacion.id == habitacion_antigua.id:
                return Response(
                    {'error': 'La nueva habitación debe ser diferente a la actual.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if nueva_habitacion.estado in ['ocupada', 'mantenimiento']:
                return Response(
                    {'error': f'La habitación H-{nueva_habitacion.numero} no está disponible (Estado: {nueva_habitacion.estado}).'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. Mutación Transaccional de Estados de Infraestructura
            # Si el huésped ya estaba hospedado (check_in), la habitación vieja pasa a estar sucia
            if reserva.estado == 'check_in':
                if habitacion_antigua:
                    habitacion_antigua.estado = 'sucia'
                    habitacion_antigua.save(update_fields=['estado'])
                nueva_habitacion.estado = 'ocupada'
            
            # Si era una reserva futura confirmada/sin pagar, la vieja queda libre directamente
            else:
                if habitacion_antigua:
                    habitacion_antigua.estado = 'libre'
                    habitacion_antigua.save(update_fields=['estado'])
                # Mantenemos el estado de la nueva según el flujo del hotel o la dejamos pre-bloqueada si aplica

            nueva_habitacion.save(update_fields=['estado'])

            # 4. Asignación y Registro
            num_antiguo = habitacion_antigua.numero if habitacion_antigua else "Ninguna"
            reserva.habitacion = nueva_habitacion
            reserva.save(update_fields=['habitacion'])

            # Bitácora de auditoría unificada
            registrar_actividad(
                'cambio_habitacion', 
                f"Mudanza: H-{num_antiguo} -> H-{nueva_habitacion.numero}. Motivo: {motivo}", 
                request.user, reserva, nueva_habitacion, reserva.huesped
            )

            return Response({
                'message': 'Cambio de habitación procesado con éxito absoluto.',
                'reserva_id': reserva.id,
                'habitacion_antigua_estado': habitacion_antigua.estado if habitacion_antigua else None,
                'nueva_habitacion_numero': nueva_habitacion.numero,
                'nueva_habitacion_estado': nueva_habitacion.estado
            }, status=status.HTTP_200_OK)

    except (Reserva.DoesNotExist, Habitacion.DoesNotExist):
        return Response({'error': 'La reserva o la nueva habitación especificada no existen.'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cancelar_reserva(request, pk):
    """
    Cancela una reserva (estado 'cancelada') y libera la habitación si estaba ocupada.
    """
    try:
        with transaction.atomic():
            reserva = Reserva.objects.select_related('habitacion').select_for_update().get(pk=pk)
            
            if reserva.estado in ['check_out', 'cancelada', 'no_show']:
                return Response({'error': f'No se puede cancelar una reserva en estado {reserva.estado}'}, status=status.HTTP_400_BAD_REQUEST)
            
            reserva.estado = 'cancelada'
            reserva.save(update_fields=['estado'])
            
            # Liberar habitación si estaba ocupada o reservada
            habitacion = reserva.habitacion
            if habitacion and habitacion.estado == 'ocupada':
                habitacion.estado = 'libre'
                habitacion.save(update_fields=['estado'])
            
            registrar_actividad(
                tipo='cancelacion',
                descripcion=f'Reserva #{reserva.id} cancelada',
                usuario=request.user,
                reserva=reserva,
                habitacion=habitacion,
                huesped=reserva.huesped
            )
            
            return Response({'message': 'Reserva cancelada exitosamente'}, status=status.HTTP_200_OK)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)