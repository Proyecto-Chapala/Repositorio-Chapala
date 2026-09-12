"""
================================================================================
SCRIPT DE CARGA INICIAL (SEED) PARA LA APP 'REPORTES' (ESQUEMA ONE-TRAX)
================================================================================
Puebla los datos maestros necesarios para que el módulo de reportes funcione
al 100%:
1. Sistemas de Fluido (Base Agua, Polimérico, Base Aceite, Sintético).
2. Pozo de referencia (PERLA-1X) con su ubicación y operador.
3. Intervalo 1 (Hoyo 12-1/4", Profundidad Inicial 0.00 ft, Lodo Polimérico KCl).
4. Tubería instalada (Revestidor 9-5/8").
5. Catálogo de 53 Productos sincronizados desde mychapala hacia reportes.Producto.
6. Catálogo de Equipos de control de sólidos y fluidos.
7. Un Reporte Diario de prueba con Muestra, Inventario, Uso de Material,
   Uso de Equipos y Comentarios.
================================================================================
"""

import os
import re
import sys
from decimal import Decimal, InvalidOperation

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chapala.settings")
django.setup()

from reportes.models import (
    Pozo,
    SistemaFluido,
    Intervalo,
    TuberiaInstalada,
    Producto as ProductoReportes,
    Equipo,
    ReporteDiario,
    MuestraFluido,
    PropiedadCatalogo,
    PropiedadValor,
    InventarioItem,
    UsoMaterial,
    UsoEquipo,
    Comentario,
)
from mychapala.models import Producto as ProductoChapala


def seed_sistemas_fluido():
    print("\n--- 1. Poblando Sistemas de Fluido ---")
    sistemas = [
        {
            "nombre": "Lodo Base Agua (WBM / CALDRIL)",
            "categoria": SistemaFluido.Categoria.AGUA,
            "descripcion": "Sistema de fluido base agua convencional y bentonítico para perforación de formaciones superiores.",
        },
        {
            "nombre": "Lodo Polimérico KCl",
            "categoria": SistemaFluido.Categoria.POLIMERICO,
            "descripcion": "Lodo polimérico inhibido con cloruro de potasio para estabilización de lutitas reactivas.",
        },
        {
            "nombre": "Lodo Base Aceite (OBM)",
            "categoria": SistemaFluido.Categoria.ACEITE,
            "descripcion": "Emulsión inversa con fase continua de aceite diesel o mineral para alta lubricidad y estabilidad térmica.",
        },
        {
            "nombre": "Lodo Sintético (SBM)",
            "categoria": SistemaFluido.Categoria.SINTETICO,
            "descripcion": "Fluido de perforación a base de ésteres, parafinas lineales o alfa-olefinas para máxima protección ambiental.",
        },
    ]

    creados = 0
    for data in sistemas:
        obj, created = SistemaFluido.objects.update_or_create(
            nombre=data["nombre"],
            defaults={"categoria": data["categoria"], "descripcion": data["descripcion"]},
        )
        if created:
            creados += 1
            print(f"  [+] Creado sistema: {obj.nombre} ({obj.get_categoria_display()})")
        else:
            print(f"  [=] Existente sistema: {obj.nombre}")
    print(f"Total Sistemas de Fluido disponibles: {SistemaFluido.objects.count()}")


def seed_pozo_e_intervalo():
    print("\n--- 2. Poblando Pozo e Intervalo de Referencia ---")
    pozo, created = Pozo.objects.update_or_create(
        nombre="PERLA-1X",
        defaults={
            "operador": "REPSOL / ENI",
            "ubicacion": "Golfo de Venezuela - Bloque Cardón IV",
            "campo_area": "Cardón IV",
            "fecha_spud": "2026-08-01",
        },
    )
    if created:
        print(f"  [+] Creado Pozo: {pozo.nombre} - Operador: {pozo.operador}")
    else:
        print(f"  [=] Existente Pozo: {pozo.nombre}")

    sistema_polimerico = SistemaFluido.objects.get(nombre="Lodo Polimérico KCl")

    intervalo, created = Intervalo.objects.update_or_create(
        pozo=pozo,
        numero=1,
        defaults={
            "sistema_fluido": sistema_polimerico,
            "profundidad_inicial": Decimal("0.00"),
            "diametro": Decimal("12.250"),
            "estado": Intervalo.Estado.ABIERTO,
        },
    )
    if created:
        print(f"  [+] Creado Intervalo 1 para {pozo.nombre} (Hoyo {intervalo.diametro}\")")
    else:
        print(f"  [=] Existente Intervalo 1 para {pozo.nombre}")

    # Tubería instalada
    tuberia, created = TuberiaInstalada.objects.update_or_create(
        intervalo=intervalo,
        tipo=TuberiaInstalada.Tipo.REVESTIDOR,
        diametro_externo=Decimal("9.625"),
        defaults={
            "diametro_interno": Decimal("8.921"),
            "longitud": Decimal("1200.00"),
        },
    )
    if created:
        print(f"  [+] Creada Tubería: Revestidor 9-5/8\" (Longitud: 1200 ft)")
    else:
        print(f"  [=] Existente Tubería: Revestidor 9-5/8\"")

    return pozo, intervalo


