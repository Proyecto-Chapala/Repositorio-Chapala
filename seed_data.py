"""
================================================================================
SCRIPT DE CARGA INICIAL DE PRODUCTOS QUÍMICOS (SEED DATA)
================================================================================
Inyecta en la base de datos (PostgreSQL o SQLite) los 38 productos químicos
oficiales de la planilla AOS (All Oil Services, C.A.) con sus especificaciones:
- Código SKU
- Descripción
- Unidad / Presentación
- Libraje
- Gravedad Específica
- Cantidad (Stock inicial)
================================================================================
"""

import os
import sys
import django

# Configuración del entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chapala.settings')
django.setup()

from mychapala.models import Producto, ReporteDiario

PRODUCTOS_AOS = [
    {
        "codigo": "AOS-1001",
        "descripcion": "ACETROL - ACETATO (TAMBOR 55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "0.89",
        "cantidad": 8
    },
    {
        "codigo": "AOS-1002",
        "descripcion": "ACETATO DE POTASIO (SACOS DE 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.57",
        "cantidad": 439
    },
    {
        "codigo": "AOS-1003",
        "descripcion": "ACIDO CITRICO GRANULADO (TAMBORES-55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "1.66",
        "cantidad": 2
    },
    {
        "codigo": "AOS-1004",
        "descripcion": "ACIDO CITRICO GRANULADO 2918.14.00",
        "unidad": "SACOS DE 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.66",
        "cantidad": 110
    },
    {
        "codigo": "AOS-1005",
        "descripcion": "ALCOHOL METANOL (TAMBOR) 208 LT",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "0.79",
        "cantidad": 1
    },
    {
        "codigo": "AOS-1006",
        "descripcion": "ALMIDON (DRILLANYL STAECHE WP) (SACOS DE 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.50",
        "cantidad": 240
    },
    {
        "codigo": "AOS-1007",
        "descripcion": "BARITA (SACOS DE 100 LBS)",
        "unidad": "SACOS 100 LBS",
        "libraje": "100 LBS",
        "gravedad_especifica": "4.20",
        "cantidad": 5037
    },
    {
        "codigo": "AOS-1008",
        "descripcion": "BARITA (SACOS DE 55 LBS)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "4.20",
        "cantidad": 19
    },
    {
        "codigo": "AOS-1009",
        "descripcion": "BENTONITA (SACOS 25 KG)",
        "unidad": "SACOS 113 LBS",
        "libraje": "113 LBS",
        "gravedad_especifica": "2.60",
        "cantidad": 910
    },
    {
        "codigo": "AOS-1010",
        "descripcion": "CAL HIDRATADA (SACOS 20 KG)",
        "unidad": "SACOS 44 LBS",
        "libraje": "44 LBS",
        "gravedad_especifica": "2.24",
        "cantidad": 1986
    },
    {
        "codigo": "AOS-1011",
        "descripcion": "CARBONATO MICRAWHIT 30TT (SACOS 30 KG)",
        "unidad": "SACOS 66 LBS",
        "libraje": "66 LBS",
        "gravedad_especifica": "2.71",
        "cantidad": 30
    },
    {
        "codigo": "AOS-1012",
        "descripcion": "CARBONATO PROPYLENE -(TOTE 1000 LT)",
        "unidad": "TOTEMS",
        "libraje": "N/A",
        "gravedad_especifica": "1.20",
        "cantidad": 14
    },
    {
        "codigo": "AOS-1013",
        "descripcion": "CLORURO DE CALCIO (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "2.15",
        "cantidad": 2548
    },
    {
        "codigo": "AOS-1014",
        "descripcion": "COAGULANTE (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.30",
        "cantidad": 3378
    },
    {
        "codigo": "AOS-1015",
        "descripcion": "COAGULANTE LIQUIDO (TAMBOR) 208 LT",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "1.10",
        "cantidad": 1
    },
    {
        "codigo": "AOS-1016",
        "descripcion": "GOMA XANTHAN CLARIFICADA (SACOS 25 LBS)",
        "unidad": "SACOS 25 LBS",
        "libraje": "25 LBS",
        "gravedad_especifica": "1.50",
        "cantidad": 320
    },
    {
        "codigo": "AOS-1017",
        "descripcion": "M.E.A (AOS) (TOTE 1000 LT)",
        "unidad": "TOTEMS",
        "libraje": "N/A",
        "gravedad_especifica": "1.01",
        "cantidad": 12
    },
    {
        "codigo": "AOS-1018",
        "descripcion": "LIGNITO CAUSTIZEC 3803.02.90.00 (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.40",
        "cantidad": 240
    },
    {
        "codigo": "AOS-1019",
        "descripcion": "NEWCHEM 169 (TAMBORES-55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "1.05",
        "cantidad": 20
    },
    {
        "codigo": "AOS-1020",
        "descripcion": "NEWCHEM 920 (TAMBORES-55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "1.08",
        "cantidad": 29
    },
    {
        "codigo": "AOS-1021",
        "descripcion": "NEWSEC 01 (TAMBORES-55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "0.98",
        "cantidad": 24
    },
    {
        "codigo": "AOS-1022",
        "descripcion": "SHALELUBE (TAMBORES-55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "0.92",
        "cantidad": 20
    },
    {
        "codigo": "AOS-1023",
        "descripcion": "SULFATO DE ALUMINIO (SACOS 40 KG)",
        "unidad": "SACOS 88 LBS",
        "libraje": "88 LBS",
        "gravedad_especifica": "1.69",
        "cantidad": 1246
    },
    {
        "codigo": "AOS-1024",
        "descripcion": "TOFA (AOS)- (TAMBORES-55 GLS)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "0.93",
        "cantidad": 92
    },
    {
        "codigo": "AOS-1025",
        "descripcion": "BRIDGESAL ULTRA (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "2.10",
        "cantidad": 187
    },
    {
        "codigo": "AOS-1026",
        "descripcion": "FLOCCUPOL (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.25",
        "cantidad": 2403
    },
    {
        "codigo": "AOS-1027",
        "descripcion": "GEL TONE (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.70",
        "cantidad": 30
    },
    {
        "codigo": "AOS-1028",
        "descripcion": "GOMA XANTHAN (SACOS 25 LBS)",
        "unidad": "SACOS 25 LBS",
        "libraje": "25 LBS",
        "gravedad_especifica": "1.50",
        "cantidad": 0
    },
    {
        "codigo": "AOS-1029",
        "descripcion": "HEC SOLIDO (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.35",
        "cantidad": 0
    },
    {
        "codigo": "AOS-1030",
        "descripcion": "MAGNESIO MUERTO (SACOS)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "3.58",
        "cantidad": 800
    },
    {
        "codigo": "AOS-1031",
        "descripcion": "PAC LV 3912.31.00 (Celulosa Polianionica de Baja viscocidasd) Sacos de 25 KG",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.55",
        "cantidad": 320
    },
    {
        "codigo": "AOS-1032",
        "descripcion": "SAL FINA (SACOS 25 KG)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "2.16",
        "cantidad": 0
    },
    {
        "codigo": "AOS-1033",
        "descripcion": "SAL INDUSTRIAL (SACOS 40 KG)",
        "unidad": "SACOS 88 LBS",
        "libraje": "88 LBS",
        "gravedad_especifica": "2.16",
        "cantidad": 2251
    },
    {
        "codigo": "AOS-1034",
        "descripcion": "SHALE INHIBIDOR 3824.99,90 (AMINA) (TOTE 1000 LT)",
        "unidad": "TOTEMS",
        "libraje": "N/A",
        "gravedad_especifica": "1.02",
        "cantidad": 14
    },
    {
        "codigo": "AOS-1035",
        "descripcion": "SODA CAUSTICA (SACOS DE 25 kg)",
        "unidad": "SACOS 55 LBS",
        "libraje": "55 LBS",
        "gravedad_especifica": "2.13",
        "cantidad": 280
    },
    {
        "codigo": "AOS-1036",
        "descripcion": "SODIUM POLYACRYLATE 40% (TAMBORES)",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "1.28",
        "cantidad": 4
    },
    {
        "codigo": "AOS-1037",
        "descripcion": "STRATABEAD SACOS (25 LBS)",
        "unidad": "25 LBS",
        "libraje": "25 LBS",
        "gravedad_especifica": "1.45",
        "cantidad": 320
    },
    {
        "codigo": "AOS-1038",
        "descripcion": "SURFACTANTE BASE AGUA Surflub-2603",
        "unidad": "TAMBOR 55 GLS",
        "libraje": "N/A",
        "gravedad_especifica": "1.04",
        "cantidad": 10
    }
]


def seed_database():
    """Ejecuta la carga inicial de los 38 reactivos en la base de datos."""
    print("Iniciando inyección de datos para Proyecto Chapala...")
    creados = 0
    actualizados = 0

    for item in PRODUCTOS_AOS:
        prod, created = Producto.objects.update_or_create(
            codigo=item["codigo"],
            defaults={
                "descripcion": item["descripcion"],
                "unidad": item["unidad"],
                "libraje": item["libraje"],
                "gravedad_especifica": item["gravedad_especifica"],
                "cantidad": item["cantidad"],
                "stock_inicial": item["cantidad"],
                "activo": True
            }
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    # Asegura reporte diario inicial
    reporte, _ = ReporteDiario.objects.get_or_create(
        departamento="ALMACÉN",
        encargado="LUIS BRICEÑO",
        elaborado_por_nombre="Lusneila Franceschi",
        elaborado_por_cargo="Administración",
        revisado_por_nombre="Luis Briceño",
        revisado_por_cargo="Encargado de Almacen"
    )

    print(f"Éxito: {creados} productos creados, {actualizados} actualizados.")
    print(f"Total de productos en base de datos: {Producto.objects.count()}")


if __name__ == "__main__":
    seed_database()

