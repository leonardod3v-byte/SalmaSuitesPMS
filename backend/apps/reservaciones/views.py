from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q

from .models import Reserva, Consumo, Actividad
from .serializers import (
    ReservaSerializer, ReservaListSerializer,
    ConsumoSerializer, ActividadSerializer
)
from apps.habitaciones.models import Habitacion


def registrar_actividad(tipo, descripcion, usuario, reserva=None, habitacion=None, huesped=None, detalle=''):
    """
    Función auxiliar para registrar actividades en el timeline del dashboard.
    Se llama desde cualquier vista que genere una acción importante.
    """
    Actividad.objects.create(
        tipo=tipo,
        descripcion=descripcion,
        detalle=detalle,
        reserva=reserva,
        habitacion=habitacion,
        huesped=huesped,
        usuario=usuario
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reservas_list(request):
    """
    GET: Lista reservas con filtros opcionales.
    POST: Crea una nueva reserva.
    """
    if request.method == 'GET':
        qs = Reserva.objects.select_related('huesped', 'habitacion').all()

        estado = request.query_params.get('estado')
        fecha = request.query_params.get('fecha')
        huesped_id = request.query_params.get('huesped')
        search = request.query_params.get('search')

        if estado:
            qs = qs.filter(estado=estado)
        if fecha:
            qs = qs.filter(Q(fecha_entrada=fecha) | Q(fecha_salida=fecha))
        if huesped_id:
            qs = qs.filter(huesped_id=huesped_id)
        if search:
            qs = qs.filter(
                Q(huesped__nombre__icontains=search) |
                Q(huesped__apellido__icontains=search) |
                Q(huesped__numero_documento__icontains=search) |
                Q(habitacion__numero__icontains=search)
            )

        serializer = ReservaListSerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ReservaSerializer(data=request.data)
        if serializer.is_valid():
            reserva = serializer.save(creada_por=request.user)
            
            # Asignar tipo_cliente desde la profesión del huésped si no viene
            if not reserva.tipo_cliente and reserva.huesped.profesion:
                mapeo = {
                    'particular': 'particular',
                    'militar': 'militar',
                    'politico': 'politico',
                    'artista': 'artista',
                    'empresarial': 'empresarial',
                    'deportista': 'deportista',
                    'diplomatico': 'diplomatico',
                    'medico': 'medico',
                    'religioso': 'religioso',
                    'turista': 'turista',
                    'ejecutivo_ventas': 'ejecutivo_ventas',
                    'comerciante': 'comerciante',
                }
                profesion_key = reserva.huesped.profesion.lower()
                reserva.tipo_cliente = mapeo.get(profesion_key, 'particular')
                reserva.save()
            
            registrar_actividad(
                tipo='reserva_creada',
                descripcion=f'Reserva creada para {reserva.huesped.nombre_completo}',
                usuario=request.user,
                reserva=reserva,
                habitacion=reserva.habitacion,
                huesped=reserva.huesped
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reserva_detail(request, pk):
    """
    GET: Detalle completo de una reserva con consumos.
    PUT: Editar reserva (estado, fechas, pago, etc.).
    DELETE: Cancelar reserva (solo admin).
    """
    try:
        reserva = Reserva.objects.select_related(
            'huesped', 'habitacion', 'creada_por'
        ).prefetch_related('consumos').get(pk=pk)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=404)

    if request.method == 'GET':
        serializer = ReservaSerializer(reserva)
        return Response(serializer.data)

    if request.method == 'PUT':
        estado_anterior = reserva.estado
        serializer = ReservaSerializer(reserva, data=request.data, partial=True)

        if serializer.is_valid():
            reserva_actualizada = serializer.save()
            nuevo_estado = serializer.validated_data.get('estado', estado_anterior)

            # Registrar actividad según el nuevo estado
            if nuevo_estado != estado_anterior:
                tipo_actividad = {
                    'check_in': 'check_in',
                    'check_out': 'check_out',
                    'cancelada': 'reserva_cancelada',
                    'no_show': 'no_show',
                }.get(nuevo_estado, 'reserva_modificada')

                registrar_actividad(
                    tipo=tipo_actividad,
                    descripcion=f'{nuevo_estado.replace("_", " ").title()} - H-{reserva.habitacion.numero}',
                    usuario=request.user,
                    reserva=reserva_actualizada,
                    habitacion=reserva.habitacion,
                    huesped=reserva.huesped
                )

                # Si es check-in, marcar habitación como ocupada
                if nuevo_estado == 'check_in':
                    reserva.habitacion.estado = 'ocupada'
                    reserva.habitacion.save()

                # Si es check-out, marcar habitación como sucia
                if nuevo_estado == 'check_out':
                    reserva.habitacion.estado = 'limpia'
                    reserva.habitacion.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar reservas.'}, status=403)
        reserva.delete()
        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def registrar_no_show(request, pk):
    """
    RF08: Registra un acta de No-Show para una reserva.
    Requiere motivo en el body: { "motivo": "El huésped no se presentó..." }
    """
    try:
        reserva = Reserva.objects.get(pk=pk)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=404)

    motivo = request.data.get('motivo', '')
    if not motivo:
        return Response({'error': 'El motivo es requerido para el acta No-Show.'}, status=400)

    reserva.estado = 'no_show'
    reserva.no_show_motivo = motivo
    reserva.no_show_fecha = timezone.now()
    reserva.no_show_registrado_por = request.user
    reserva.save()

    registrar_actividad(
        tipo='no_show',
        descripcion=f'No-Show registrado - H-{reserva.habitacion.numero}',
        detalle=motivo,
        usuario=request.user,
        reserva=reserva,
        habitacion=reserva.habitacion,
        huesped=reserva.huesped
    )

    return Response({'message': 'Acta No-Show registrada correctamente.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def agregar_consumo(request, pk):
    """
    RF06: Agrega un consumo a una reserva activa.
    Body: { "producto": "Agua mineral", "cantidad": 2, "precio_unitario": 1.50 }
    """
    try:
        reserva = Reserva.objects.get(pk=pk)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=404)

    if reserva.estado not in ['confirmada', 'pagada', 'check_in']:
        return Response({'error': 'Solo se pueden agregar consumos a reservas activas.'}, status=400)

    serializer = ConsumoSerializer(data=request.data)
    if serializer.is_valid():
        consumo = serializer.save(reserva=reserva, registrado_por=request.user)

        registrar_actividad(
            tipo='consumo',
            descripcion=f'Consumo: {consumo.producto} - H-{reserva.habitacion.numero}',
            detalle=f'Cantidad: {consumo.cantidad} | Total: ${consumo.total}',
            usuario=request.user,
            reserva=reserva,
            habitacion=reserva.habitacion,
            huesped=reserva.huesped
        )

        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cambiar_habitacion(request, pk):
    """
    RF05: Cambia la habitación de una reserva activa.
    Body: { "nueva_habitacion_id": 5, "motivo": "Solicitud del huésped" }
    """
    try:
        reserva = Reserva.objects.get(pk=pk)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada.'}, status=404)

    nueva_hab_id = request.data.get('nueva_habitacion_id')
    if not nueva_hab_id:
        return Response({'error': 'nueva_habitacion_id es requerido.'}, status=400)

    try:
        nueva_habitacion = Habitacion.objects.get(pk=nueva_hab_id)
    except Habitacion.DoesNotExist:
        return Response({'error': 'Habitación destino no encontrada.'}, status=404)

    if nueva_habitacion.estado not in ['libre', 'limpia']:
        return Response({'error': f'La habitación {nueva_habitacion.numero} no está disponible.'}, status=400)

    # Guardar habitación original si es el primer cambio
    if not reserva.habitacion_original:
        reserva.habitacion_original = reserva.habitacion

    habitacion_anterior = reserva.habitacion

    # Liberar habitación anterior y ocupar la nueva
    habitacion_anterior.estado = 'sucia'
    habitacion_anterior.save()

    nueva_habitacion.estado = 'ocupada'
    nueva_habitacion.save()

    reserva.habitacion = nueva_habitacion
    reserva.save()

    registrar_actividad(
        tipo='cambio_habitacion',
        descripcion=f'Cambio H-{habitacion_anterior.numero} → H-{nueva_habitacion.numero}',
        detalle=request.data.get('motivo', ''),
        usuario=request.user,
        reserva=reserva,
        habitacion=nueva_habitacion,
        huesped=reserva.huesped
    )

    return Response({'message': f'Habitación cambiada a H-{nueva_habitacion.numero} exitosamente.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def actividades_recientes(request):
    """
    RF02: Últimas actividades para el timeline del dashboard.
    """
    actividades = Actividad.objects.select_related(
        'usuario', 'habitacion', 'huesped'
    ).all()[:20]

    serializer = ActividadSerializer(actividades, many=True)
    return Response(serializer.data)