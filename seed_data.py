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

PRODUCTOS_LIQUIDOS = [
    {
        "codigo": "AOS-LIQ-01",
        "descripcion": "Salmuera de Cloruro de Calcio densidad 11 LPG",
        "unidad": "BLS",
        "libraje": "N/A",
        "gravedad_especifica": "11.0 LPG",
        "cantidad": 300,
        "precio_unitario": 85.00
    },
    {
        "codigo": "AOS-LIQ-02",
        "descripcion": "Samuera de Cloruro de Sodio Nacl densidad 10.0 LPG",
        "unidad": "BLS",
        "libraje": "N/A",
        "gravedad_especifica": "10.0 LPG",
        "cantidad": 160,
        "precio_unitario": 65.00
    }
]

PRODUCTOS_WELLSITE = [
    {
        "codigo": "WELL-001",
        "descripcion": "BENTONITE WYOMING",
        "unidad": "100. LB BG",
        "libraje": "100 LBS",
        "gravedad_especifica": "2.60",
        "cantidad": 55,
        "stock_inicial": 55,
        "precio_unitario": 28.72,
        "cum_used": 445,
        "daily_received": 0,
        "cum_received": 500,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-002",
        "descripcion": "CALCIUM CARBONATE #6",
        "unidad": "50. LB BG",
        "libraje": "50 LBS",
        "gravedad_especifica": "2.71",
        "cantidad": 112,
        "stock_inicial": 112,
        "precio_unitario": 18.45,
        "cum_used": 0,
        "daily_received": 0,
        "cum_received": 112,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-003",
        "descripcion": "CAUSTIC POTASH (POTASSIUM",
        "unidad": "25. KG BG",
        "libraje": "55 LBS",
        "gravedad_especifica": "2.04",
        "cantidad": 14,
        "stock_inicial": 14,
        "precio_unitario": 113.32,
        "cum_used": 0,
        "daily_received": 0,
        "cum_received": 14,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-004",
        "descripcion": "CAUSTIC SODA",
        "unidad": "25. KG BG",
        "libraje": "55 LBS",
        "gravedad_especifica": "2.13",
        "cantidad": 2,
        "stock_inicial": 9,
        "precio_unitario": 64.72,
        "cum_used": 28,
        "daily_received": 0,
        "cum_received": 30,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-005",
        "descripcion": "CELL-U-SEAL FINE",
        "unidad": "30. LB BG",
        "libraje": "30 LBS",
        "gravedad_especifica": "1.30",
        "cantidad": 114,
        "stock_inicial": 114,
        "precio_unitario": 69.67,
        "cum_used": 0,
        "daily_received": 0,
        "cum_received": 114,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-006",
        "descripcion": "DEFOAM X",
        "unidad": "5. GA CN",
        "libraje": "N/A",
        "gravedad_especifica": "0.95",
        "cantidad": 21,
        "stock_inicial": 21,
        "precio_unitario": 387.61,
        "cum_used": 9,
        "daily_received": 0,
        "cum_received": 30,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-007",
        "descripcion": "DRIL-KLEEN",
        "unidad": "5. GA CN",
        "libraje": "N/A",
        "gravedad_especifica": "1.02",
        "cantidad": 20,
        "stock_inicial": 20,
        "precio_unitario": 322.21,
        "cum_used": 2,
        "daily_received": 0,
        "cum_received": 45,
        "daily_return": 23,
        "cum_return": 0
    },
    {
        "codigo": "WELL-008",
        "descripcion": "DUO-VIS",
        "unidad": "25. KG BG",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.50",
        "cantidad": 32,
        "stock_inicial": 10,
        "precio_unitario": 550.12,
        "cum_used": 56,
        "daily_received": 30,
        "cum_received": 88,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-009",
        "descripcion": "ENGINEERING SERVICE",
        "unidad": "1. EA",
        "libraje": "N/A",
        "gravedad_especifica": "N/A",
        "cantidad": 0,
        "stock_inicial": 0,
        "precio_unitario": 1485.00,
        "cum_used": 27,
        "daily_received": 0,
        "cum_received": 0,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-010",
        "descripcion": "G-SEAL PLUS",
        "unidad": "25. KG BG",
        "libraje": "55 LBS",
        "gravedad_especifica": "1.70",
        "cantidad": 35,
        "stock_inicial": 35,
        "precio_unitario": 178.41,
        "cum_used": 0,
        "daily_received": 0,
        "cum_received": 35,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-011",
        "descripcion": "LIME",
        "unidad": "20. KG BG",
        "libraje": "44 LBS",
        "gravedad_especifica": "2.24",
        "cantidad": 89,
        "stock_inicial": 89,
        "precio_unitario": 37.43,
        "cum_used": 0,
        "daily_received": 0,
        "cum_received": 89,
        "daily_return": 0,
        "cum_return": 0
    },
    {
        "codigo": "WELL-012",
        "descripcion": "LOWA TECH 70/75",
        "unidad": "50. LB BG",
        "libraje": "50 LBS",
        "gravedad_especifica": "2.60",
        "cantidad": 112,
        "stock_inicial": 112,
        "precio_unitario": 18.45,
        "cum_used": 0,
        "daily_received": 0,
        "cum_received": 224,
        "daily_return": 0,
        "cum_return": 112
    },
    {
        "codigo": "WELL-013",
        "descripcion": "M-I BAR BULK",
        "unidad": "100. LB BG",
        "libraje": "100 LBS",
        "gravedad_especifica": "4.20",
        "cantidad": 1903,
        "stock_inicial": 1903,
        "precio_unitario": 20.25,
        "cum_used": 2456,
        "daily_received": 0,
        "cum_received": 4359,
        "daily_return": 0,
        "cum_return": 0
    }
]


