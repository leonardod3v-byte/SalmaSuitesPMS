from .models import Huesped
from apps.reservaciones.models import Reservacion

def listar_huespedes():
    return Huesped.objects.all()

def obtener_huesped(pk: int) -> Huesped:
    return Huesped.objects.get(pk=pk)

def crear_huesped(**datos) -> Huesped:
    # El serializador se encarga de la validación de unicidad
    huesped = Huesped(**datos)
    huesped.save()
    return huesped

def actualizar_huesped(huesped: Huesped, datos: dict) -> Huesped:
    for campo, valor in datos.items():
        if campo == 'edad' and valor is not None:
            # La edad se recalculará en el save, pero si se envía manualmente se ignora
            continue
        setattr(huesped, campo, valor)
    huesped.save()
    return huesped

def validar_disponibilidad_huesped(huesped_id: int) -> bool:
    """
    Retorna True si el huésped NO tiene reservación activa (Confirmada o EnCurso).
    """
    tiene_activa = Reservacion.objects.filter(
        id_huesped_titular_id=huesped_id,
        estado__in=['Confirmada', 'EnCurso']
    ).exists()
    # También como acompañante
    tiene_activa |= Reservacion.objects.filter(
        huespedes_secundarios__id_huesped_id=huesped_id,
        huespedes_secundarios__rol='Acompañante',
        estado__in=['Confirmada', 'EnCurso']
    ).exists()
    return not tiene_activa