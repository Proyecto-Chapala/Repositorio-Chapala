# Decisiones confirmadas — Núcleo de datos (Pozo/Intervalo/ReporteDiario) y Misión 4

Continuación tras pérdida de contexto (modo incógnito). Estado al 2026-09-07. Este documento cubre el esquema ONE-TRAX completo (Pozo → Intervalo → SistemaFluido → ReporteDiario). Para los cambios sobre el inventario CHAPALA (`mychapala/`), ver `claude/decisiones_inventario_chapala.md`.

## Núcleo (Pozo/Intervalo/TuberiaInstalada/CierreVolumetrico/ReporteDiario)

- **TuberiaInstalada uno a muchos con Intervalo** — confirmado, sin cambios (un intervalo puede tener varios tramos: revestidor + liner).
- **numero_reporte correlativo por Pozo**, no por intervalo — confirmado, sin cambios.
- **SistemaFluido**: catálogo maestro editable (nombre + `categoria`: agua/polimerico/aceite/sintetico/otro). `Intervalo.sistema_fluido` es FK obligatoria, fija mientras el intervalo está abierto (se bloquea en el admin al cerrar). El tipo de fluido puede cambiar de un intervalo a otro del mismo pozo según el diseño de fluidos.
- **CierreVolumetrico.volumen_no_fluido**: el lodo atrapado bajo la profundidad de cierre, se clasifica siempre como "Left in Hole". El catálogo formal de categorías de pérdida (sección 7.4) queda pendiente para la Misión 5.
- **Producto**: ver `claude/decisiones_inventario_chapala.md` — esa separación de Unit Size se aplicó fue sobre CHAPALA, no sobre este esquema (aunque el `Producto` de este archivo también tiene `cantidad_unitaria`/`unidad_medida`/`tipo_empaque` por si este esquema ONE-TRAX se termina desplegando).
- **Fórmula de volumen confirmada** (pendiente de implementar en Misión 5): `Volumen = Libraje Final / (Gravedad Específica × 350)`.

## Misión 4 — Matriz de propiedades selectivas — ✅ COMPLETA Y SEMBRADA EN LA BASE REAL

Propuesta documentada en `claude/propuesta_mision4_propiedades.md` y confirmada por el usuario. Catálogo de 42 propiedades extraído de las hojas MUD PROPERTIES del Mud Report 16 PERLA-1X (WBM/CALDRIL Check = agua, OBM Check = aceite, Synthetic-Based Mud = sintético).

Decisiones confirmadas:

1. **Varias muestras por reporte** (no un solo valor por propiedad por día) — modelado fiel al mud report real (ej. "TK 2 20:00", "TK 2 12:00").
2. **Propiedades compuestas separadas en campos numéricos individuales** — R600/R300/R200/R100/R6/R3 y Pf/Mf se partieron en propiedades independientes del catálogo (r600, r300, r200, r100, r6, r3, pf, mf), no como texto libre.
3. **Categoría "polimérico" reutiliza el catálogo de "agua"** — no hay hoja de referencia separada para polímeros en el mud report base.

Modelos agregados a `models.py`:

- `PropiedadCatalogo` (codigo, nombre, unidad, orden) — catálogo maestro, 42 filas.
- `PropiedadSistema` (propiedad, categoria_sistema, obligatoria) — la matriz: qué propiedad aplica a qué categoría de SistemaFluido. 19 propiedades comunes a las 4 categorías, 12 exclusivas de agua/polimérico, 11 exclusivas de aceite/sintético.
- `MuestraFluido` (reporte, identificador, orden) — una muestra del día (ej. "TK 2 20:00"), bloqueada si el intervalo está cerrado.
- `PropiedadValor` (muestra, propiedad, valor Decimal) — el valor cargado; `clean()` valida que la propiedad esté habilitada para la categoría del sistema de fluido del intervalo del reporte, y que el intervalo no esté cerrado.

**Fuera de alcance de la Misión 4** (pertenece a Misión 5): los bloques "SOLIDS ANALYSIS" y "RHEOLOGY & HYDRAULICS" del mud report (Calcium Chloride, Brine Specific Gravity, ECD, Jet Velocity, etc.) — son cálculos de volumen/hidráulica, no propiedades del catálogo selectivo.

**Carga de datos (`seed_propiedades.py`) — ejecutada con éxito en la base real:**

- Resultado: `Propiedades: 42 nuevas de 42 totales.` / `Entradas de matriz (PropiedadSistema): 122 nuevas.`
- 122 cuadra exacto con el diseño: 19 comunes × 4 categorías (76) + 12 agua/polimérico × 2 (24) + 11 aceite/sintético × 2 (22) = 122.
- **Bug encontrado y corregido en el script**: `seed_propiedades.py` importaba `reportes.models` a nivel de módulo (línea 14), antes de que `django.setup()` se ejecutara (eso solo pasaba dentro de `if __name__ == "__main__":`, al final del archivo) → `ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured`. Se corrigió moviendo `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chapala.settings")` + `django.setup()` al principio del archivo, antes del import de los modelos. Archivo corregido entregado y escrito en el disco del usuario (`seed_propiedades.py`, raíz del proyecto).

## Misión 0 — App 'reportes' creada, dentro del proyecto CHAPALA existente — ✅ VERIFICADA

