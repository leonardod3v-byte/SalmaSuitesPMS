from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from datetime import datetime

from .models import Reservacion, Consumo, Pago
from .serializers import ReservacionSerializer, ConsumoSerializer, PagoSerializer
from . import services

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lista_reservaciones(request):
    if request.method == 'GET':
        qs = Reservacion.objects.select_related('id_huesped_titular', 'id_habitacion').all()
        
        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        
        if desde and hasta:
            # Reservas que se solapan con el rango [desde, hasta]
            qs = qs.filter(
                fecha_entrada__lt=hasta,
                fecha_salida__gt=desde
            )
        elif desde:
            qs = qs.filter(fecha_salida__gt=desde)
        elif hasta:
            qs = qs.filter(fecha_entrada__lt=hasta)
        
        serializer = ReservacionSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        # Convertir fechas de string a date
        from datetime import datetime
        data['fecha_entrada'] = datetime.strptime(data['fecha_entrada'], '%Y-%m-%d').date()
        data['fecha_salida'] = datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date()
        
        acompanantes = data.pop('acompanantes', [])
        monto_abonado = data.pop('monto_abonado', '0.00')
        try:
            reserva = services.crear_reservacion(
                id_huesped_titular=data['id_huesped_titular'],
                id_habitacion=data['id_habitacion'],
                fecha_entrada=data['fecha_entrada'],
                fecha_salida=data['fecha_salida'],
                modalidad_pago=data.get('modalidad_pago', 'Contado'),
                requiere_factura=data.get('requiere_factura', False),
                acompanantes=acompanantes,
                metodo_pago_inicial=data.get('metodo_pago_inicial'),
                numero_referencia_inicial=data.get('numero_referencia_inicial', ''),
                monto_abonado=monto_abonado,
                usuario=request.user
            )
            return Response(ReservacionSerializer(reserva).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error': f'Falta campo requerido: {e}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def detalle_reservacion(request, pk):
    reserva = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'GET':
        serializer = ReservacionSerializer(reserva)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        # Solo se pueden editar ciertos campos (fechas, factura, etc.) pero el estado se maneja con endpoints específicos
        # Por simplicidad, permitimos actualización parcial de campos no calculados.
        allowed_fields = ['requiere_factura', 'acta', 'motivo_cancelacion']
        data = request.data
        for field in allowed_fields:
            if field in data:
                setattr(reserva, field, data[field])
        reserva.save()
        return Response(ReservacionSerializer(reserva).data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkin_reservacion(request, pk):
    try:
        reserva = services.realizar_checkin(pk, request.user)
        return Response(ReservacionSerializer(reserva).data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_reservacion(request, pk):
    try:
        reserva = services.realizar_checkout(pk, request.user)
        return Response(ReservacionSerializer(reserva).data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_reservacion(request, pk):
    motivo = request.data.get('motivo', '')
    acta = request.data.get('acta', '')
    try:
        reserva = services.cancelar_reservacion(pk, motivo, acta, request.user)
        return Response(ReservacionSerializer(reserva).data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def noshow_reservacion(request, pk):
    motivo = request.data.get('motivo', '')
    acta = request.data.get('acta', '')
    try:
        reserva = services.marcar_noshow(pk, motivo, acta, request.user)
        return Response(ReservacionSerializer(reserva).data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen_checkout(request, pk):
    reserva = get_object_or_404(Reservacion, pk=pk)
    if reserva.estado != 'EnCurso':
        return Response({'error': 'La reserva no está en curso'}, status=status.HTTP_400_BAD_REQUEST)
    resumen = services.obtener_resumen_para_checkout(reserva)
    return Response(resumen)


# Consumos de una reservación
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def consumos_reservacion(request, pk):
    reserva = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'GET':
        consumos = reserva.consumos.all()
        serializer = ConsumoSerializer(consumos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        try:
            producto = None
            if data.get('producto_id'):
                from apps.inventario.models import Producto
                producto = get_object_or_404(Producto, pk=data['producto_id'])

            consumo = services.agregar_consumo(
                reserva_id=pk,
                tipo=data['tipo_consumo'],
                descripcion=data.get('descripcion', ''),
                cantidad=data['cantidad'],
                precio_unitario=data['precio_unitario'],
                producto=producto,
                usuario=request.user
            )
            return Response(ConsumoSerializer(consumo).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error': f'Falta campo requerido: {e}'}, status=status.HTTP_400_BAD_REQUEST)


# Pagos de una reservación
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pagos_reservacion(request, pk):
    reserva = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'GET':
        pagos = reserva.pagos.all()
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        try:
            pago = services.registrar_pago_extra(
                reserva_id=pk,
                monto=data['monto'],
                metodo_pago=data['metodo_pago'],
                numero_referencia=data.get('numero_referencia', ''),
                usuario=request.user
            )
            return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error': f'Falta campo requerido: {e}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saldo_reservacion(request, pk):
    reserva = get_object_or_404(Reservacion, pk=pk)
    return Response({
        'total_habitacion': str(reserva.total_habitacion),
        'total_consumos': str(reserva.monto_total_consumos),
        'total_final': str(reserva.monto_total_final),
        'monto_pagado': str(reserva.monto_pagado),
        'saldo_pendiente': str(reserva.saldo_pendiente),
    })