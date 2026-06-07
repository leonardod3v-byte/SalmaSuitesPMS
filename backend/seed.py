import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.habitaciones.models import TipoHabitacion, Habitacion
from apps.guests.models import Huesped
from apps.reservaciones.models import Reserva, Actividad
from apps.pagos.models import Pago

# ── Limpiar datos existentes (excepto el admin) ─────────────────────────────
print("🧹 Limpiando datos existentes...")
# Conservar el usuario admin (por nombre de usuario)
admin_username = 'basquiatdev'
admin = User.objects.filter(username=admin_username).first()

# Eliminar datos en orden para evitar violaciones de FK
Actividad.objects.all().delete()
Pago.objects.all().delete()
Reserva.objects.all().delete()
Huesped.objects.all().delete()
Habitacion.objects.all().delete()
TipoHabitacion.objects.all().delete()

# Si no existe admin, crearlo
if not admin:
    admin = User.objects.create_superuser(
        username=admin_username,
        email='admin@salmasuites.com',
        password='admin123'  # CAMBIAR EN PRODUCCIÓN
    )
    admin.role = 'admin'
    admin.save()
    print(f"✓ Admin {admin_username} creado.")
else:
    # Asegurar que tiene rol admin
    admin.role = 'admin'
    admin.save()
    print(f"✓ Admin {admin_username} conservado.")

# ── Tipos de habitación (actualizados) ──────────────────────────────────────
tipos_data = [
    {'codigo': 'uni_familiar',      'nombre': 'Uni-Familiar',                     'capacidad_maxima': 2, 'precio_base_noche': 70.00},
    {'codigo': 'doble_individual',  'nombre': 'Doble Individual (2 camas)',       'capacidad_maxima': 2, 'precio_base_noche': 75.00},
    {'codigo': 'matrimonial',       'nombre': 'Matrimonial',                      'capacidad_maxima': 2, 'precio_base_noche': 80.00},
    {'codigo': 'doble_matrimonial', 'nombre': 'Doble Matrimonial (2 camas mat.)', 'capacidad_maxima': 4, 'precio_base_noche': 120.00},
    {'codigo': 'triple_individual', 'nombre': 'Triple Individual',                'capacidad_maxima': 3, 'precio_base_noche': 100.00},
    {'codigo': 'suite',             'nombre': 'Suite',                            'capacidad_maxima': 2, 'precio_base_noche': 200.00},
    {'codigo': 'queen',             'nombre': 'Queen',                            'capacidad_maxima': 2, 'precio_base_noche': 90.00},
]
tipos_creados = []
for t in tipos_data:
    tipo, _ = TipoHabitacion.objects.get_or_create(codigo=t['codigo'], defaults=t)
    tipos_creados.append(tipo)
print(f"✓ Tipos de habitación: {len(tipos_creados)}")

# ── Habitaciones de ejemplo ─────────────────────────────────────────────────
# Mapeo de códigos a objetos tipo
tipo_map = {t.codigo: t for t in tipos_creados}

habs_data = [
    # Piso 1
    {'numero': '101', 'piso': 1, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '102', 'piso': 1, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '103', 'piso': 1, 'tipo': tipo_map['doble_individual'],  'estado': 'libre'},
    {'numero': '104', 'piso': 1, 'tipo': tipo_map['doble_individual'],  'estado': 'libre'},
    {'numero': '105', 'piso': 1, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '106', 'piso': 1, 'tipo': tipo_map['matrimonial'],       'estado': 'sucia'},
    {'numero': '107', 'piso': 1, 'tipo': tipo_map['doble_matrimonial'], 'estado': 'ocupada'},
    {'numero': '108', 'piso': 1, 'tipo': tipo_map['doble_matrimonial'], 'estado': 'mantenimiento'},
    # Piso 2
    {'numero': '201', 'piso': 2, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '202', 'piso': 2, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '203', 'piso': 2, 'tipo': tipo_map['doble_individual'],  'estado': 'libre'},
    {'numero': '204', 'piso': 2, 'tipo': tipo_map['doble_individual'],  'estado': 'ocupada'},
    {'numero': '205', 'piso': 2, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '206', 'piso': 2, 'tipo': tipo_map['doble_matrimonial'], 'estado': 'libre'},
    {'numero': '207', 'piso': 2, 'tipo': tipo_map['suite'],             'estado': 'ocupada'},
    {'numero': '208', 'piso': 2, 'tipo': tipo_map['suite'],             'estado': 'ocupada'},
    # Piso 3
    {'numero': '301', 'piso': 3, 'tipo': tipo_map['suite'],             'estado': 'ocupada'},
    {'numero': '302', 'piso': 3, 'tipo': tipo_map['queen'],             'estado': 'libre'},
    {'numero': '303', 'piso': 3, 'tipo': tipo_map['matrimonial'],       'estado': 'ocupada'},
    {'numero': '304', 'piso': 3, 'tipo': tipo_map['uni_familiar'],      'estado': 'ocupada'},
]
for h in habs_data:
    Habitacion.objects.get_or_create(numero=h['numero'], defaults=h)
