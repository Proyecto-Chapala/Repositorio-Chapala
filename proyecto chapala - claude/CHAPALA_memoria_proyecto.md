# Contexto del Proyecto: CHAPALA (sistema tipo ONE-TRAX en Django)

**Objetivo general:** Sistema de operaciones de perforación petrolera basado en
la estructura de ONE-TRAX (MI SWACO), desarrollado en Django, **100% en
español**, con UX moderna que minimice clicks respecto al software original
(multi-ventana, Windows Forms).

**App Django existente:** `operaciones` (dentro del proyecto). Ya tenía
construido un CRUD de `Producto` (inventario de químicos: código,
descripción, unidad, libraje, gravedad, costo, cantidad, categoría
SOLIDO/LIQUIDO, estado ALTO/MEDIO/BAJO calculado automáticamente).
Arquitectura: vistas basadas en función + `JsonResponse` (API JSON),
frontend vanilla JS (SPA simple, sin framework), CSS modular por archivo
(no inline).

**Estructura de carpetas real:**

```
operaciones/
├── migrations/
├── static/operaciones/
│   ├── css/ (variables.css, layout.css, styles.css, inventario.css, pozos.css ←nuevo)
│   └── js/ (app.js, inventario.js, pozos.js ←nuevo, spud_date.js ←nuevo)
├── templates/operaciones/
│   ├── componentes/ (sidebar.html, etc.)
│   ├── inventario/
│   ├── pozos/ ←nuevo (wizard.html, _stepper.html, _paso1-4_*.html, spud_date.html)
│   ├── base.html, index.html
├── admin.py, apps.py, models.py, urls.py, views.py
```

---

## Jerarquía funcional acordada

(basada ÚNICAMENTE en las capturas de ONE-TRAX compartidas — todo lo demás
se descarta si aparece)

```
Pozo (Well)
├── [Wizard de creación — 4 pasos]
├── Spud Date (pantalla única, primera vez que se abre el pozo ya activo)
├── Well Information (11 sub-pantallas de configuración única — AÚN NO CONSTRUIDAS):
│    Well Header Information, Loss Setup, Well Casing Intervals (Cost),
│    Active Products/Equipment/Screens, Well Survey, Benchmark Setup,
│    Pit Information, Equipment Properties Setup, General Setup,
│    Unscheduled Events, Cost Overview
└── ONE-TRAX Modules (captura diaria — AÚN NO CONSTRUIDOS):
     ├── Drilling Fluids and Equipment → 8 pestañas (Mud Report diario):
     │     1-General, 2-Bombas/Brocas, 3-Propiedades del Lodo,
     │     4-Geometría del Pozo (sub: Well Casing Interval, Daily Casing Volume),
     │     5-Comentarios,
     │     6-Equipo de Sólidos (sub: Inventario de Mallas, Transacciones,
     │         Análisis de Sólidos, Retención de Recortes, Detalle/Uso)
     │         — SE MANTIENE COMPLETO, no descartar nada, aunque no es lo
     │         mismo que el inventario de Producto (son mallas/equipo
     │         físico, no químicos)
     │     7-Distribución de Tiempo,
     │     8-Inventario/Hidráulica/Concentración (sub: Selección Impresión
     │         Pérdidas, Benchmark Evaluation, Concentración de Producto,
     │         Resultados Hidráulicos, Contabilidad de Volumen e Inventario)
     ├── RDF Module
     ├── Completion Fluids
     └── Waste Treatment and Disposal
```

**Importante:** las 8 pestañas del reporte diario NO son independientes —
consumen datos configurados una sola vez en "Well Information" (dropdowns,
cálculos). Ver Well Header Information como ejemplo ya analizado (2 tabs:
Well Information + Marketing Codes, con validaciones: Offshore obligatorio
si aplica, Marketing Codes obligatorio antes de subir a ONE-TRAX Central).

**Pendiente de definir con más capturas:** el detalle de las 11
sub-pantallas de Well Information, y las 8 secciones del módulo diario.
**La volumetría del pozo es la parte más compleja** (repartida entre
sección 4, 6 y 8) — se deja para el final, cuando se compartan más
capturas específicas.

---

## Wizard "Nuevo Pozo" — 4 pasos con "Guardar y Continuar" (stepper visible)

Decisión de diseño (Opción B, confirmada): **siempre 4 pasos fijos**, sin
importar las elecciones del usuario (evita que el contador de progreso sea
inconsistente):

1. **Datos Básicos** — nombre del pozo (único, obligatorio) + toggle "usar
   pozo anterior como plantilla" (clona configuración si se activa).
