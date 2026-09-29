"""
seed_pozo_prueba.py — Management command
Pobla la BD con datos de prueba completos para PRUEBA-001.

Uso:
    python manage.py seed_pozo_prueba
    python manage.py seed_pozo_prueba --reset   (borra y recrea desde cero)
"""

from decimal import Decimal
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from operaciones.models import (
    Pozo, Producto, ProductoActivoPozo,
    WellHeaderInfo, CategoriaPerdidaItem,
    IntervaloRevestimiento, TipoFosa, Fosa,
    AlmacenCodigo, TipoDistribucionTiempo,
    Equipo, EquipoActivoPozo,
)
from operaciones.models_daily_reports import WellSurveyStation


NOMBRE_POZO = "PRUEBA-001"


class Command(BaseCommand):
    help = "Crea / repobla el pozo de prueba PRUEBA-001 con datos en todos los módulos."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Elimina el pozo existente y lo recrea desde cero.'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset'] and Pozo.objects.filter(nombre=NOMBRE_POZO).exists():
            Pozo.objects.filter(nombre=NOMBRE_POZO).delete()
            self.stdout.write(self.style.WARNING(f"[seed] Pozo '{NOMBRE_POZO}' eliminado."))

        # ── 1. POZO ────────────────────────────────────────────────────────
        p, created = Pozo.objects.get_or_create(
            nombre=NOMBRE_POZO,
            defaults=dict(
                sistema_unidades='STANDARD_OILFIELD',
                unidades_bloqueadas=True,
                moneda_simbolo='USD',
                moneda_decimales=2,
                tasa_impuesto=Decimal('16.00'),
                ecuacion_solidos_base_agua='MI',
                ecuacion_solidos_base_aceite='MI',
                usar_api_5ta_edicion_hidraulica=False,
                categoria_perdida_tipo='MI',
                fecha_primera_captura=date(2025, 9, 1),
                tipo_fluido_inicial='WATER_BASE',
                con_tratamiento_disposicion=False,
                numero_control_logit='LOG-PRUEBA-001',
                spud_date_completado=True,
                estado='ACTIVO',
                paso_wizard_actual=4,
            )
        )
        verb = "creado" if created else "ya existía"
        self.stdout.write(self.style.SUCCESS(f"[seed] Pozo '{NOMBRE_POZO}' {verb} (id={p.pk})."))

        # ── 2. WELL HEADER INFO (Información General del Pozo) ─────────────
        WellHeaderInfo.objects.get_or_create(
            pozo=p,
            defaults=dict(
                operador='All Oil Services, C.A.',
                field_area='Campo Motatán Sur',
                descripcion='Pozo vertical de desarrollo – Prueba del sistema',
                ubicacion='Bloque III, Parcela 7, Monagas',
                almacen='Almacén Principal – Anaco',
                contratista='Perforaciones Chapala S.A.',
                nombre_taladro='Taladro No. 4',
                ingeniero_proyecto='Ing. Carlos Pérez',
                ingeniero_miswaco_1='Ing. Ana Torres',
                spud_date=date(2025, 9, 1),
                surface_temp_f=Decimal('80.0'),
                temp_gradient_f_100ft=Decimal('1.5'),
                primary_mud_type_codigo='WBM',
                primary_mud_type_descripcion='Base Agua (WBM)',
                well_type_codigo='DEV',
                well_type_descripcion='Desarrollo',
                completado=True,
                marketing_codes_completado=True,
            )
        )
        self.stdout.write("  ✓ Información General del Pozo")

        # ── 3. CATEGORÍAS DE PÉRDIDA ───────────────────────────────────────
        CategoriaPerdidaItem.sembrar_estandar(p)
        self.stdout.write("  ✓ Categorías de Pérdida (15 categorías estándar M-I)")

        # ── 4. INTERVALOS DE REVESTIMIENTO ────────────────────────────────
        intervalos = [
            dict(numero_intervalo=1, tipo='CONDUCTOR',
                 casing_od_in=Decimal('20.0'), casing_id_in=Decimal('19.0'),
                 hole_size_in=Decimal('26.0'), profundidad_ft=Decimal('300.0'),
                 tvd_ft=Decimal('300.0'), maximum_density_lb_gal=Decimal('9.0'),
                 max_bht_f=Decimal('90.0'), interval_days=2, planned_days=2),
            dict(numero_intervalo=2, tipo='SUPERFICIE',
                 casing_od_in=Decimal('13.375'), casing_id_in=Decimal('12.415'),
                 hole_size_in=Decimal('17.5'), profundidad_ft=Decimal('1800.0'),
                 tvd_ft=Decimal('1800.0'), maximum_density_lb_gal=Decimal('10.5'),
                 max_bht_f=Decimal('130.0'), interval_days=12, planned_days=14),
            dict(numero_intervalo=3, tipo='INTERMEDIO',
                 casing_od_in=Decimal('9.625'), casing_id_in=Decimal('8.835'),
                 hole_size_in=Decimal('12.25'), profundidad_ft=Decimal('4500.0'),
                 tvd_ft=Decimal('4500.0'), maximum_density_lb_gal=Decimal('13.0'),
                 max_bht_f=Decimal('195.0'), interval_days=25, planned_days=30),
            dict(numero_intervalo=4, tipo='PRODUCCION',
                 casing_od_in=Decimal('7.0'), casing_id_in=Decimal('6.276'),
                 hole_size_in=Decimal('8.5'), profundidad_ft=Decimal('7200.0'),
                 tvd_ft=Decimal('7200.0'), maximum_density_lb_gal=Decimal('15.5'),
                 max_bht_f=Decimal('250.0'), interval_days=35, planned_days=40),
        ]
        for data in intervalos:
            IntervaloRevestimiento.objects.get_or_create(
                pozo=p, numero_intervalo=data['numero_intervalo'], defaults=data
            )
        self.stdout.write("  ✓ Intervalos de Revestimiento (4 intervalos)")

        # ── 5. TIPOS DE FOSA ───────────────────────────────────────────────
        TipoFosa.sembrar_estandar(p)
        self.stdout.write("  ✓ Tipos de Fosa (7 tipos estándar)")

        # ── 6. FOSAS ──────────────────────────────────────────────────────
        fosas = [
            (1, 'Pit Activo #1',   200),
            (2, 'Pit Activo #2',   200),
            (3, 'Pit de Reserva',  250),
            (4, 'Pit Premix',      150),
        ]
        for num, desc, cap in fosas:
            Fosa.objects.get_or_create(
                pozo=p, numero=num,
                defaults={'descripcion': desc, 'capacidad': Decimal(str(cap))}
            )
        self.stdout.write("  ✓ Fosas (4 fosas)")

        # ── 7. ALMACENES ──────────────────────────────────────────────────
        almacenes = [
            ('ALM-01', 'Almacén Base – Anaco'),
            ('ALM-02', 'Almacén Taladro'),
            ('ALM-03', 'Almacén Patio'),
        ]
        for cod, nom in almacenes:
            AlmacenCodigo.objects.get_or_create(
                pozo=p, codigo=cod, defaults={'nombre': nom}
            )
        self.stdout.write("  ✓ Almacenes (3 almacenes)")

        # ── 8. DISTRIBUCIÓN DE TIEMPO ─────────────────────────────────────
        TipoDistribucionTiempo.sembrar_estandar(p)
        self.stdout.write("  ✓ Distribución de Tiempo (20 categorías estándar)")

        # ── 9. PRODUCTOS DEL CATÁLOGO MAESTRO + ACTIVOS EN EL POZO ────────
        productos_data = [
            ('GEL-TITAN',  'Gel Titan Premium (Bentonita)',    'SACOS',  'LBS',  100.0, 1.0,    25.0, 'SOLIDO',  1.0),
            ('BARITA-325', 'Barita 325 Malla',                 'SACOS',  'LBS',  200.0, 4.2,    18.0, 'SOLIDO',  4.2),
            ('KCL-GRADO',  'KCl Grado Industrial',             'SACOS',  'LBS',  150.0, 1.59,   22.0, 'SOLIDO',  1.59),
            ('LUBR-EZE',   'Lubricante EZE-GLIDE',             'TAMBOR', 'GAL',  55.0,  0.9,    85.0, 'LIQUIDO', 0.9),
            ('SODA-ASH',   'Carbonato de Sodio (Soda Ash)',    'SACOS',  'LBS',  80.0,  1.03,   12.0, 'SOLIDO',  1.03),
            ('CAUS-SODA',  'Hidróxido de Sodio (Caustic Soda)','SACOS',  'LBS',  60.0,  1.53,   9.50, 'SOLIDO',  1.53),
        ]
        for cod, desc, emp, uni, cant, grav, costo, cat, gs in productos_data:
            prod, _ = Producto.objects.get_or_create(
                codigo=cod,
                defaults=dict(
                    descripcion=desc, empaque=emp, unidad=uni,
                    cantidad=Decimal(str(cant)), gravedad=Decimal(str(grav)),
                    costo=Decimal(str(costo)), categoria=cat,
                )
            )
            ProductoActivoPozo.objects.get_or_create(
                pozo=p, producto=prod,
                defaults=dict(
                    abreviatura=cod, unidad=uni, empaque=emp,
                    precio=Decimal(str(costo)),
                    gravedad_especifica=Decimal(str(gs)),
                    calcular_concentracion=True,
                    es_producto_mi=True,
                )
            )
        self.stdout.write("  ✓ Productos / Equipos Activos (6 productos)")

        # ── 10. EQUIPOS ───────────────────────────────────────────────────
        equipos_data = [
            ('BEM-503',   'BEM 503 Shale Shaker',       'ZARANDA',    3),
            ('CENTRF-DEA','Decanter Centrifuge DEA-60',  'CENTRIFUGA', 0),
            ('MUDCLN-1',  'Mud Cleaner MC-1',            'LIMPIADOR_LODO', 0),
        ]
        for cod, nom, tipo, pos in equipos_data:
            eq, _ = Equipo.objects.get_or_create(
                codigo=cod,
                defaults={'nombre': nom, 'tipo_equipo': tipo, 'posiciones_malla': pos}
            )
            EquipoActivoPozo.objects.get_or_create(
                pozo=p, numero_serie=f'SN-{cod}',
                defaults={'equipo': eq, 'descripcion': nom}
            )
        self.stdout.write("  ✓ Equipos (3 equipos activos)")

        # ── 11. ESTACIONES DE SURVEY (Registro Direccional) ────────────────
        stations = [
            (1,  0.0,    0.0,  0.0,   0.0),
            (2,  500.0,  500.0, 1.2,  15.0),
            (3,  1800.0, 1800.0, 0.8, 20.0),
            (4,  4500.0, 4500.0, 0.5, 25.0),
            (5,  7200.0, 7200.0, 0.3, 28.0),
        ]
        for num, md, tvd, inc, azi in stations:
            WellSurveyStation.objects.get_or_create(
                pozo=p, md_ft=md,
                defaults=dict(
                    estacion=num,
                    tvd_ft=tvd,
                    inclinacion_deg=inc,
                    azimut_deg=azi,
                )
            )
        self.stdout.write("  ✓ Registro Direccional (5 estaciones de survey)")

        # ── RESUMEN ────────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"[seed] ¡Listo! Abre el pozo en: /operaciones/pozos/{p.pk}/"
        ))