print(f"✓ Habitaciones: {Habitacion.objects.count()}")

# ── Huéspedes con nuevos campos ────────────────────────────────────────────
huespedes_data = [
    {
        'tipo_documento': 'V', 'numero_documento': '12345678',
        'nombre': 'Carlos', 'apellido': 'Rodríguez',
        'telefono': '+584141234567', 'email': 'carlos@email.com',
        'es_vip': True, 'procedencia': 'Caracas, Venezuela',
        'profesion': 'Ingeniero', 'edad': 35, 'nacionalidad': 'Venezolana',
        'estado_civil': 'casado', 'fecha_nacimiento': '1989-05-15',
        'telefono_contacto': '+584142223344'
    },
    {
        'tipo_documento': 'V', 'numero_documento': '87654321',
        'nombre': 'María', 'apellido': 'González',
        'telefono': '+584161234567', 'email': 'maria@email.com',
        'es_vip': False, 'procedencia': 'Valencia, Venezuela',
        'profesion': 'Médico', 'edad': 42, 'nacionalidad': 'Venezolana',
        'estado_civil': 'divorciado', 'fecha_nacimiento': '1982-11-23',
        'telefono_contacto': ''
    },
    {
        'tipo_documento': 'E', 'numero_documento': '11223344',
        'nombre': 'John', 'apellido': 'Smith',
        'telefono': '+584121234567', 'email': 'john@email.com',
        'es_vip': True, 'procedencia': 'Miami, USA',
        'profesion': 'Ejecutivo de Ventas', 'edad': 48, 'nacionalidad': 'Americana',
        'estado_civil': 'casado', 'fecha_nacimiento': '1976-03-10',
        'telefono_contacto': '+584126665544'
    },
    {
        'tipo_documento': 'V', 'numero_documento': '55667788',
        'nombre': 'Ana', 'apellido': 'Martínez',
        'telefono': '+584151234567', 'email': 'ana@email.com',
        'es_vip': False, 'procedencia': 'Barquisimeto, Venezuela',
        'profesion': 'Comerciante', 'edad': 29, 'nacionalidad': 'Venezolana',
        'estado_civil': 'soltero', 'fecha_nacimiento': '1995-07-19',
        'telefono_contacto': '+584159998877'
    },
]
for h in huespedes_data:
    Huesped.objects.get_or_create(numero_documento=h['numero_documento'], defaults=h)
print(f"✓ Huéspedes: {Huesped.objects.count()}")

# ── Reservas con nuevos campos ──────────────────────────────────────────────
hoy    = date.today()
ayer   = hoy - timedelta(days=1)
manana = hoy + timedelta(days=1)

h101 = Habitacion.objects.get(numero='101')
h102 = Habitacion.objects.get(numero='102')
h201 = Habitacion.objects.get(numero='201')
h301 = Habitacion.objects.get(numero='301')
h207 = Habitacion.objects.get(numero='207')
h302 = Habitacion.objects.get(numero='302')

c1 = Huesped.objects.get(numero_documento='12345678')
c2 = Huesped.objects.get(numero_documento='87654321')
c3 = Huesped.objects.get(numero_documento='11223344')
c4 = Huesped.objects.get(numero_documento='55667788')