2. **Sistema de Unidades** — 10 presets en tarjetas (Standard Oilfield,
   Standard 1/2/3, SI Metric, Metric 1-5) + acordeón "Personalizado" que
   despliega 16 propiedades con su unidad (Profundidad, Volumen, Caudal,
   etc.). **Inmutable tras crear el pozo.**
3. **Financiero** — moneda (símbolo + decimales, editable siempre — SE
   CONFIRMÓ que NO se bloquea, a diferencia de ONE-TRAX original), tasa de
   impuesto (editable después), ecuaciones de sólidos M-I/API (agua y
   aceite/sintético por separado), + acordeón "Categorías de Pérdida"
   (M-I/UK/Hydro/Statoil/IFE/Completion Fluids/Personalizado — las listas
   predefinidas completas se cargan luego como fixtures/datos semilla, aún
   no se tienen).
4. **Resumen y Confirmación** — solo lectura de todo lo anterior + botón
   "Crear Pozo" (llama a `pozo.activar()`).

**Regla de negocio clave:** el `Pozo` se guarda en estado `BORRADOR` desde
el paso 1 (autoguardado real en cada "Guardar y Continuar", no solo en
sesión), permite retomar el wizard si se cierra el navegador
(`paso_wizard_actual` trackea el progreso), y solo pasa a `ACTIVO` al
confirmar el paso 4, momento en que `unidades_bloqueadas=True`.
**Validación agregada:** no se puede activar si `paso_wizard_actual < 4`.

**Decisión de datos:** todas las unidades/categorías personalizadas van en
**tablas relacionales auditables** (no JSON), para poder auditar cada valor
como fila individual.

---

## Modelos construidos (`models.py` — YA CODEADOS, faltan migraciones)

- **`Pozo`**: nombre (único), pozo_plantilla (FK self), sistema_unidades,
  unidades_bloqueadas, moneda_simbolo, moneda_decimales, tasa_impuesto,
  ecuacion_solidos_base_agua/aceite, categoria_perdida_tipo,
  fecha_primera_captura, tipo_fluido_inicial, con_tratamiento_disposicion,
  numero_control_logit, spud_date_completado, estado
  (BORRADOR/ACTIVO/CERRADO), paso_wizard_actual, creado_por, timestamps.
  Métodos: `clonar_configuracion_desde_plantilla()`,
  `clonar_categorias_perdida()`, `clonar_unidades_personalizadas()`,
  `activar()`.
- **`PropiedadUnidadPozo`**: FK pozo, propiedad (16 choices), unidad (con
  `OPCIONES_UNIDAD` dict de validación por propiedad),
  `unique_together(pozo, propiedad)`.
- **`CategoriaPerdidaItem`**: FK pozo, codigo, descripcion, tipo
  (SUPERFICIE/SUBSUELO), `unique_together(pozo, codigo)`.

**Ya construidos también:** `admin.py` (con inlines), `forms_pozo.py`
(`PozoPaso1Form`, `PozoPaso2Form`, `PropiedadUnidadPozoForm`,
`PozoPaso3Form`, `CategoriaPerdidaItemForm`, `PozoSpudDateForm`),
`views_pozo.py` (vista shell + API por paso + `pozo_to_dict()` + Spud
Date), `urls_pozo.py`.

**Frontend construido:** `wizard.html` + 4 partials de paso +
`_stepper.html`, `pozos.css`, `pozos.js` (con repoblado completo de
borrador al retomar vía `/pozos/<id>/continuar/`), `spud_date.html` (modo
formulario / modo solo-lectura server-side), `spud_date.js`.

---

## Pendiente inmediato

1. Correr migraciones y probar el wizard end-to-end.
2. Reemplazar el link temporal del sidebar y el botón "Continuar" de Spud
   Date (hoy apunta al índice de Inventario como placeholder).
3. Construir el "Project Main Screen" (Well Information + Módulos
   ONE-TRAX) — el pozo activo aún no tiene una pantalla propia a la que
   aterrizar.
4. Luego, ir sección por sección: primero cerrar Well Information (11
   sub-pantallas), después las 8 pestañas del módulo diario.

---

## Mockup visual de referencia

<https://claude.ai/artifact/FxHiadffRezkT6VNuuT9vF>

(Nota: este mockup refleja una versión temprana de la navegación — el
sidebar ya no debe listar las 8 secciones directamente; esas viven como
pestañas dentro de un pozo abierto, no como ítems del menú lateral.)