def seed_database():
    """Ejecuta la carga inicial de productos en la base de datos divididos por categorías."""
    print("Iniciando inyección de datos para Proyecto Chapala...")
    creados = 0
    actualizados = 0

    # 1. Productos Químicos AOS
    for item in PRODUCTOS_AOS:
        prod, created = Producto.objects.update_or_create(
            codigo=item["codigo"],
            defaults={
                "descripcion": item["descripcion"],
                "unidad": item["unidad"],
                "libraje": item.get("libraje", "N/A"),
                "gravedad_especifica": item.get("gravedad_especifica", "N/A"),
                "cantidad": item["cantidad"],
                "stock_inicial": item["cantidad"],
                "categoria": "quimico",
                "precio_unitario": item.get("precio_unitario", 45.00),
                "activo": True
            }
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    # 2. Productos Líquidos AOS (Imagen 1)
    for item in PRODUCTOS_LIQUIDOS:
        prod, created = Producto.objects.update_or_create(
            codigo=item["codigo"],
            defaults={
                "descripcion": item["descripcion"],
                "unidad": item["unidad"],
                "libraje": item.get("libraje", "N/A"),
                "gravedad_especifica": item.get("gravedad_especifica", "N/A"),
                "cantidad": item["cantidad"],
                "stock_inicial": item["cantidad"],
                "categoria": "liquido",
                "precio_unitario": item.get("precio_unitario", 65.00),
                "activo": True
            }
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    # 3. Wellsite Chemical Inventory (Imagen 2)
    for item in PRODUCTOS_WELLSITE:
        prod, created = Producto.objects.update_or_create(
            codigo=item["codigo"],
            defaults={
                "descripcion": item["descripcion"],
                "unidad": item["unidad"],
                "libraje": item.get("libraje", "N/A"),
                "gravedad_especifica": item.get("gravedad_especifica", "N/A"),
                "cantidad": item["cantidad"],
                "stock_inicial": item.get("stock_inicial", item["cantidad"]),
                "categoria": "wellsite",
                "precio_unitario": item.get("precio_unitario", 0.00),
                "cum_used": item.get("cum_used", 0),
                "daily_received": item.get("daily_received", 0),
                "cum_received": item.get("cum_received", 0),
                "daily_return": item.get("daily_return", 0),
                "cum_return": item.get("cum_return", 0),
                "activo": True
            }
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    # Asegura reporte diario inicial con metadatos Wellsite
    reporte = ReporteDiario.objects.filter(
        departamento="ALMACÉN",
        encargado="LUIS BRICEÑO"
    ).first()
    if not reporte:
        reporte = ReporteDiario.objects.create(
            departamento="ALMACÉN",
            encargado="LUIS BRICEÑO",
            elaborado_por_nombre="Lusneila Franceschi",
            elaborado_por_cargo="Administración",
            revisado_por_nombre="Luis Briceño",
            revisado_por_cargo="Encargado de Almacen",
            operador="Cardon IV",
            pozo="Perla-1X",
            locacion="Offshore",
            reporte_no_wellsite="16"
        )

    print(f"Éxito: {creados} productos creados, {actualizados} actualizados.")
    print(f"Total de productos en base de datos: {Producto.objects.count()}")


if __name__ == "__main__":
    seed_database()


