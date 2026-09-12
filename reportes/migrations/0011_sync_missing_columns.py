# Generated to synchronize missing columns in reportes_tuberiainstalada and reportes_cierrevolumetrico
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0010_remove_pit_unica_descripcion_fosa_por_pozo_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE reportes_tuberiainstalada 
                ADD COLUMN IF NOT EXISTS profundidad_tvd numeric(10, 2) NULL;
            
            ALTER TABLE reportes_cierrevolumetrico 
                ADD COLUMN IF NOT EXISTS fosa_origen_id uuid NULL 
                REFERENCES reportes_fosa(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE reportes_cierrevolumetrico 
                ADD COLUMN IF NOT EXISTS categoria_perdida_id uuid NULL 
                REFERENCES reportes_categoriaperdida(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE reportes_cierrevolumetrico 
                ADD COLUMN IF NOT EXISTS transaccion_left_in_hole_id uuid NULL 
                REFERENCES reportes_transaccionfosa(id) DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            ALTER TABLE reportes_tuberiainstalada DROP COLUMN IF EXISTS profundidad_tvd;
            ALTER TABLE reportes_cierrevolumetrico DROP COLUMN IF EXISTS fosa_origen_id;
            ALTER TABLE reportes_cierrevolumetrico DROP COLUMN IF EXISTS categoria_perdida_id;
            ALTER TABLE reportes_cierrevolumetrico DROP COLUMN IF EXISTS transaccion_left_in_hole_id;
            """
        ),
    ]

