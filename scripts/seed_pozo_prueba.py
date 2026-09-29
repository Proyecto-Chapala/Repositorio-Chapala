"""
seed_pozo_prueba.py
-------------------
Crea un Pozo de prueba en estado ACTIVO con todos los campos mínimos
necesarios para navegar la interfaz.

Uso:
    python manage.py shell < scripts/seed_pozo_prueba.py

Si ya existe un pozo con ese nombre, lo omite (no duplica).
"""

from decimal import Decimal
from datetime import date
from operaciones.models import Pozo

NOMBRE_POZO = "PRUEBA-001"

if Pozo.objects.filter(nombre=NOMBRE_POZO).exists():
    p = Pozo.objects.get(nombre=NOMBRE_POZO)
    print(f"[seed] Pozo '{NOMBRE_POZO}' ya existe (id={p.pk}). No se creó duplicado.")
else:
    p = Pozo.objects.create(
        nombre=NOMBRE_POZO,

        # --- Unidades ---
        sistema_unidades='STANDARD_OILFIELD',
        unidades_bloqueadas=True,

        # --- Financiero ---
        moneda_simbolo='USD',
        moneda_decimales=2,
        tasa_impuesto=Decimal('16.00'),

        # --- Sólidos / hidráulica ---
        ecuacion_solidos_base_agua='MI',
        ecuacion_solidos_base_aceite='MI',
        usar_api_5ta_edicion_hidraulica=False,
        categoria_perdida_tipo='MI',

        # --- Spud date ---
        fecha_primera_captura=date(2025, 9, 1),
        tipo_fluido_inicial='WATER_BASE',
        con_tratamiento_disposicion=False,
        numero_control_logit='LOG-PRUEBA-001',
        spud_date_completado=True,

        # --- Estado final: ACTIVO ---
        estado='ACTIVO',
        paso_wizard_actual=4,
    )
    print(f"[seed] Pozo '{NOMBRE_POZO}' creado exitosamente (id={p.pk}).")

print(f"[seed] URL del pozo: /operaciones/pozos/{p.pk}/")
