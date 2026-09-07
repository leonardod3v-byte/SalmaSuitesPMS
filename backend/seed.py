import os
import sys
import django
from datetime import date
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import User
from apps.habitaciones.models import Habitacion
from apps.huespedes.models import Huesped
from apps.inventario.models import Producto
from apps.configuracion.models import Configuracion, ColoresTipoCliente, ColoresEstadoHabitacion

def crear_usuarios():
    print("Creando usuarios...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            password='admin123',
            role='admin',
            nombre_completo='Leonardo Noa',
            email='leonardonoa803@gmail.com'
        )
        print("  Admin creado.")
    else:
        print("  Admin ya existe.")

    if not User.objects.filter(username='recepcion1').exists():
        User.objects.create_user(
            username='recepcion1',
            password='recepcion123',
            role='recepcionista',
            nombre_completo='María Recepción',
            email='recepcion@salmasuite.com'
        )
        print("  Recepcionista 1 creado.")
    else:
        print("  Recepcionista 1 ya existe.")

    if not User.objects.filter(username='recepcion2').exists():
        User.objects.create_user(
            username='recepcion2',
            password='recepcion123',
            role='recepcionista',
            nombre_completo='Juan Recepción',
            email='juan@salmasuite.com'
        )
        print("  Recepcionista 2 creado.")
    else:
        print("  Recepcionista 2 ya existe.")
    print("OK")

