# Prueba 29 — Blindaje Integral contra Mutaciones en Pozos Cerrados

> **Documento de referencia:** [29](../29_CERRAR_Y_REABRIR_POZOS.md), [05](../05_CONFIGURACION_POZO.md), [16](../16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) y [00](../00_TRASPASO.md).  
> **Migración:** No requiere.

---

## Cómo funciona

Cuando un pozo es marcado con estado `CERRADO`, representa un pozo cuyas operaciones han concluido y cuyo historial, costos y recap deben quedar congelados e inmutables para fines de auditoría y reportes finales.

Para garantizar la integridad total de la base de datos:

1. **Banner visual unificado:**
   - La barra de navegación compartida de configuración del pozo (`operaciones/templates/operaciones/pozos/_nav_info_pozo.html`) despliega automáticamente un aviso de advertencia cuando `pozo.estado == 'CERRADO'`:
     > 🔒 **Pozo Cerrado — Solo lectura:** Este pozo está cerrado. Toda su información y configuración se encuentra en modo de consulta y protegida contra modificaciones. Para realizar cambios debes reabrir el pozo.
   - Esto protege visualmente las 8 pantallas de configuración del pozo sin duplicación de código.

2. **Blindaje de Backend en Configuración del Pozo (`views.py`):**
   - Todas las funciones de guardado (`POST`) validan el estado mediante `_validar_pozo_abierto(pozo)` y devuelven código HTTP 400 y mensaje en español si el pozo está cerrado:
     - `api_well_header_guardar` (Well Information)
     - `api_marketing_codes_guardar` (Marketing Codes)
     - `api_fosas_guardar` y `api_tipos_fosa_guardar` (Tanques / Pit Setup)
     - `api_categorias_perdida_guardar` (Loss Setup)
     - `api_general_setup_guardar` (General Setup)
     - `api_almacenes_guardar` (Warehouse Setup)
     - `api_tipos_distribucion_guardar` (Time Distribution Setup)
     - `api_productos_activos_guardar` (Active Products Setup)
     - `api_equipos_activos_guardar` (Active Equipment Setup)
     - `api_mallas_activas_guardar` (Active Screens Setup)
     - `api_equipment_properties_guardar` (Equipment Properties Setup)
     - `api_benchmark_definiciones_guardar` y `api_benchmark_targets_guardar` (Benchmark Setup)

3. **Blindaje de Backend en Reportes Diarios y Pestañas (`views_daily_reports.py`, `views_inventario.py`, `views_control_solidos.py`, `views_opcionales.py`):**
   - Se validan y rechazan con 400 las mutaciones en:
     - Creación y eliminación de reportes (`api_reporte_diario_crear`, `api_reporte_diario_eliminar`)
     - Pestaña 1: General (`api_reporte_diario_general_guardar`)
     - Pestaña 2: Survey y Litología (`api_well_survey_guardar`, `api_formation_tops_guardar`, `api_propiedades_extra_guardar`)
     - Pestaña 3: Bombas y Barrenas (`api_pumps_bits_guardar`)
     - Pestaña 4: Propiedades de Lodo (`api_mud_properties_guardar`, `api_reporte_propiedades_comentario`)
     - Pestaña 5: Geometría y Sarta (`api_well_geometry_guardar`)
     - Pestaña 6: Control de Sólidos y Rendimiento de Equipos (`api_transaccion_malla_crear`, `api_transaccion_malla_deshacer`, `api_ticket_malla_guardar`, `api_ticket_malla_eliminar`, `api_tipo_ticket_malla_guardar`, `api_tipo_ticket_malla_eliminar`, `api_uso_equipos_guardar`)
     - Pestaña 7: Distribución de Tiempo (`api_tiempo_guardar`)
     - Pestaña 8: Volumetría, Inventario y Servicios (`api_volumetria_guardar`, `api_volumetria_transaccion`, `api_volumetria_transaccion_editar`, `api_volumetria_transaccion_eliminar`, `api_volumetria_dejar_en_hoyo`, `api_volumetria_deshacer`, `api_ticket_producto_guardar`, `api_ticket_producto_eliminar`, `api_servicio_guardar`, `api_servicio_eliminar`, `api_perdidas_reporte_guardar`)
     - Módulos opcionales: Muestras y Eventos (`api_muestras_guardar`, `api_muestras_eliminar`, `api_eventos_guardar`, `api_eventos_eliminar`)

4. **Reapertura de Pozo:**
   - Si el usuario decide reabrir el pozo (`/api/pozos/<id>/reabrir/`), el pozo vuelve a estado `ACTIVO` y todas las operaciones de guardado y edición vuelven a quedar habilitadas con normalidad.

---

## Pasos para verificar

### 1. Banner visual en configuración
- [ ] Tomar un pozo y cerrarlo desde el Recap o la lista de pozos.
- [ ] Navegar a **Información del Pozo** (Well Header).
- [ ] Verificar que en la parte superior del menú secundario aparece el banner rojo indicando que el pozo está cerrado y en modo de consulta.
- [ ] Navegar por las pestañas: Tanques, Pérdidas, Configuración General, Catálogos del Pozo, Propiedades de Equipo, Benchmark.
- [ ] Verificar que el banner protector aparece de forma consistente en todas las 8 pantallas.

### 2. Intento de modificación vía API
- [ ] Con el pozo cerrado, intentar enviar un guardado (por consola de desarrollador o herramienta HTTP) a cualquier endpoint de configuración o reporte (ej. `/api/pozos/<id>/well-header/guardar/` o `/api/pozos/<id>/daily-report/<reporte_id>/general/guardar/`).
- [ ] Verificar que el servidor responde con status HTTP 400 y mensaje en español indicando que el pozo está cerrado y debe reabrirse.

### 3. Reapertura
- [ ] Reabrir el pozo pulsando **`Reabrir Pozo`**.
- [ ] Verificar que el banner rojo desaparece.
- [ ] Realizar una modificación normal en cualquier pestaña y verificar que se guarda con éxito (HTTP 200).

