from django.db import migrations, models
import django.db.models.deletion

def limpiar_ocupacion(apps, schema_editor):
    Huesped = apps.get_model('huespedes', 'Huesped')
    Huesped.objects.filter(ocupacion='').update(ocupacion=None)

class Migration(migrations.Migration):

    dependencies = [
        ('huespedes', '0003_remove_huesped_procedencia_and_more'),
        ('configuracion', '0002_ocupacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='huesped',
            name='ocupacion',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.RunPython(limpiar_ocupacion, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='huesped',
            name='ocupacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='huespedes', to='configuracion.ocupacion'),
        ),
    ]
