"""
Carga el catálogo de productos químicos de AOS en la matriz (operaciones.Producto).

Solo CREA los productos que no existen (por código); los que ya existen no se tocan.
El precio y la existencia arrancan en 0: con el inventario por pozo, la existencia sale
de los tickets del pozo y el precio lo pone el usuario (ver docs/23_CORRECCIONES_REVISION_OCT.md).

SmartMud.exe lo ejecuta la primera vez que crea la base. A mano:
    python manage.py cargar_catalogo_productos
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from operaciones.models import Producto

# (código, descripción, unidad, libraje, gravedad específica, categoría)
CATALOGO_AOS = [
    ('AOS-1001', 'ACETROL - ACETATO (TAMBOR 55 GLS)', 'TAMBOR 55 GLS', '0', '0.89', 'LIQUIDO'),
    ('AOS-1002', 'ACETATO DE POTASIO (SACOS DE 25 KG)', 'SACOS 55 LBS', '55', '1.57', 'SOLIDO'),
    ('AOS-1003', 'ACIDO CITRICO GRANULADO (TAMBORES-55 GLS)', 'TAMBOR 55 GLS', '0', '1.66', 'LIQUIDO'),
    ('AOS-1004', 'ACIDO CITRICO GRANULADO 2918.14.00', 'SACOS DE 55 LBS', '55', '1.66', 'SOLIDO'),
    ('AOS-1005', 'ALCOHOL METANOL (TAMBOR) 208 LT', 'TAMBOR 55 GLS', '0', '0.79', 'LIQUIDO'),
    ('AOS-1006', 'ALMIDON (DRILLANYL STAECHE WP) (SACOS DE 25 KG)', 'SACOS 55 LBS', '55', '1.50', 'SOLIDO'),
    ('AOS-1007', 'BARITA (SACOS DE 100 LBS)', 'SACOS 100 LBS', '100', '4.20', 'SOLIDO'),
    ('AOS-1008', 'BARITA (SACOS DE 55 LBS)', 'SACOS 55 LBS', '55', '4.20', 'SOLIDO'),
    ('AOS-1009', 'BENTONITA (SACOS 25 KG)', 'SACOS 113 LBS', '113', '2.60', 'SOLIDO'),
    ('AOS-1010', 'CAL HIDRATADA (SACOS 20 KG)', 'SACOS 44 LBS', '44', '2.24', 'SOLIDO'),
    ('AOS-1011', 'CARBONATO MICRAWHIT 30TT (SACOS 30 KG)', 'SACOS 66 LBS', '66', '2.71', 'SOLIDO'),
    ('AOS-1012', 'CARBONATO PROPYLENE -(TOTE 1000 LT)', 'TOTEMS', '0', '1.20', 'LIQUIDO'),
    ('AOS-1013', 'CLORURO DE CALCIO (SACOS 25 KG)', 'SACOS 55 LBS', '55', '2.15', 'SOLIDO'),
    ('AOS-1014', 'COAGULANTE (SACOS 25 KG)', 'SACOS 55 LBS', '55', '1.30', 'SOLIDO'),
    ('AOS-1015', 'COAGULANTE LIQUIDO (TAMBOR) 208 LT', 'TAMBOR 55 GLS', '0', '1.10', 'LIQUIDO'),
    ('AOS-1016', 'GOMA XANTHAN CLARIFICADA (SACOS 25 LBS)', 'SACOS 25 LBS', '25', '1.50', 'SOLIDO'),
    ('AOS-1017', 'M.E.A (AOS) (TOTE 1000 LT)', 'TOTEMS', '0', '1.01', 'LIQUIDO'),
    ('AOS-1018', 'LIGNITO CAUSTIZEC 3803.02.90.00 (SACOS 25 KG)', 'SACOS 55 LBS', '55', '1.40', 'SOLIDO'),
    ('AOS-1019', 'NEWCHEM 169 (TAMBORES-55 GLS)', 'TAMBOR 55 GLS', '0', '1.05', 'LIQUIDO'),
    ('AOS-1020', 'NEWCHEM 920 (TAMBORES-55 GLS)', 'TAMBOR 55 GLS', '0', '1.08', 'LIQUIDO'),
    ('AOS-1021', 'NEWSEC 01 (TAMBORES-55 GLS)', 'TAMBOR 55 GLS', '0', '0.98', 'LIQUIDO'),
    ('AOS-1022', 'SHALELUBE (TAMBORES-55 GLS)', 'TAMBOR 55 GLS', '0', '0.92', 'LIQUIDO'),
    ('AOS-1023', 'SULFATO DE ALUMINIO (SACOS 40 KG)', 'SACOS 88 LBS', '88', '1.69', 'SOLIDO'),
    ('AOS-1024', 'TOFA (AOS)- (TAMBORES-55 GLS)', 'TAMBOR 55 GLS', '0', '0.93', 'LIQUIDO'),
    ('AOS-1025', 'BRIDGESAL ULTRA (SACOS 25 KG)', 'SACOS 55 LBS', '55', '2.10', 'SOLIDO'),
    ('AOS-1026', 'FLOCCUPOL (SACOS 25 KG)', 'SACOS 55 LBS', '55', '1.25', 'SOLIDO'),
    ('AOS-1027', 'GEL TONE (SACOS 25 KG)', 'SACOS 55 LBS', '55', '1.70', 'SOLIDO'),
    ('AOS-1028', 'GOMA XANTHAN (SACOS 25 LBS)', 'SACOS 25 LBS', '25', '1.50', 'SOLIDO'),
    ('AOS-1029', 'HEC SOLIDO (SACOS 25 KG)', 'SACOS 55 LBS', '55', '1.35', 'SOLIDO'),
    ('AOS-1030', 'MAGNESIO MUERTO (SACOS)', 'SACOS 55 LBS', '55', '3.58', 'SOLIDO'),
    ('AOS-1031', 'PAC LV 3912.31.00 (Celulosa Polianionica de Baja viscocidasd) Sacos de 25 KG', 'SACOS 55 LBS', '55', '1.55', 'SOLIDO'),
    ('AOS-1032', 'SAL FINA (SACOS 25 KG)', 'SACOS 55 LBS', '55', '2.16', 'SOLIDO'),
    ('AOS-1033', 'SAL INDUSTRIAL (SACOS 40 KG)', 'SACOS 88 LBS', '88', '2.16', 'SOLIDO'),
    ('AOS-1034', 'SHALE INHIBIDOR 3824.99,90 (AMINA) (TOTE 1000 LT)', 'TOTEMS', '0', '1.02', 'LIQUIDO'),
    ('AOS-1035', 'SODA CAUSTICA (SACOS DE 25 kg)', 'SACOS 55 LBS', '55', '2.13', 'SOLIDO'),
    ('AOS-1036', 'SODIUM POLYACRYLATE 40% (TAMBORES)', 'TAMBOR 55 GLS', '0', '1.28', 'LIQUIDO'),
    ('AOS-1037', 'STRATABEAD SACOS (25 LBS)', '25 LBS', '25', '1.45', 'SOLIDO'),
    ('AOS-1038', 'SURFACTANTE BASE AGUA Surflub-2603', 'TAMBOR 55 GLS', '0', '1.04', 'LIQUIDO'),
    ('AOS-LIQ-01', 'Salmuera de Cloruro de Calcio densidad 11 LPG', 'BLS', '0', '11.0', 'LIQUIDO'),
    ('AOS-LIQ-02', 'Samuera de Cloruro de Sodio Nacl densidad 10.0 LPG', 'BLS', '0', '10.0', 'LIQUIDO'),
    ('WELL-001', 'BENTONITE WYOMING', '100. LB BG', '100', '2.60', 'SOLIDO'),
    ('WELL-002', 'CALCIUM CARBONATE #6', '50. LB BG', '50', '2.71', 'SOLIDO'),
    ('WELL-003', 'CAUSTIC POTASH (POTASSIUM', '25. KG BG', '55', '2.04', 'SOLIDO'),
    ('WELL-004', 'CAUSTIC SODA', '25. KG BG', '55', '2.13', 'SOLIDO'),
    ('WELL-005', 'CELL-U-SEAL FINE', '30. LB BG', '30', '1.30', 'SOLIDO'),
    ('WELL-006', 'DEFOAM X', '5. GA CN', '0', '0.95', 'SOLIDO'),
    ('WELL-007', 'DRIL-KLEEN', '5. GA CN', '0', '1.02', 'SOLIDO'),
    ('WELL-008', 'DUO-VIS', '25. KG BG', '55', '1.50', 'SOLIDO'),
    ('WELL-009', 'ENGINEERING SERVICE', '1. EA', '0', '1', 'SOLIDO'),
    ('WELL-010', 'G-SEAL PLUS', '25. KG BG', '55', '1.70', 'SOLIDO'),
    ('WELL-011', 'LIME', '20. KG BG', '44', '2.24', 'SOLIDO'),
    ('WELL-012', 'LOWA TECH 70/75', '50. LB BG', '50', '2.60', 'SOLIDO'),
    ('WELL-013', 'M-I BAR BULK', '100. LB BG', '100', '4.20', 'SOLIDO'),
]


class Command(BaseCommand):
    help = "Carga el catálogo de productos de AOS (solo crea los que faltan)."

    @transaction.atomic
    def handle(self, *args, **options):
        creados = 0
        for codigo, descripcion, unidad, libraje, gravedad, categoria in CATALOGO_AOS:
            _, creado = Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'descripcion': descripcion,
                    'unidad': unidad,
                    'libraje': Decimal(libraje),
                    'gravedad': Decimal(gravedad),
                    'categoria': categoria,
                },
            )
            creados += creado
        self.stdout.write(f"Catálogo de productos: {creados} creados, "
                          f"{len(CATALOGO_AOS) - creados} ya existían.")
