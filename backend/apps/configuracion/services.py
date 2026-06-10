from .models import Configuracion, ColoresTipoCliente, ColoresEstadoHabitacion

def obtener_configuracion():
    return {c.clave: c.valor for c in Configuracion.objects.all()}

def guardar_configuracion(clave, valor):
    Configuracion.objects.update_or_create(clave=clave, defaults={'valor': valor})

def listar_colores_tipo_cliente():
    return ColoresTipoCliente.objects.all()

def guardar_color_tipo_cliente(tipo_cliente_profesion, color):
    ColoresTipoCliente.objects.update_or_create(
        tipo_cliente_profesion=tipo_cliente_profesion,
        defaults={'color': color}
    )

def listar_colores_estado_habitacion():
    return ColoresEstadoHabitacion.objects.all()

def guardar_color_estado_habitacion(estado, color):
    ColoresEstadoHabitacion.objects.update_or_create(
        estado=estado,
        defaults={'color': color}
    )