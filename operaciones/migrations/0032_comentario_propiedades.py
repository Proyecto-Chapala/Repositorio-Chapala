"""
Comentario del reporte de propiedades (reportito), punto 16 de la revisión de octubre 2026.
Antes se escribía en la página pero no se guardaba.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0031_tarifas_dos_monedas'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportediariocomentarios',
            name='comentario_propiedades',
            field=models.TextField(
                blank=True, verbose_name='Comentario del Reporte de Propiedades',
                help_text='Lo que el ingeniero le escribe al Company Man en el reporte de propiedades (reportito).'),
        ),
    ]
