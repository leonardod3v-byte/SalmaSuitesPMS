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
                es_emergencia: bool = False):
    """
    Lógica central de transiciones de estado.
    Estados válidos: Disponible, Ocupada, Limpieza, Mantenimiento, Obra.
    """
    estado_actual = habitacion.estado

    if nuevo_estado == 'Ocupada':
        if estado_actual != 'Disponible':
            raise ValueError('Solo se puede ocupar una habitación Disponible.')
    elif nuevo_estado == 'Limpieza':
        if estado_actual not in ['Ocupada', 'Mantenimiento', 'Obra']:
            raise ValueError('Solo se puede enviar a Limpieza una habitación Ocupada, en Mantenimiento o en Obra.')
    elif nuevo_estado == 'Disponible':
        if estado_actual != 'Limpieza':
            raise ValueError('Solo se puede marcar como Disponible una habitación que esté en Limpieza.')
    elif nuevo_estado in ['Mantenimiento', 'Obra']:
        if estado_actual == 'Ocupada' and not es_emergencia:
            raise ValueError('No se puede enviar a mantenimiento/obra una habitación ocupada sin marcar emergencia.')
    else:
        raise ValueError(f'Estado no reconocido: {nuevo_estado}')

    with transaction.atomic():
        habitacion.estado = nuevo_estado
        if notas:
            habitacion.notas = notas
        habitacion.save()
    return habitacion

def marcar_como_disponible(habitacion: Habitacion):
    """Termina la limpieza y deja la habitación lista para nuevos huéspedes."""
    return cambiar_estado(habitacion, 'Disponible')

def iniciar_mantenimiento(habitacion: Habitacion, notas: str, es_emergencia: bool = False):
    return cambiar_estado(habitacion, 'Mantenimiento', notas=notas, es_emergencia=es_emergencia)

def iniciar_obra(habitacion: Habitacion, notas: str, es_emergencia: bool = False):
    return cambiar_estado(habitacion, 'Obra', notas=notas, es_emergencia=es_emergencia)

def finalizar_mantenimiento_obra(habitacion: Habitacion):
    """Al terminar mantenimiento/obra, pasa a Limpieza (para que la limpien antes de reusar)."""
    return cambiar_estado(habitacion, 'Limpieza')

def esta_disponible(habitacion_id: int) -> bool:
    return Habitacion.objects.filter(pk=habitacion_id, estado='Disponible').exists()

def listar_disponibles():
    return Habitacion.objects.filter(estado='Disponible')
