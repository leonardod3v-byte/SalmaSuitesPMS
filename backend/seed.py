import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.habitaciones.models import TipoHabitacion, Habitacion
from apps.guests.models import Huesped
from apps.reservaciones.models import Reserva, Actividad
from apps.pagos.models import Pago
from datetime import date, timedelta

# ── Usuario admin ──────────────────────────────────────────────────────────
admin = User.objects.get(username='basquiatdev')
admin.role = 'admin'
admin.save()
print(f'✓ Admin: {admin.username} → {admin.role}')

# ── Tipos de habitación ────────────────────────────────────────────────────
tipos_data = [
    {'codigo': 'matrimonial',       'nombre': 'Habitación Matrimonial',               'capacidad_maxima': 2, 'precio_base_noche': 80.00},
    {'codigo': 'doble_individual',  'nombre': 'Doble Individual (2 camas)',            'capacidad_maxima': 2, 'precio_base_noche': 75.00},
    {'codigo': 'doble_matrimonial', 'nombre': 'Doble Matrimonial (2 camas matrimon.)', 'capacidad_maxima': 4, 'precio_base_noche': 120.00},
    {'codigo': 'triple_individual', 'nombre': 'Triple Individual',                     'capacidad_maxima': 3, 'precio_base_noche': 100.00},
    {'codigo': 'suite',             'nombre': 'Suite',                                'capacidad_maxima': 2, 'precio_base_noche': 200.00},
]
for t in tipos_data:
    TipoHabitacion.objects.get_or_create(codigo=t['codigo'], defaults=t)
print(f'✓ Tipos: {TipoHabitacion.objects.count()}')

# ── Habitaciones ───────────────────────────────────────────────────────────
mat  = TipoHabitacion.objects.get(codigo='matrimonial')
dind = TipoHabitacion.objects.get(codigo='doble_individual')
dmat = TipoHabitacion.objects.get(codigo='doble_matrimonial')
suit = TipoHabitacion.objects.get(codigo='suite')

habs_data = [
    {'numero': '101', 'piso': 1, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '102', 'piso': 1, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '103', 'piso': 1, 'tipo': dind, 'estado': 'libre'},
    {'numero': '104', 'piso': 1, 'tipo': dind, 'estado': 'libre'},
    {'numero': '105', 'piso': 1, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '106', 'piso': 1, 'tipo': mat,  'estado': 'sucia'},
    {'numero': '107', 'piso': 1, 'tipo': dmat, 'estado': 'ocupada'},
    {'numero': '108', 'piso': 1, 'tipo': dmat, 'estado': 'mantenimiento'},
    {'numero': '201', 'piso': 2, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '202', 'piso': 2, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '203', 'piso': 2, 'tipo': dind, 'estado': 'libre'},
    {'numero': '204', 'piso': 2, 'tipo': dind, 'estado': 'ocupada'},
    {'numero': '205', 'piso': 2, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '206', 'piso': 2, 'tipo': dmat, 'estado': 'libre'},
    {'numero': '207', 'piso': 2, 'tipo': suit, 'estado': 'ocupada'},
    {'numero': '208', 'piso': 2, 'tipo': suit, 'estado': 'ocupada'},
    {'numero': '301', 'piso': 3, 'tipo': suit, 'estado': 'ocupada'},
    {'numero': '302', 'piso': 3, 'tipo': suit, 'estado': 'libre'},
    {'numero': '303', 'piso': 3, 'tipo': mat,  'estado': 'ocupada'},
    {'numero': '304', 'piso': 3, 'tipo': mat,  'estado': 'ocupada'},
]
for h in habs_data:
    Habitacion.objects.get_or_create(numero=h['numero'], defaults=h)
print(f'✓ Habitaciones: {Habitacion.objects.count()}')