Decisión confirmada por el usuario: **'reportes' vive DENTRO del proyecto Django existente** (`Proyecto CHAPALA`, mismo `manage.py`, mismo PostgreSQL vía `.env`), como segunda app junto a `mychapala` — no un proyecto separado. Razón: ya había PostgreSQL configurado y funcionando, no tenía sentido duplicar credenciales/infraestructura.

Archivos ya escritos en el disco del usuario:

- `reportes/__init__.py`, `reportes/apps.py` (`ReportesConfig`), `reportes/models.py`, `reportes/admin.py`, `reportes/migrations/__init__.py` y `0001_initial.py` (generada por el usuario).
- `chapala/settings.py` — se agregó `'reportes.apps.ReportesConfig'` a `INSTALLED_APPS`, después de `mychapala`.
- `seed_propiedades.py` (raíz del proyecto, junto a `seed_data.py`) — ver bugfix arriba.

**Importante — lo que NO se pudo hacer desde aquí:** esta sesión no tiene acceso a PyPI/pip (el proxy de red bloquea `pypi.org` para esta cuenta), así que no se pudo instalar Django ni correr `makemigrations` en este entorno para generar la migración inicial. A diferencia de la migración 0004 de CHAPALA (que sí escribí a mano porque era pequeña y solo agregaba 3 campos), la migración inicial de `reportes` tiene 13 modelos interdependientes — es mucho más seguro que Django la autogenere contra el entorno real del usuario que escribirla a mano.

**Checklist de verificación — completado por el usuario:**

1. `python manage.py makemigrations reportes` — generó `0001_initial.py` con los 13 modelos.
2. `python manage.py migrate` — aplicó `reportes.0001_initial` sin errores contra PostgreSQL.
3. `python manage.py showmigrations reportes` — confirmó `[X] 0001_initial`.
4. **Verificación definitiva**: conteo de filas de los 13 modelos vía shell — todos consultables, en 0 filas (esperado en base recién migrada).
5. `python seed_propiedades.py` — cargó los 42 registros de `PropiedadCatalogo` y las 122 entradas de `PropiedadSistema` sin errores.

## Interfaz web del módulo 'reportes' — ✅ CREADA Y FUNCIONANDO

Como el usuario prefiere probar el resto directamente en Antigravity (su entorno local) y solo pidió una interfaz visual (no quedarse limitado al admin de Django), se construyó un frontend propio para `reportes`, en el mismo patrón vanilla-JS + API JSON que ya usa `mychapala` (para mantener consistencia y que el usuario no tenga que aprender un stack nuevo).

**No requirió migración nueva** — solo se agregaron métodos `to_dict()` a cada modelo de `reportes/models.py` (serialización, sin tocar campos).

Archivos nuevos:

- `reportes/views.py` — vistas de función + APIs JSON (mismo patrón `@csrf_exempt` + `@require_http_methods` + `JsonResponse({"success": ...})` que `mychapala/views.py`). Cubre: Pozos, Sistemas de Fluido, Intervalos (crear/editar/cerrar), Tubería Instalada, Cierre Volumétrico (`api/intervalos/<uuid:pk>/cerrar/` — delega la regla de auto-cierre al `save()` del modelo), Productos, Reportes Diarios, catálogo de Propiedades filtrado por categoría de sistema de fluido, Muestras de Fluido + guardado de valores de la matriz, Inventario y Uso de Material (con recálculo automático de `cantidad_final` al registrar/eliminar un uso).
- `reportes/urls.py` — montada bajo el prefijo `/reportes/` en `chapala/urls.py` (no choca con `mychapala`, que vive en `/`).
- `reportes/templates/reportes/index.html` + `reportes/static/reportes/css/style.css` + `reportes/static/reportes/js/app.js` — SPA con 5 pestañas: Pozos, Sistemas de Fluido, Intervalos (con tubería instalada y formulario de cierre volumétrico inline), Productos, Reportes Diarios (con muestras, matriz de propiedades selectivas dinámica según el sistema de fluido del intervalo, e inventario/uso de material).

**Deliberadamente fuera de esta interfaz** (según la estrategia acordada del proyecto): geometría interactiva del pozo (queda para el final) y módulos de Equipos/Comentarios (esos modelos todavía no existen en `models.py`).

Confirmado por el usuario: la interfaz carga y funciona en `http://127.0.0.1:8000/reportes/` (requirió reiniciar el servidor de desarrollo una vez, ya que se crearon carpetas nuevas de `templates/` y `static/` de una sola vez).

## Próximo paso pendiente

1. El usuario va a probar el flujo completo (Pozo → Sistema de Fluido → Intervalo → Tubería → Cierre Volumétrico → Reporte Diario → Muestras/Propiedades → Inventario/Uso) por su cuenta en Antigravity y reportará hallazgos.
2. Formalizar el detalle exacto del cierre volumétrico contra el manual de ONE-TRAX (sección 8 del contexto).
3. Misión 5: implementar `Volumen = Libraje Final / (Gravedad Específica × 350)` y el catálogo de categorías de pérdida.
4. Eventualmente: módulos de Equipos y Comentarios (aún no modelados), y la geometría interactiva del pozo (JS, para el final).