reservas_data = [
    {
        'habitacion': h101, 'huesped': c1,
        'fecha_entrada': ayer, 'fecha_salida': manana,
        'estado': 'pagada', 'metodo_pago': 'zelle',
        'monto_total': 160.00, 'monto_pagado': 160.00,
        'referencia_pago': 'ZLL-001', 'creada_por': admin,
        'modalidad_pago': 'contado', 'requiere_factura': True,
        'datos_fiscales': {'rif': 'J-12345678-0', 'razon_social': 'Rodríguez Asoc.', 'direccion': 'Calle 1, Caracas'}
    },
    {
        'habitacion': h102, 'huesped': c2,
        'fecha_entrada': hoy, 'fecha_salida': manana,
        'estado': 'confirmada', 'metodo_pago': 'efectivo_usd',
        'monto_total': 80.00, 'monto_pagado': 40.00,
        'referencia_pago': '', 'creada_por': admin,
        'modalidad_pago': 'abono', 'requiere_factura': False,
        'datos_fiscales': {}
    },
    {
        'habitacion': h201, 'huesped': c3,
        'fecha_entrada': hoy, 'fecha_salida': hoy + timedelta(days=3),
        'estado': 'pagada', 'metodo_pago': 'transferencia',
        'monto_total': 600.00, 'monto_pagado': 600.00,
        'referencia_pago': 'TRF-002', 'creada_por': admin,
        'modalidad_pago': 'contado', 'requiere_factura': True,
        'datos_fiscales': {'rif': 'J-98765432-1', 'razon_social': 'Smith Enterprises', 'direccion': 'Miami, FL'}
    },
    {
        'habitacion': h301, 'huesped': c4,
        'fecha_entrada': manana, 'fecha_salida': hoy + timedelta(days=4),
        'estado': 'pendiente', 'metodo_pago': '',
        'monto_total': 800.00, 'monto_pagado': 0.00,
        'referencia_pago': '', 'creada_por': admin,
        'modalidad_pago': 'credito', 'requiere_factura': False,
        'datos_fiscales': {}
    },
    {
        'habitacion': h207, 'huesped': c1,  # mismo huésped en otra reserva
        'fecha_entrada': hoy + timedelta(days=5), 'fecha_salida': hoy + timedelta(days=7),
        'estado': 'confirmada', 'metodo_pago': 'zelle',
        'monto_total': 400.00, 'monto_pagado': 200.00,
        'referencia_pago': 'ZLL-003', 'creada_por': admin,
        'modalidad_pago': 'abono', 'requiere_factura': True,
        'datos_fiscales': {'rif': 'J-12345678-0', 'razon_social': 'Rodríguez Asoc.', 'direccion': 'Calle 1, Caracas'}
    },
]

reservas_creadas = []
for r in reservas_data:
    obj, created = Reserva.objects.get_or_create(
        habitacion=r['habitacion'],
        huesped=r['huesped'],
        fecha_entrada=r['fecha_entrada'],
        defaults=r
    )
    reservas_creadas.append(obj)
print(f"✓ Reservas: {Reserva.objects.count()}")

# Reserva en check_in
Reserva.objects.create(
    habitacion=Habitacion.objects.get(numero='101'),
    huesped=Huesped.objects.first(),
    fecha_entrada=hoy - timedelta(days=2),
    fecha_salida=hoy + timedelta(days=2),
    estado='check_in',
    monto_total=200.00,
    creada_por=admin
)

# ── Actividades ────────────────────────────────────────────────────────────
# Limpiar actividades anteriores (ya se borraron al inicio, pero por si acaso)
Actividad.objects.all().delete()

actividades_data = [
    {'tipo': 'check_in',       'descripcion': 'Check-in completado',     'detalle': 'H-101 - Carlos Rodríguez'},
    {'tipo': 'consumo',        'descripcion': 'Consumo registrado',       'detalle': 'Minibar H-201 - $45'},
    {'tipo': 'cambio_estado',  'descripcion': 'Limpieza finalizada',      'detalle': 'Habitación 103 lista'},
    {'tipo': 'reserva_creada', 'descripcion': 'Nueva reserva registrada', 'detalle': 'H-301 - Ana Martínez'},
]
for a in actividades_data:
    Actividad.objects.create(**a, usuario=admin)
print(f"✓ Actividades: {Actividad.objects.count()}")

# ── Pagos ──────────────────────────────────────────────────────────────────
r1 = reservas_creadas[0]  # H-101
r3 = reservas_creadas[2]  # H-201
r5 = reservas_creadas[4]  # H-207

pagos_data = [
    {'reserva': r1, 'monto': 160.00, 'metodo': 'zelle',         'concepto': 'estadia', 'referencia': 'ZLL-001'},
    {'reserva': r3, 'monto': 600.00, 'metodo': 'transferencia', 'concepto': 'estadia', 'referencia': 'TRF-002'},
    {'reserva': r3, 'monto': 45.00,  'metodo': 'efectivo_usd',  'concepto': 'consumo', 'referencia': ''},
    {'reserva': r5, 'monto': 200.00, 'metodo': 'zelle',         'concepto': 'abono',   'referencia': 'ZLL-003'},
]
for p in pagos_data:
    Pago.objects.create(**p, registrado_por=admin)
print(f"✓ Pagos: {Pago.objects.count()}")

print("\n✅ Seed completado correctamente.")