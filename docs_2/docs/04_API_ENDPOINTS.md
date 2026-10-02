# 04 — API y rutas

> Tablas generadas **desde `operaciones/urls.py`** recorriendo el resolvedor de Django: los métodos HTTP salen de los decoradores `@require_http_methods` y la descripción, del docstring de cada vista. Fecha: 25-sep-2026.

## Convenciones

- **Prefijo**: todas las rutas cuelgan de la raíz (`chapala/urls.py` incluye `operaciones.urls` en `''`). El espacio de nombres es `operaciones:` y se usa en las plantillas como `{% url 'operaciones:pozo_main' pozo.pk %}`.
- **Páginas vs API**: las rutas que empiezan con `api/` devuelven JSON. Las demás devuelven HTML.
- **Parámetros de ruta**: `<pk>` = id del **pozo** (salvo en `api/productos/<pk>`, `api/equipos/<pk>` y demás catálogos, donde es el id del registro); `<reporte_pk>` = id del **reporte diario**.
- **Cuerpo de las escrituras**: JSON en el body (`Content-Type: application/json`).
- **Respuesta**: hay **dos convenciones**. Las APIs de `views.py` (inventario de almacén, wizard, setups del pozo y catálogos) responden `{"success": true, …}` o `{"success": false, "error": "…", "errores_filas": […]}`. Las del reporte diario (`views_daily_reports`, `views_control_solidos`, `views_inventario`, `views_hidraulica`, `views_opcionales`) responden `{"ok": true, …}` o `{"ok": false, "error": "…"}`. Los errores usan HTTP 400 o 404. Las APIs de las pestañas 6 y 8 devuelven, después de cada escritura, **el estado completo recalculado** de la pestaña, y la pantalla se redibuja con él.
- **CSRF**: las vistas de escritura están marcadas `@csrf_exempt` (⚠ aparecen en las tablas como *CSRF-exento*). El frontend igual envía `X-CSRFToken` con `getCookie('csrftoken')`. Ver [16 § Seguridad](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md#c-seguridad).
- **Autenticación**: ninguna vista exige inicio de sesión.
- **Métodos**: cuando una fila dice `PUT / POST` o `DELETE / POST`, el frontend usa `POST`. La excepción es `api_reporte_diario_eliminar`, que **solo** acepta `DELETE`.

## Ejemplos

Crear un reporte diario:

```http
POST /api/pozos/3/reportes-diarios/crear/
Content-Type: application/json

{ "fecha": "2026-09-24", "tipo_lodo": "WBM", "copy_data": true }
```
```json
{ "ok": true, "id": 41, "fecha": "2026-09-24" }
```

Registrar una transacción de mallas (pestaña 6):

```http
POST /api/pozos/3/daily-report/41/control-solidos/transaccion/
{ "accion": "INSTALAR_NUEVA", "serie": "ZAR-01", "posicion": 2, "malla_id": 7 }
```
Acciones válidas: `INSTALAR_NUEVA`, `INSTALAR_USADA`, `A_ALMACEN`, `DESECHAR_EQUIPO`, `DESECHAR_ALMACEN`.

Consultar la hidráulica con la 4ª edición:

```http
GET /api/pozos/3/daily-report/41/hidraulica/?edicion=4
```

Descargar el Excel del reporte: `GET /pozos/3/daily-report/41/excel/`

# Rutas por módulo

## Inventario de almacén (productos)

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/` | `views.index` | Renderiza la SPA principal de Operaciones. |
| GET | `/api/productos/` | `views.api_productos_list` | Lista los productos con filtros opcionales de categoría, estado y búsqueda. |
| POST ⚠CSRF-exento | `/api/productos/crear/` | `views.api_producto_create` | Crea un nuevo producto en el inventario con validaciones estrictas. |
| GET | `/api/productos/<int:pk>/` | `views.api_producto_detail` | Obtiene el detalle de un producto por su ID. |
| PUT / POST ⚠CSRF-exento | `/api/productos/<int:pk>/modificar/` | `views.api_producto_update` | Modifica un producto existente. |
| DELETE / POST ⚠CSRF-exento | `/api/productos/<int:pk>/eliminar/` | `views.api_producto_delete` | Elimina un producto siempre y cuando su cantidad disponible sea 0. |

## Pozos y wizard de creación

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/` | `views.pozos_list_view` | Vista temporal/placeholder para la lista de pozos en el sidebar. |
| GET (página HTML) | `/pozos/nuevo/` | `views.pozo_wizard_view` | Renderiza el shell del wizard (SPA) |
| GET (página HTML) | `/pozos/<int:pk>/continuar/` | `views.pozo_wizard_view` | Renderiza el shell del wizard (SPA) |
| GET | `/api/pozos/plantillas/` | `views.api_pozos_plantillas` | Lista de pozos ACTIVOS disponibles para usar como plantilla (paso 1). |
| GET | `/api/pozos/<int:pk>/` | `views.api_pozo_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/paso1/` | `views.api_pozo_paso1` | Crea el borrador (pk=None) o actualiza uno existente (pk dado) |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/paso1/` | `views.api_pozo_paso1` | Crea el borrador (pk=None) o actualiza uno existente (pk dado) |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/paso2/` | `views.api_pozo_paso2` | Guarda sistema de unidades |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/paso3/` | `views.api_pozo_paso3` | Guarda ajustes financieros + tipo de categoría de pérdida |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/confirmar/` | `views.api_pozo_confirmar` | Paso 4 — Confirma la creación: bloquea unidades y activa el pozo. |
| GET (página HTML) | `/pozos/<int:pk>/` | `views.pozo_main_view` | Pantalla principal del pozo (equivalente al 'Project Main Screen' de ONE-TRAX) |

## Spud Date

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/spud-date/` | `views.pozo_spud_date_view` | Renderiza la pantalla de Spud Date |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/spud-date/` | `views.api_pozo_spud_date` | Confirma la pantalla Spud Date |

## Información general del pozo (Well Header)

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/well-header/` | `views.well_header_view` |  |
| GET | `/api/pozos/<int:pk>/well-header/` | `views.api_well_header_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/well-header/guardar/` | `views.api_well_header_guardar` | Guarda la pestaña 1 (Well Information). |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/marketing-codes/guardar/` | `views.api_marketing_codes_guardar` | Guarda la pestaña 2 (Marketing Codes). |

## Intervalos de revestimiento

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/casing-intervals/` | `views.casing_intervals_view` |  |
| GET | `/api/pozos/<int:pk>/casing-intervals/` | `views.api_intervalos_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/casing-intervals/crear/` | `views.api_intervalo_crear` |  |
| POST / PUT ⚠CSRF-exento | `/api/pozos/<int:pk>/casing-intervals/<int:intervalo_pk>/` | `views.api_intervalo_actualizar` |  |
| POST / DELETE ⚠CSRF-exento | `/api/pozos/<int:pk>/casing-intervals/<int:intervalo_pk>/eliminar/` | `views.api_intervalo_eliminar` |  |

## Fosas y tipos de fosa

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/pits/` | `views.pits_view` |  |
| GET | `/api/pozos/<int:pk>/pits/` | `views.api_pits_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/pits/guardar/` | `views.api_fosas_guardar` | Reemplaza el listado completo de fosas del pozo (guardado en bloque, como la grilla de ONE-TRAX). |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/pit-types/guardar/` | `views.api_tipos_fosa_guardar` | Reemplaza el listado completo de Pit Type Setup del pozo. |

## Configuración de pérdidas

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/loss-setup/` | `views.loss_setup_view` |  |
| GET | `/api/pozos/<int:pk>/loss-setup/` | `views.api_categorias_perdida_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/loss-setup/guardar/` | `views.api_categorias_perdida_guardar` | Reemplaza el listado completo de categorías de pérdida del pozo. |

## Configuración general, almacenes y distribución de tiempo

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/general-setup/` | `views.general_setup_view` |  |
| GET | `/api/pozos/<int:pk>/general-setup/` | `views.api_general_setup_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/general-setup/guardar/` | `views.api_general_setup_guardar` |  |
| GET | `/api/pozos/<int:pk>/almacenes/` | `views.api_almacenes_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/almacenes/guardar/` | `views.api_almacenes_guardar` | Reemplaza el listado completo de códigos de almacén del pozo. |
| GET | `/api/pozos/<int:pk>/tipos-distribucion/` | `views.api_tipos_distribucion_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/tipos-distribucion/guardar/` | `views.api_tipos_distribucion_guardar` | Reemplaza el listado completo de Time Distribution Setup del pozo. |

## Productos / Equipos / Mallas activos del pozo

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/active-items/` | `views.active_items_view` | Pantalla de 3 pestañas: Productos Activos, Equipos Activos y Mallas Activas del pozo |
| GET | `/api/equipos/` | `views.api_equipos_list` | Master Equipment List — catálogo maestro global de equipos. |
| GET | `/api/mallas/` | `views.api_mallas_list` | Master Screen List — catálogo maestro global de mallas de zaranda. |
| GET | `/api/pozos/<int:pk>/productos-activos/` | `views.api_productos_activos_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/productos-activos/guardar/` | `views.api_productos_activos_guardar` | Reemplaza el listado completo de productos activos del pozo. |
| GET | `/api/pozos/<int:pk>/equipos-activos/` | `views.api_equipos_activos_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/equipos-activos/guardar/` | `views.api_equipos_activos_guardar` | Reemplaza el listado completo de equipos activos del pozo. |
| GET | `/api/pozos/<int:pk>/mallas-activas/` | `views.api_mallas_activas_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/mallas-activas/guardar/` | `views.api_mallas_activas_guardar` | Reemplaza el listado completo de mallas activas del pozo. |

## Catálogos maestros

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/catalogos-maestros/` | `views.catalogos_maestros_view` |  |
| POST ⚠CSRF-exento | `/api/equipos/crear/` | `views.api_equipo_create` |  |
| PUT / POST ⚠CSRF-exento | `/api/equipos/<int:pk>/modificar/` | `views.api_equipo_update` |  |
| DELETE / POST ⚠CSRF-exento | `/api/equipos/<int:pk>/eliminar/` | `views.api_equipo_delete` |  |
| POST ⚠CSRF-exento | `/api/mallas/crear/` | `views.api_malla_create` |  |
| PUT / POST ⚠CSRF-exento | `/api/mallas/<int:pk>/modificar/` | `views.api_malla_update` |  |
| DELETE / POST ⚠CSRF-exento | `/api/mallas/<int:pk>/eliminar/` | `views.api_malla_delete` |  |
| GET | `/api/propiedades-equipo/` | `views.api_propiedades_equipo_list` | Catálogo maestro global (editable) de propiedades por Tipo de Equipo. |
| POST ⚠CSRF-exento | `/api/propiedades-equipo/crear/` | `views.api_propiedad_equipo_create` |  |
| POST / PUT ⚠CSRF-exento | `/api/propiedades-equipo/<int:pk>/modificar/` | `views.api_propiedad_equipo_update` |  |
| DELETE / POST ⚠CSRF-exento | `/api/propiedades-equipo/<int:pk>/eliminar/` | `views.api_propiedad_equipo_delete` |  |
| GET | `/api/parametros-benchmark/` | `views.api_parametros_benchmark_list` | Catálogo maestro global (editable) de parámetros de Benchmark. |
| POST ⚠CSRF-exento | `/api/parametros-benchmark/crear/` | `views.api_parametro_benchmark_create` |  |
| POST / PUT ⚠CSRF-exento | `/api/parametros-benchmark/<int:pk>/modificar/` | `views.api_parametro_benchmark_update` |  |
| DELETE / POST ⚠CSRF-exento | `/api/parametros-benchmark/<int:pk>/eliminar/` | `views.api_parametro_benchmark_delete` |  |
| GET | `/api/componentes-sarta/` | `views.api_componentes_sarta_list` | Catálogo maestro global de componentes de sarta de perforación. |
| POST ⚠CSRF-exento | `/api/componentes-sarta/crear/` | `views.api_componente_sarta_create` |  |
| PUT / POST ⚠CSRF-exento | `/api/componentes-sarta/<int:pk>/modificar/` | `views.api_componente_sarta_update` |  |
| DELETE / POST ⚠CSRF-exento | `/api/componentes-sarta/<int:pk>/eliminar/` | `views.api_componente_sarta_delete` |  |

## Configuración de propiedades de equipo

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/equipment-properties-setup/` | `views.equipment_properties_setup_view` |  |
| GET | `/api/pozos/<int:pk>/equipment-properties-setup/` | `views.api_equipment_properties_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/equipment-properties-setup/guardar/` | `views.api_equipment_properties_guardar` |  |

## Configuración de benchmark

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/benchmark-setup/` | `views.benchmark_setup_view` |  |
| GET | `/api/pozos/<int:pk>/benchmark-setup/definiciones/` | `views.api_benchmark_definiciones_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/benchmark-setup/definiciones/guardar/` | `views.api_benchmark_definiciones_guardar` | Reemplaza el listado completo de parámetros de benchmark elegidos para el pozo. |
| GET | `/api/pozos/<int:pk>/benchmark-setup/targets/` | `views.api_benchmark_targets_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/benchmark-setup/targets/guardar/` | `views.api_benchmark_targets_guardar` | Reemplaza el listado completo de objetivos (Target Entry) del pozo. |

## Hub de fluidos y reportes diarios

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/pozos/<int:pk>/drilling-fluids-equipment/` | `views_daily_reports.daily_reports_hub_view` | Gateway principal para Drilling Fluids and Equipment (Historial y Setup). |
| GET (página HTML) | `/pozos/<int:pk>/daily-reports/` | `views_daily_reports.daily_reports_hub_view` | Gateway principal para Drilling Fluids and Equipment (Historial y Setup). |
| GET (página HTML) | `/pozos/<int:pk>/daily-report/<int:reporte_pk>/` | `views_daily_reports.reporte_diario_detalle_view` | Vista de 8 pestañas (Detalle del Reporte Diario). |
| GET | `/api/pozos/<int:pk>/reportes-diarios/` | `views_daily_reports.api_reportes_diarios_list` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/reportes-diarios/crear/` | `views_daily_reports.api_reporte_diario_crear` |  |
| DELETE ⚠CSRF-exento | `/api/pozos/<int:pk>/reportes-diarios/<int:reporte_pk>/eliminar/` | `views_daily_reports.api_reporte_diario_eliminar` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/reportes-diarios/<int:reporte_pk>/general/guardar/` | `views_daily_reports.api_reporte_diario_general_guardar` |  |
| GET (página HTML) | `/pozos/<int:pk>/daily-report/<int:reporte_pk>/excel/` | `views_daily_reports.reporte_diario_excel_view` | Descarga el reporte diario en Excel con el formato del libro de ONE-TRAX (en español): reporte de lodo, propiedades extra, contabilidad de volumen, inventario químico, equipos y ma |
| GET | `/api/pozos/<int:pk>/survey-stations/` | `views_daily_reports.api_well_survey_list` | Devuelve las estaciones de survey registradas para el pozo. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/survey-stations/guardar/` | `views_daily_reports.api_well_survey_guardar` | Guarda y recalcula todas las estaciones direccionales del pozo. |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/cost-overview/` | `views_daily_reports.api_cost_overview_detail` | Devuelve el balance detallado de costos para el modal de Cost Overview. |
| GET | `/api/pozos/<int:pk>/propiedades-extra/` | `views_daily_reports.api_propiedades_extra_list` | Devuelve las propiedades extra configuradas para el pozo en formato de diccionario clave-valor. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/propiedades-extra/guardar/` | `views_daily_reports.api_propiedades_extra_guardar` | Guarda/actualiza todas las propiedades extra del pozo de una sola vez. |
| GET | `/api/pozos/<int:pk>/formation-tops/` | `views_daily_reports.api_formation_tops_list` | Devuelve los topes de formación y litología configurados para el pozo. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/formation-tops/guardar/` | `views_daily_reports.api_formation_tops_guardar` | Guarda/reemplaza la lista completa de topes de formación para el pozo. |

## Pestaña 1 y 2 — General, Bombas y Barrena

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/pumps-bits/` | `views_daily_reports.api_pumps_bits_detail` | Devuelve los datos completos de bombas, barrena, boquillas y parámetros de Tab 2. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/pumps-bits/guardar/` | `views_daily_reports.api_pumps_bits_guardar` | Guarda todos los cambios de bombas, boquillas y barrena del reporte diario. |

## Pestaña 3 — Propiedades del lodo

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/mud-properties/` | `views_daily_reports.api_mud_properties_detail` | Devuelve la configuración y los 4 chequeos de lodo del reporte diario. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/mud-properties/guardar/` | `views_daily_reports.api_mud_properties_guardar` | Guarda los cambios en configuración, chequeos y propiedades extra de lodo. |

## Pestaña 4 — Geometría del pozo

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/well-geometry/` | `views_daily_reports.api_well_geometry_detail` | Devuelve la sarta, el contexto del pozo y los volúmenes calculados del Tab 4. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/well-geometry/guardar/` | `views_daily_reports.api_well_geometry_guardar` | Guarda la sarta del día (reemplazo total), el intervalo de costo y el hoyo piloto. |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/well-geometry/sarta-anterior/` | `views_daily_reports.api_sarta_reporte_anterior` | Devuelve la sarta del reporte anterior, para heredarla al reporte del día. |

## Pestaña 5 — Comentarios

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/comentarios/` | `views_daily_reports.api_comentarios_detail` | Devuelve los comentarios del día y el resumen del reporte anterior como referencia. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/comentarios/guardar/` | `views_daily_reports.api_comentarios_guardar` | Guarda la especificación de lodo y los tres bloques de comentarios del día. |

## Pestaña 6 — Control de sólidos

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/` | `views_control_solidos.api_control_solidos_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/transaccion/` | `views_control_solidos.api_transaccion_malla_crear` | Registra un movimiento de malla: instalar, pasar al almacén o desechar. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/transaccion/deshacer/` | `views_control_solidos.api_transaccion_malla_deshacer` | Deshace la última transacción del pozo, solo si pertenece a este reporte. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/ticket/guardar/` | `views_control_solidos.api_ticket_malla_guardar` | Crea o actualiza un ticket con sus cantidades por malla. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/ticket/<int:ticket_pk>/eliminar/` | `views_control_solidos.api_ticket_malla_eliminar` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/tipo-ticket/guardar/` | `views_control_solidos.api_tipo_ticket_malla_guardar` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/tipo-ticket/<int:tipo_pk>/eliminar/` | `views_control_solidos.api_tipo_ticket_malla_eliminar` |  |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/equipos/` | `views_control_solidos.api_uso_equipos_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/control-solidos/equipos/guardar/` | `views_control_solidos.api_uso_equipos_guardar` | Guarda el rendimiento, los costos y las paradas del día de todos los equipos. |

## Pestaña 7 — Distribución de tiempo

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/tiempo/` | `views_daily_reports.api_tiempo_detail` | Devuelve la distribución de tiempo del día y el catálogo de actividades del pozo. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/tiempo/guardar/` | `views_daily_reports.api_tiempo_guardar` | Guarda las horas del período y las actividades del día |

## Pestaña 8 — Volumetría, inventario, pérdidas e hidráulica

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET | `/api/pozos/<int:pk>/perdidas-reporte/` | `views_inventario.api_perdidas_reporte_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/perdidas-reporte/guardar/` | `views_inventario.api_perdidas_reporte_guardar` |  |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/volumetria/` | `views_inventario.api_volumetria_detail` |  |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/hidraulica/` | `views_hidraulica.api_hidraulica_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/volumetria/guardar/` | `views_inventario.api_volumetria_guardar` | Guarda lo que se mide o se escribe a mano: tipo y volumen real de fosas, hoyo e inventario. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/volumetria/transaccion/` | `views_inventario.api_volumetria_transaccion` | Registra un movimiento: químicos, lodo entero, transferencia, devolución o pérdida. |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/volumetria/transaccion/deshacer/` | `views_inventario.api_volumetria_deshacer` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/volumetria/ticket/guardar/` | `views_inventario.api_ticket_producto_guardar` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/volumetria/ticket/<int:ticket_pk>/eliminar/` | `views_inventario.api_ticket_producto_eliminar` |  |

## Módulos opcionales y evaluación de benchmark

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET / POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/ife/` | `views_opcionales.api_ife` |  |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/muestras/<str:clave>/` | `views_opcionales.api_muestras_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/muestras/<str:clave>/guardar/` | `views_opcionales.api_muestras_guardar` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/muestras/<str:clave>/<int:muestra_pk>/eliminar/` | `views_opcionales.api_muestras_eliminar` |  |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/eventos/` | `views_opcionales.api_eventos_detail` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/eventos/guardar/` | `views_opcionales.api_eventos_guardar` |  |
| POST ⚠CSRF-exento | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/eventos/<int:evento_pk>/eliminar/` | `views_opcionales.api_eventos_eliminar` |  |
| GET | `/api/pozos/<int:pk>/daily-report/<int:reporte_pk>/benchmark/` | `views_opcionales.api_benchmark_evaluacion` |  |

## Administración de Django

| Método | Ruta | Vista | Descripción |
|---|---|---|---|
| GET (página HTML) | `/admin/` | `sites.index` | Display the main admin index page, which lists all of the installed apps that have been registered in this site. |