# ── Huéspedes ──────────────────────────────────────────────────────────────
huespedes_data = [
    {'tipo_documento': 'V', 'numero_documento': '12345678', 'nombre': 'Carlos', 'apellido': 'Rodríguez', 'telefono': '+584141234567', 'email': 'carlos@email.com', 'es_vip': True},
    {'tipo_documento': 'V', 'numero_documento': '87654321', 'nombre': 'María',  'apellido': 'González',  'telefono': '+584161234567', 'email': 'maria@email.com',  'es_vip': False},
    {'tipo_documento': 'E', 'numero_documento': '11223344', 'nombre': 'John',   'apellido': 'Smith',     'telefono': '+584121234567', 'email': 'john@email.com',   'es_vip': True},
    {'tipo_documento': 'V', 'numero_documento': '55667788', 'nombre': 'Ana',    'apellido': 'Martínez',  'telefono': '+584151234567', 'email': 'ana@email.com',    'es_vip': False},
]
for h in huespedes_data:
    Huesped.objects.get_or_create(numero_documento=h['numero_documento'], defaults=h)
print(f'✓ Huéspedes: {Huesped.objects.count()}')

# ── Reservas ───────────────────────────────────────────────────────────────
hoy    = date.today()
ayer   = hoy - timedelta(days=1)
manana = hoy + timedelta(days=1)

h101 = Habitacion.objects.get(numero='101')
h102 = Habitacion.objects.get(numero='102')
h201 = Habitacion.objects.get(numero='201')
h301 = Habitacion.objects.get(numero='301')

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
        'referencia_pago': 'ZLL-001', 'creada_por': admin
    },
    {
        'habitacion': h102, 'huesped': c2,
        'fecha_entrada': hoy, 'fecha_salida': manana,
        'estado': 'confirmada', 'metodo_pago': 'efectivo_usd',
        'monto_total': 80.00, 'monto_pagado': 0.00,
        'referencia_pago': '', 'creada_por': admin
    },
    {
        'habitacion': h201, 'huesped': c3,
        'fecha_entrada': hoy, 'fecha_salida': hoy + timedelta(days=3),
        'estado': 'pagada', 'metodo_pago': 'transferencia',
        'monto_total': 600.00, 'monto_pagado': 600.00,
        'referencia_pago': 'TRF-002', 'creada_por': admin
    },
    {
        'habitacion': h301, 'huesped': c4,
        'fecha_entrada': manana, 'fecha_salida': hoy + timedelta(days=4),
        'estado': 'pendiente', 'metodo_pago': '',
        'monto_total': 800.00, 'monto_pagado': 0.00,
        'referencia_pago': '', 'creada_por': admin
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
print(f'✓ Reservas: {Reserva.objects.count()}')

# ── Actividades ────────────────────────────────────────────────────────────
# Limpiar actividades anteriores para evitar duplicados
Actividad.objects.all().delete()

actividades_data = [
    {'tipo': 'check_in',       'descripcion': 'Check-in completado',     'detalle': 'H-101 - Carlos Rodríguez'},
    {'tipo': 'consumo',        'descripcion': 'Consumo registrado',       'detalle': 'Minibar H-201 - $45'},
    {'tipo': 'cambio_estado',  'descripcion': 'Limpieza finalizada',      'detalle': 'Habitación 103 lista'},
    {'tipo': 'reserva_creada', 'descripcion': 'Nueva reserva registrada', 'detalle': 'H-301 - Ana Martínez'},
]
for a in actividades_data:
    Actividad.objects.create(**a, usuario=admin)
print(f'✓ Actividades: {Actividad.objects.count()}')

# ── Pagos ──────────────────────────────────────────────────────────────────
r1 = reservas_creadas[0]
r3 = reservas_creadas[2]

pagos_data = [
    {'reserva': r1, 'monto': 160.00, 'metodo': 'zelle',         'concepto': 'estadia', 'referencia': 'ZLL-001'},
    {'reserva': r3, 'monto': 600.00, 'metodo': 'transferencia', 'concepto': 'estadia', 'referencia': 'TRF-002'},
    {'reserva': r3, 'monto': 45.00,  'metodo': 'efectivo_usd',  'concepto': 'consumo', 'referencia': ''},
]
for p in pagos_data:
    Pago.objects.create(**p, registrado_por=admin)
print(f'✓ Pagos: {Pago.objects.count()}')

print('\n Seed completado correctamente')