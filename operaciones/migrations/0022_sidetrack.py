from django.db import migrations, models


class Migration(migrations.Migration):
    """Casos especiales del manual: side track (kick-off del día y tipo de intervalo)."""

    dependencies = [
        ('operaciones', '0021_modulos_opcionales'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportediario',
            name='kickoff_sidetrack_ft',
            field=models.FloatField(
                default=0.0, verbose_name='Profundidad de Kick-off del Side Track (ft)',
                help_text='Solo el día en que arranca el side track. El hoyo perforado de ese día se '
                          'cuenta desde aquí y no desde la profundidad del día anterior.'),
        ),
        migrations.AlterField(
            model_name='intervalorevestimiento',
            name='tipo',
            field=models.CharField(
                blank=True, max_length=15, verbose_name='Tipo',
                choices=[('CONDUCTOR', 'Conductor'), ('SUPERFICIE', 'Superficie'),
                         ('INTERMEDIO', 'Intermedio'), ('PRODUCCION', 'Producción'),
                         ('LINER', 'Liner'), ('CASING', 'Revestimiento'),
                         ('HOYO_ABIERTO', 'Hoyo Abierto'), ('SIDETRACK', 'Side Track (desvío)')]),
        ),
    ]
