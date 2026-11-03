from .models import Huesped
from apps.reservaciones.models import Reservacion

def listar_huespedes():
    return Huesped.objects.all()

def obtener_huesped(pk: int) -> Huesped:
    return Huesped.objects.get(pk=pk)

def crear_huesped(**datos) -> Huesped:
    huesped = Huesped(**datos)
    huesped.save()
    return huesped

def actualizar_huesped(huesped: Huesped, datos: dict) -> Huesped:
    for campo, valor in datos.items():
        if campo == 'edad' and valor is not None:
            continue
        setattr(huesped, campo, valor)
    huesped.save()
    return huesped

def validar_disponibilidad_huesped(huesped_id):
    """Un huésped está disponible si NO tiene reservas EnCurso."""
    from apps.reservaciones.models import Reservacion
    es_titular_activo = Reservacion.objects.filter(
        id_huesped_titular_id=huesped_id,
        estado='EnCurso'
    ).exists()
    if es_titular_activo:
        return False
    from apps.reservaciones.models import ReservacionHuespedes
    es_acompanante_activo = ReservacionHuespedes.objects.filter(
        id_huesped_id=huesped_id,
        id_reservacion__estado='EnCurso',
        rol='Acompañante'
    ).exists()
    return not es_acompanante_activo