def crear_habitaciones():
    print("Creando habitaciones...")
    datos = [
        ('105', 1, 2, 2, 'Doble Individual',    Decimal('45.00')),
        ('106', 1, 1, 2, 'Doble Matrimonial',   Decimal('55.00')),
        ('107', 1, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('108', 1, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('109', 1, 2, 2, 'Doble Individual',    Decimal('45.00')),
        ('110', 1, 2, 2, 'Doble Individual',    Decimal('45.00')),
        ('111', 1, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('112', 1, 1, 2, 'Doble Matrimonial',   Decimal('55.00')),
        ('113', 1, 3, 3, 'Triple Individual',   Decimal('65.00')),
        ('115', 2, 1, 2, 'Queen',               Decimal('80.00')),
        ('116', 2, 1, 2, 'Queen',               Decimal('80.00')),
        ('117', 2, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('118', 2, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('119', 2, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('120', 2, 1, 2, 'Matrimonial',         Decimal('50.00')),
        ('121', 2, 1, 2, 'Doble Matrimonial',   Decimal('55.00')),
        ('122', 2, 1, 2, 'Doble Matrimonial',   Decimal('55.00')),
        ('114', 2, 1, 2, 'Suite',               Decimal('100.00')),
    ]
    creadas = 0
    for num, piso, camas, cap, tipo, precio in datos:
        _, created = Habitacion.objects.update_or_create(
            numero=num,
            defaults={'piso': piso, 'cantidad_camas': camas,
                    'capacidad_maxima': cap, 'categoria_tipo': tipo,
                    'precio_por_noche': precio, 'estado': 'Limpia'}
        )
        if created:
            creadas += 1
    print(f"  {creadas} nuevas, {len(datos) - creadas} ya existían. Total: {len(datos)}")
    print("OK")

def crear_huespedes():
    print("Creando huéspedes...")
    datos = [
        {'tipo_documento':'V','numero_documento':'12345678','nombres':'Carlos','apellidos':'González',
        'fecha_nacimiento':date(1985,5,15),'nacionalidad':'Venezolana','estado_civil':'Soltero',
        'telefono':'0412-1234567','email':'carlos@email.com','procedencia':'Caracas',
        'tipo_cliente_profesion':'Empresario','categoria':'VIP','credito_autorizado':True,
        'limite_credito':Decimal('500.00'),'observaciones':'Cliente frecuente, prefiere pisos altos.'},
        {'tipo_documento':'E','numero_documento':'98765432','nombres':'Ana','apellidos':'Martínez',
        'fecha_nacimiento':date(1990,8,22),'nacionalidad':'Colombiana','estado_civil':'Casada',
        'telefono':'0414-7654321','email':'ana@email.com','procedencia':'Bogotá',
        'tipo_cliente_profesion':'Turista','categoria':'Estándar','credito_autorizado':False,
        'limite_credito':None,'observaciones':''},
        {'tipo_documento':'V','numero_documento':'11223344','nombres':'Pedro','apellidos':'Ramírez',
        'fecha_nacimiento':date(1975,3,10),'nacionalidad':'Venezolana','estado_civil':'Divorciado',
        'telefono':'0424-1122334','email':'pedro@email.com','procedencia':'Maracaibo',
        'tipo_cliente_profesion':'Militar','categoria':'VIP','credito_autorizado':True,
        'limite_credito':Decimal('1000.00'),'observaciones':'Solicita factura legal siempre.'},
        {'tipo_documento':'V','numero_documento':'22334455','nombres':'Luisa','apellidos':'Fernández',
        'fecha_nacimiento':date(1995,11,30),'nacionalidad':'Venezolana','estado_civil':'Soltera',
        'telefono':'0416-2233445','email':'luisa@email.com','procedencia':'Valencia',
        'tipo_cliente_profesion':'Médico','categoria':'Estándar','credito_autorizado':False,
        'limite_credito':None,'observaciones':''},
        {'tipo_documento':'P','numero_documento':'33445566','nombres':'John','apellidos':'Smith',
        'fecha_nacimiento':date(1988,7,4),'nacionalidad':'Estadounidense','estado_civil':'Casado',
        'telefono':'0412-9876543','email':'john@email.com','procedencia':'Miami',
        'tipo_cliente_profesion':'Deportista','categoria':'VIP','credito_autorizado':True,
        'limite_credito':Decimal('2000.00'),'observaciones':'Habitación con vista al mar.'},
    ]
    creados = 0
    for d in datos:
        _, created = Huesped.objects.update_or_create(
            tipo_documento=d['tipo_documento'], numero_documento=d['numero_documento'], defaults=d
        )
        if created:
            creados += 1
    print(f"  {creados} nuevos, {len(datos) - creados} ya existían. Total: {len(datos)}")
    print("OK")

def crear_productos():
    print("Creando productos de ejemplo...")
    productos = [
        # Restaurante
        {'nombre': 'Pollo a la Parrilla', 'descripcion': '', 'categoria': 'Comida', 'precio_venta': 12.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'porción', 'maneja_stock': False},
        {'nombre': 'Club Sandwich', 'descripcion': '', 'categoria': 'Comida', 'precio_venta': 8.50, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'unidad', 'maneja_stock': False},
        {'nombre': 'Ensalada César', 'descripcion': '', 'categoria': 'Comida', 'precio_venta': 7.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'unidad', 'maneja_stock': False},
        {'nombre': 'Sopa del Día', 'descripcion': '', 'categoria': 'Comida', 'precio_venta': 5.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'unidad', 'maneja_stock': False},
        # Bebidas
        {'nombre': 'Agua Mineral 500ml', 'descripcion': '', 'categoria': 'Bebida', 'precio_venta': 2.50, 'stock_actual': 50, 'stock_minimo': 10, 'unidad': 'unidad', 'maneja_stock': True},
        {'nombre': 'Refresco Cola Lata', 'descripcion': '', 'categoria': 'Bebida', 'precio_venta': 3.00, 'stock_actual': 30, 'stock_minimo': 5, 'unidad': 'unidad', 'maneja_stock': True},
        {'nombre': 'Cerveza Nacional', 'descripcion': '', 'categoria': 'Bebida', 'precio_venta': 4.50, 'stock_actual': 20, 'stock_minimo': 5, 'unidad': 'unidad', 'maneja_stock': True},
        {'nombre': 'Jugo Natural', 'descripcion': '', 'categoria': 'Bebida', 'precio_venta': 3.50, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'unidad', 'maneja_stock': False},
        # Snacks
        {'nombre': 'Papas Fritas', 'descripcion': '', 'categoria': 'Snack', 'precio_venta': 3.50, 'stock_actual': 15, 'stock_minimo': 5, 'unidad': 'unidad', 'maneja_stock': True},
        {'nombre': 'Chocolate', 'descripcion': '', 'categoria': 'Snack', 'precio_venta': 2.00, 'stock_actual': 25, 'stock_minimo': 5, 'unidad': 'unidad', 'maneja_stock': True},
        {'nombre': 'Maní Salado', 'descripcion': '', 'categoria': 'Snack', 'precio_venta': 1.50, 'stock_actual': 40, 'stock_minimo': 10, 'unidad': 'unidad', 'maneja_stock': True},
        # Lavandería
        {'nombre': 'Lavado de Camisa', 'descripcion': '', 'categoria': 'Lavandería', 'precio_venta': 3.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'servicio', 'maneja_stock': False},
        {'nombre': 'Lavado de Pantalón', 'descripcion': '', 'categoria': 'Lavandería', 'precio_venta': 4.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'servicio', 'maneja_stock': False},
        {'nombre': 'Lavado de Chaqueta', 'descripcion': '', 'categoria': 'Lavandería', 'precio_venta': 6.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'servicio', 'maneja_stock': False},
        {'nombre': 'Planchado', 'descripcion': '', 'categoria': 'Lavandería', 'precio_venta': 2.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'servicio', 'maneja_stock': False},
        {'nombre': 'Lavado de Toalla', 'descripcion': '', 'categoria': 'Lavandería', 'precio_venta': 1.50, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'servicio', 'maneja_stock': False},
        # Llamadas
        {'nombre': 'Llamada Local', 'descripcion': '', 'categoria': 'Llamadas', 'precio_venta': 0.50, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'minuto', 'maneja_stock': False},
        {'nombre': 'Llamada Internacional', 'descripcion': '', 'categoria': 'Llamadas', 'precio_venta': 2.00, 'stock_actual': 0, 'stock_minimo': 0, 'unidad': 'minuto', 'maneja_stock': False},
    ]
    creados = 0
    for p in productos:
        _, created = Producto.objects.get_or_create(nombre=p['nombre'], defaults=p)
        if created:
            creados += 1
    print(f"  {creados} nuevos, {len(productos) - creados} ya existían. Total: {len(productos)}")
    print("OK")

def crear_configuracion():
    print("Creando configuración...")
    pares = [
        ('nombre_hotel','Hotel Salma Suites VIP, C.A.'),
        ('rif','J-40089697-5'),
        ('direccion','Calle N° 5 con Carrera N° 5, Urbanización Delfín Mendoza, Tucupita, Estado Delta Amacuro'),
        ('telefono','+58 287-7210659'),
        ('telefono_2','+58 287-7210707'),
        ('telefono_2','+58 412-8329091'),
        ('email','info@salmasuite.com'),
        ('logo',''),
        ('simbolo_moneda','$'),
        ('posicion_simbolo','antes'),
        ('separador_miles',','),
        ('separador_decimal','.'),
        ('limite_dias_cierre_recepcion','7'),
        ('formato_fecha','DD/MM/AAAA'),
        ('formato_hora','24h'),
    ]
    for c, v in pares:
        Configuracion.objects.update_or_create(clave=c, defaults={'valor': v})
    print("OK")

def crear_colores():
    print("Creando colores...")
    tipos = [
        ('Particular','#9E9E9E'),('Militar','#4CAF50'),('Político','#2196F3'),
        ('Artista','#FF9800'),('Empresario','#607D8B'),('Deportista','#E91E63'),
        ('Diplomático','#3F51B5'),('Médico','#00BCD4'),('Religioso','#FFEB3B'),
        ('Turista','#FF5722'),('Ejecutivo de Ventas','#795548'),('Comerciante','#8BC34A'),
    ]
    creados = 0
    for t, c in tipos:
        _, created = ColoresTipoCliente.objects.update_or_create(tipo_cliente_profesion=t, defaults={'color': c})
        if created:
            creados += 1
    print(f"  {creados} nuevos, {len(tipos) - creados} ya existían. Total: {len(tipos)}")

    estados = [
        ('Limpia','#4CAF50'),('Ocupada','#F44336'),('Sucia','#FFEB3B'),
        ('Mantenimiento','#9E9E9E'),('Obra','#212121'),
    ]
    creados_estados = 0
    for e, c in estados:
        _, created = ColoresEstadoHabitacion.objects.update_or_create(estado=e, defaults={'color': c})
        if created:
            creados_estados += 1
    print(f"  {creados_estados} nuevos, {len(estados) - creados_estados} ya existían. Total: {len(estados)}")
    print("OK")

def main():
    print("========================================")
    print("   SEED DE DATOS - Salma Suite VIP PMS  ")
    print("========================================")
    print()
    crear_usuarios()
    print()
    crear_habitaciones()
    print()
    crear_huespedes()
    print()
    crear_productos()
    print()
    crear_configuracion()
    print()
    crear_colores()
    print()
    print("========================================")
    print("   COMPLETADO - Ahora puedes iniciar    ")
    print("   el sistema con: npm run dev          ")
    print("========================================")

if __name__ == '__main__':
    main()