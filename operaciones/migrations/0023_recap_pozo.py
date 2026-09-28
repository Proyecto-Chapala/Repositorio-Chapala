import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Reporte final del pozo: textos de conclusiones y recomendaciones."""

    dependencies = [
        ('operaciones', '0022_sidetrack'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecapPozo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resumen', models.TextField(blank=True, verbose_name='Resumen del pozo')),
                ('conclusiones', models.TextField(blank=True, verbose_name='Conclusiones')),
                ('recomendaciones', models.TextField(blank=True, verbose_name='Recomendaciones')),
                ('lecciones', models.TextField(blank=True, verbose_name='Lecciones aprendidas / buenas prácticas')),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('pozo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recap', to='operaciones.pozo')),
            ],
            options={
                'verbose_name': 'Reporte Final del Pozo',
                'verbose_name_plural': 'Reportes Finales de Pozo',
            },
        ),
    ]