def clean_decimal(val, default="1.000"):
    """Limpia textos como '11.0 LPG' o 'N/A' y extrae un Decimal válido."""
    if not val:
        return Decimal(default)
    # Extraer el primer número decimal o entero en el string
    match = re.search(r"[-+]?\d*\.?\d+", str(val))
    if match:
        try:
            return Decimal(match.group(0))
        except InvalidOperation:
            pass
    return Decimal(default)


def seed_productos():
    print("\n--- 3. Sincronizando Productos de mychapala hacia reportes.Producto ---")
    productos_chapala = ProductoChapala.objects.filter(activo=True)
    print(f"Se encontraron {productos_chapala.count()} productos en mychapala.")

    sincronizados = 0
    for p in productos_chapala:
        # Extraer campos unitarios con valores seguros
        cant_unit = p.cantidad_unitaria if p.cantidad_unitaria is not None else Decimal("55.00")
        unidad_m = p.unidad_medida if p.unidad_medida in ("LB", "KG", "GA", "EA") else "LB"
        tipo_emp = p.tipo_empaque if p.tipo_empaque in ("BG", "CN", "DM", "TOTE", "BLS", "EA") else "BG"
        precio = p.precio_unitario if p.precio_unitario is not None else Decimal("45.00")
        grav_esp = clean_decimal(p.gravedad_especifica, "1.250")

        # Asegurar longitud máxima en gravedad específica Decimal(5, 3) (máx 99.999)
        if grav_esp > Decimal("99.999"):
            grav_esp = Decimal("99.999")

        obj, created = ProductoReportes.objects.update_or_create(
            codigo=p.codigo,
            defaults={
                "nombre": p.descripcion,
                "cantidad_unitaria": cant_unit,
                "unidad_medida": unidad_m,
                "tipo_empaque": tipo_emp,
                "precio_unitario": precio,
                "gravedad_especifica": grav_esp,
            },
        )
        sincronizados += 1

    print(f"Total productos en reportes.Producto: {ProductoReportes.objects.count()} (sincronizados: {sincronizados})")


def seed_equipos():
    print("\n--- 4. Poblando Catálogo de Equipos de Control de Sólidos ---")
    equipos = [
        {"codigo": "EQ-SHK-01", "nombre": "Zaranda Primaria 1 (Shaker Brandt)", "costo_diario": Decimal("120.00")},
        {"codigo": "EQ-SHK-02", "nombre": "Zaranda Primaria 2 (Shaker Brandt)", "costo_diario": Decimal("120.00")},
        {"codigo": "EQ-CENT-01", "nombre": "Centrífuga de Decantación Alta Velocidad", "costo_diario": Decimal("250.00")},
        {"codigo": "EQ-DEGAS-01", "nombre": "Desgasificador de Vacío M-I SWACO", "costo_diario": Decimal("85.00")},
        {"codigo": "EQ-AGIT-01", "nombre": "Agitadores Mecánicos de Tanques (Set)", "costo_diario": Decimal("50.00")},
    ]

    for data in equipos:
        obj, created = Equipo.objects.update_or_create(
            codigo=data["codigo"],
            defaults={"nombre": data["nombre"], "costo_diario": data["costo_diario"]},
        )
        if created:
            print(f"  [+] Creado Equipo: {obj.codigo} - {obj.nombre} (${obj.costo_diario}/día)")
        else:
            print(f"  [=] Existente Equipo: {obj.codigo}")
    print(f"Total Equipos disponibles: {Equipo.objects.count()}")


