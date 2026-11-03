from .models import Configuracion

def obtener_configuracion():
    return {c.clave: c.valor for c in Configuracion.objects.all()}

def guardar_configuracion(clave, valor):
    Configuracion.objects.update_or_create(clave=clave, defaults={'valor': valor})
