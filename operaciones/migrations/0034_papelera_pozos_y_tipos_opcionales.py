"""
Papelera de pozos (eliminar solo oculta) y tipos correctos en los módulos opcionales:
- hora_inicio / hora_fin de las muestras pasan de texto 'HH:MM' a TimeField. Primero se
  permiten nulos, se limpian los textos vacíos o inválidos y luego se cambia el tipo.
- costo del evento no programado pasa de FloatField a DecimalField (dinero sin redondeos).
"""

from datetime import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

MODELOS_CON_HORA = ('AnalisisSolidosEquipo', 'RetencionRecortes')
CAMPOS_HORA = ('hora_inicio', 'hora_fin')


def _hora_valida(texto):
    try:
        datetime.strptime(texto, '%H:%M')
        return True
    except (TypeError, ValueError):
        return False


def limpiar_horas_invalidas(apps, schema_editor):
    for nombre_modelo in MODELOS_CON_HORA:
        modelo = apps.get_model('operaciones', nombre_modelo)
        for campo in CAMPOS_HORA:
            invalidas = [pk for pk, valor in modelo.objects.values_list('pk', campo)
                         if valor is not None and not _hora_valida(valor)]
            modelo.objects.filter(pk__in=invalidas).update(**{campo: None})


def _campo_hora_texto(etiqueta):
    return models.CharField(max_length=5, null=True, blank=True, verbose_name=etiqueta)


def _campo_hora(etiqueta):
    return models.TimeField(null=True, blank=True, verbose_name=etiqueta)


ETIQUETAS = {'hora_inicio': 'Hora de inicio', 'hora_fin': 'Hora de fin'}


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0033_inventario_inicial_manual'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pozo',
            name='eliminado_en',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Eliminado el'),
        ),
        migrations.AddField(
            model_name='pozo',
            name='eliminado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pozos_eliminados', to=settings.AUTH_USER_MODEL, verbose_name='Eliminado por'),
        ),
        migrations.AlterField(
            model_name='eventonoprogramado',
            name='costo',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True, verbose_name='Costo estimado'),
        ),
        *[migrations.AlterField(model_name=m.lower(), name=c, field=_campo_hora_texto(ETIQUETAS[c]))
          for m in MODELOS_CON_HORA for c in CAMPOS_HORA],
        migrations.RunPython(limpiar_horas_invalidas, migrations.RunPython.noop),
        *[migrations.AlterField(model_name=m.lower(), name=c, field=_campo_hora(ETIQUETAS[c]))
          for m in MODELOS_CON_HORA for c in CAMPOS_HORA],
    ]
