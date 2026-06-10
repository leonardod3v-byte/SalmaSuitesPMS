from django.db import transaction
from .models import Habitacion

def listar_habitaciones(estado=None):
    qs = Habitacion.objects.all()
    if estado:
        qs = qs.filter(estado=estado)
    return qs

def obtener_habitacion(pk: int) -> Habitacion:
    return Habitacion.objects.get(pk=pk)

def crear_habitacion(**datos) -> Habitacion:
    habitacion = Habitacion(**datos)
    habitacion.full_clean()
    habitacion.save()
    return habitacion

def actualizar_habitacion(habitacion: Habitacion, datos: dict) -> Habitacion:
    for campo, valor in datos.items():
        setattr(habitacion, campo, valor)
    habitacion.full_clean()
    habitacion.save()
    return habitacion

def cambiar_estado(habitacion: Habitacion, nuevo_estado: str, notas: str = '',
                es_emergencia: bool = False, pasar_a_limpia: bool = False):
    """
    Lógica central de transiciones de estado.
    Las transiciones automáticas (check‑in/check‑out) son llamadas desde el servicio de reservaciones.
    Las manuales desde los endpoints de recepción.
    """
    estado_actual = habitacion.estado

    # Validaciones según transiciones
    if nuevo_estado == 'Ocupada':
        if estado_actual != 'Limpia':
            raise ValueError('Solo se puede ocupar una habitación que esté Limpia.')
    elif nuevo_estado == 'Sucia':
        if estado_actual not in ['Ocupada', 'Mantenimiento', 'Obra']:
            raise ValueError('Solo se puede ensuciar una habitación que esté Ocupada, en Mantenimiento o en Obra.')
    elif nuevo_estado == 'Limpia':
        if estado_actual != 'Sucia':
            raise ValueError('Solo se puede marcar como limpia una habitación que esté Sucia.')
    elif nuevo_estado in ['Mantenimiento', 'Obra']:
        if estado_actual == 'Ocupada' and not es_emergencia:
            raise ValueError('No se puede enviar a mantenimiento/obra una habitación ocupada a menos que sea una emergencia.')
        if estado_actual == 'Ocupada' and es_emergencia:
            # En caso de emergencia se permite, pero se debe manejar la reubicación del huésped externamente
            pass
    else:
        raise ValueError(f'Estado no reconocido: {nuevo_estado}')

    # Si se finaliza mantenimiento/obra y se decide pasar directamente a limpia
    if estado_actual in ['Mantenimiento', 'Obra'] and nuevo_estado == 'Limpia' and pasar_a_limpia:
        pass  # permitido
    elif estado_actual in ['Mantenimiento', 'Obra'] and nuevo_estado == 'Sucia':
        pass  # permitido
    elif estado_actual in ['Mantenimiento', 'Obra'] and nuevo_estado not in ['Sucia', 'Limpia']:
        raise ValueError('Al finalizar mantenimiento/obra la habitación debe pasar a Sucia o Limpia.')

    with transaction.atomic():
        habitacion.estado = nuevo_estado
        if notas:
            habitacion.notas = notas
        habitacion.save()
    return habitacion

def marcar_como_limpia(habitacion: Habitacion):
    return cambiar_estado(habitacion, 'Limpia')

def iniciar_mantenimiento(habitacion: Habitacion, notas: str, es_emergencia: bool = False):
    return cambiar_estado(habitacion, 'Mantenimiento', notas=notas, es_emergencia=es_emergencia)

def iniciar_obra(habitacion: Habitacion, notas: str, es_emergencia: bool = False):
    return cambiar_estado(habitacion, 'Obra', notas=notas, es_emergencia=es_emergencia)

def finalizar_mantenimiento_obra(habitacion: Habitacion, pasar_a_limpia: bool = False):
    nuevo_estado = 'Limpia' if pasar_a_limpia else 'Sucia'
    return cambiar_estado(habitacion, nuevo_estado, pasar_a_limpia=pasar_a_limpia)

def esta_disponible(habitacion_id: int) -> bool:
    return Habitacion.objects.filter(pk=habitacion_id, estado='Limpia').exists()

def listar_disponibles():
    return Habitacion.objects.filter(estado='Limpia')