def seed_reporte_ejemplo(intervalo):
    print("\n--- 5. Poblando Reporte Diario Inicial de Ejemplo ---")
    fecha_reporte = "2026-08-17"
    reporte, created = ReporteDiario.objects.get_or_create(
        intervalo=intervalo,
        fecha=fecha_reporte,
        defaults={
            "actividad": "Perforando hoyo 12-1/4\" de 1,200 ft a 1,850 ft con lodo polimérico KCl.",
            "peso_lodo": Decimal("9.40"),
        },
    )
    if created:
        print(f"  [+] Creado Reporte Diario N° {reporte.numero_reporte} (Fecha: {reporte.fecha})")
    else:
        print(f"  [=] Existente Reporte Diario N° {reporte.numero_reporte}")

    # 1. Muestra y valores de matriz de propiedades
    muestra, m_created = MuestraFluido.objects.get_or_create(
        reporte=reporte,
        identificador="TK 2 20:00",
        defaults={"orden": 1},
    )
    if m_created:
        print(f"  [+] Creada Muestra: {muestra.identificador}")
        # Asignar algunas propiedades comunes habilitadas para lodo polimérico
        propiedades_demo = {
            "mud_weight": Decimal("9.40"),
            "funnel_viscosity": Decimal("48.0"),
            "pv": Decimal("16.0"),
            "yp": Decimal("22.0"),
            "gel_10s": Decimal("6.0"),
            "gel_10m": Decimal("14.0"),
            "ph_agua": Decimal("9.2"),
            "potassium_cl_kcl": Decimal("18000.0"),
        }
        for codigo, valor in propiedades_demo.items():
            try:
                prop = PropiedadCatalogo.objects.get(codigo=codigo)
                PropiedadValor.objects.update_or_create(
                    muestra=muestra,
                    propiedad=prop,
                    defaults={"valor": valor},
                )
            except PropiedadCatalogo.DoesNotExist:
                pass
        print("  [+] Valores de matriz de propiedades guardados para la muestra.")

    # 2. Inventario y Uso de Materiales
    # Seleccionar 2 productos existentes para el reporte
    prod_bentonita = ProductoReportes.objects.filter(codigo__icontains="1008").first() or ProductoReportes.objects.first()
    prod_soda = ProductoReportes.objects.filter(codigo__icontains="1032").first() or ProductoReportes.objects.last()

    if prod_bentonita:
        item1, _ = InventarioItem.objects.update_or_create(
            reporte=reporte,
            producto=prod_bentonita,
            defaults={"cantidad_inicial": Decimal("150.00"), "cantidad_entrada": Decimal("50.00")},
        )
        UsoMaterial.objects.get_or_create(
            reporte=reporte,
            producto=prod_bentonita,
            defaults={"cantidad_usada": Decimal("20.00")},
        )
        item1.save()  # recalcula cantidad_final
        print(f"  [+] Inventario y consumo registrado para: {prod_bentonita.nombre}")

    if prod_soda and prod_soda != prod_bentonita:
        item2, _ = InventarioItem.objects.update_or_create(
            reporte=reporte,
            producto=prod_soda,
            defaults={"cantidad_inicial": Decimal("40.00"), "cantidad_entrada": Decimal("0.00")},
        )
        UsoMaterial.objects.get_or_create(
            reporte=reporte,
            producto=prod_soda,
            defaults={"cantidad_usada": Decimal("5.00")},
        )
        item2.save()
        print(f"  [+] Inventario y consumo registrado para: {prod_soda.nombre}")

    # 3. Uso de Equipos
    eq1 = Equipo.objects.first()
    if eq1:
        UsoEquipo.objects.get_or_create(
            reporte=reporte,
            equipo=eq1,
            defaults={"horas_usadas": Decimal("24.00")},
        )
        print(f"  [+] Uso de equipo registrado: {eq1.nombre} (24 hrs)")

    eq2 = Equipo.objects.filter(codigo__icontains="CENT").first()
    if eq2:
        UsoEquipo.objects.get_or_create(
            reporte=reporte,
            equipo=eq2,
            defaults={"horas_usadas": Decimal("12.00")},
        )
        print(f"  [+] Uso de equipo registrado: {eq2.nombre} (12 hrs)")

    # 4. Comentario
    Comentario.objects.get_or_create(
        reporte=reporte,
        texto="Avance de perforación según programa. Propiedades reológicas estables en todo el turno.",
        defaults={"autor": "Ing. de Fluidos - AOS"},
    )
    print("  [+] Comentario del reporte registrado.")


def main():
    print("=" * 70)
    print("INICIANDO POBLADO DE DATOS MAESTROS DE REPORTES (ONE-TRAX)")
    print("=" * 70)
    seed_sistemas_fluido()
    pozo, intervalo = seed_pozo_e_intervalo()
    seed_productos()
    seed_equipos()
    seed_reporte_ejemplo(intervalo)
    print("\n" + "=" * 70)
    print("POBLADO COMPLETADO EXITOSAMENTE")
    print("=" * 70)


if __name__ == "__main__":
    main()

