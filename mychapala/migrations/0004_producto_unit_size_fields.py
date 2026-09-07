"""
Agrega los campos estructurados de "Unit Size" a Producto (cantidad_unitaria,
unidad_medida, tipo_empaque) y migra los 53 productos ya cargados (38 químicos +
2 líquidos + 13 wellsite) a partir de los valores conocidos de seed_data.py.

No se toca ni se borra ningún campo existente (unidad, libraje, gravedad_especifica
se conservan tal cual, en texto libre, para no romper la búsqueda ni la API actual).
"""

from decimal import Decimal

from django.db import migrations, models


# codigo -> (cantidad_unitaria, unidad_medida, tipo_empaque)
# Derivado a mano de seed_data.py (PRODUCTOS_AOS, PRODUCTOS_LIQUIDOS, PRODUCTOS_WELLSITE).
# Reglas aplicadas:
#   - "SACOS ... LBS" con libraje explícito (ej. "55 LBS")  -> LB / BG
#   - "TAMBOR 55 GLS" con libraje "N/A"                      -> GA / DM
#   - "TOTEMS" con libraje "N/A" (tamaño real en descripcion: "TOTE 1000 LT") -> LT / TOTE
#   - Líquidos en "BLS" (barriles)                           -> 1 BBL / BLS
#   - Wellsite: unidad ya viene como "{n}. {LB|KG|GA} {BG|CN}" o "1. EA" -> se parsea directo
UNIT_SIZE_POR_CODIGO = {
    # --- PRODUCTOS_AOS (categoria=quimico) ---
    "AOS-1001": ("55", "GA", "DM"),
    "AOS-1002": ("55", "LB", "BG"),
    "AOS-1003": ("55", "GA", "DM"),
    "AOS-1004": ("55", "LB", "BG"),
    "AOS-1005": ("55", "GA", "DM"),
    "AOS-1006": ("55", "LB", "BG"),
    "AOS-1007": ("100", "LB", "BG"),
    "AOS-1008": ("55", "LB", "BG"),
    "AOS-1009": ("113", "LB", "BG"),
    "AOS-1010": ("44", "LB", "BG"),
    "AOS-1011": ("66", "LB", "BG"),
    "AOS-1012": ("1000", "LT", "TOTE"),
    "AOS-1013": ("55", "LB", "BG"),
    "AOS-1014": ("55", "LB", "BG"),
    "AOS-1015": ("55", "GA", "DM"),
    "AOS-1016": ("25", "LB", "BG"),
    "AOS-1017": ("1000", "LT", "TOTE"),
    "AOS-1018": ("55", "LB", "BG"),
    "AOS-1019": ("55", "GA", "DM"),
    "AOS-1020": ("55", "GA", "DM"),
    "AOS-1021": ("55", "GA", "DM"),
    "AOS-1022": ("55", "GA", "DM"),
    "AOS-1023": ("88", "LB", "BG"),
    "AOS-1024": ("55", "GA", "DM"),
    "AOS-1025": ("55", "LB", "BG"),
    "AOS-1026": ("55", "LB", "BG"),
    "AOS-1027": ("55", "LB", "BG"),
    "AOS-1028": ("25", "LB", "BG"),
    "AOS-1029": ("55", "LB", "BG"),
    "AOS-1030": ("55", "LB", "BG"),
    "AOS-1031": ("55", "LB", "BG"),
    "AOS-1032": ("55", "LB", "BG"),
    "AOS-1033": ("88", "LB", "BG"),
    "AOS-1034": ("1000", "LT", "TOTE"),
    "AOS-1035": ("55", "LB", "BG"),
    "AOS-1036": ("55", "GA", "DM"),
    "AOS-1037": ("25", "LB", "BG"),
    "AOS-1038": ("55", "GA", "DM"),
    # --- PRODUCTOS_LIQUIDOS (categoria=liquido) ---
    "AOS-LIQ-01": ("1", "BBL", "BLS"),
    "AOS-LIQ-02": ("1", "BBL", "BLS"),
    # --- PRODUCTOS_WELLSITE (categoria=wellsite) ---
    "WELL-001": ("100", "LB", "BG"),
    "WELL-002": ("50", "LB", "BG"),
    "WELL-003": ("25", "KG", "BG"),
    "WELL-004": ("25", "KG", "BG"),
    "WELL-005": ("30", "LB", "BG"),
    "WELL-006": ("5", "GA", "CN"),
    "WELL-007": ("5", "GA", "CN"),
    "WELL-008": ("25", "KG", "BG"),
    "WELL-009": ("1", "EA", "EA"),
    "WELL-010": ("25", "KG", "BG"),
    "WELL-011": ("20", "KG", "BG"),
    "WELL-012": ("50", "LB", "BG"),
    "WELL-013": ("100", "LB", "BG"),
}


def poblar_unit_size(apps, schema_editor):
    Producto = apps.get_model("mychapala", "Producto")
    for codigo, (cantidad, unidad_medida, tipo_empaque) in UNIT_SIZE_POR_CODIGO.items():
        Producto.objects.filter(codigo=codigo).update(
            cantidad_unitaria=Decimal(cantidad),
            unidad_medida=unidad_medida,
            tipo_empaque=tipo_empaque,
        )


def revertir_unit_size(apps, schema_editor):
    Producto = apps.get_model("mychapala", "Producto")
    Producto.objects.filter(codigo__in=list(UNIT_SIZE_POR_CODIGO.keys())).update(
        cantidad_unitaria=None,
        unidad_medida="",
        tipo_empaque="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("mychapala", "0003_producto_categoria_producto_cum_received_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="cantidad_unitaria",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True,
                help_text="Cantidad por unidad de empaque (ej. 100, 50, 25, 5, 1000). "
                           "Dato estructurado equivalente al primer número del antiguo 'Unit Size'.",
                verbose_name="Cantidad unitaria",
            ),
        ),
        migrations.AddField(
            model_name="producto",
            name="unidad_medida",
            field=models.CharField(
                blank=True, max_length=3,
                choices=[
                    ("LB", "Libras (LB)"), ("KG", "Kilogramos (KG)"), ("GA", "Galones (GA)"),
                    ("LT", "Litros (LT)"), ("BBL", "Barriles (BBL)"),
                    ("EA", "Unidad (EA) — sin conversión de peso"),
                ],
                help_text="Unidad de esa cantidad (LB, KG, GA, LT, BBL, EA).",
                verbose_name="Unidad de medida",
            ),
        ),
        migrations.AddField(
            model_name="producto",
            name="tipo_empaque",
            field=models.CharField(
                blank=True, max_length=4,
                choices=[
                    ("BG", "Saco / Bolsa (BG)"), ("CN", "Lata / Cuñete (CN)"), ("DM", "Tambor (DM)"),
                    ("TOTE", "Tote"), ("BLS", "Barril (BLS)"),
                    ("EA", "Unidad (EA) — sin empaque físico, ej. servicios"),
                ],
                help_text="Empaque en que viene esa cantidad (BG, CN, DM, TOTE, BLS, EA).",
                verbose_name="Tipo de empaque",
            ),
        ),
        migrations.RunPython(poblar_unit_size, revertir_unit_size),
    ]
