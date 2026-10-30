from django.db import migrations

def renombrar_estados(apps, schema_editor):
    Habitacion = apps.get_model('habitaciones', 'Habitacion')

    Habitacion.objects.filter(estado='Limpia').update(estado='Disponible')
    Habitacion.objects.filter(estado='Sucia').update(estado='Limpieza')

def revertir_estados(apps, schema_editor):
    Habitacion = apps.get_model('habitaciones', 'Habitacion')

    Habitacion.objects.filter(estado='Disponible').update(estado='Limpia')
    Habitacion.objects.filter(estado='Limpieza').update(estado='Sucia')

class Migration(migrations.Migration):

    dependencies = [
        ('habitaciones', '0003_alter_habitacion_estado'),
    ]

    operations = [
        migrations.RunPython(renombrar_estados, revertir_estados),
    ]
