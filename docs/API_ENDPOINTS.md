# API y rutas

Todas las rutas están en `operaciones/urls.py` (namespace `operaciones`). El proyecto las monta en la raíz (`chapala/urls.py`: `path('', include('operaciones.urls'))`).

## Convenciones

- **Cuerpo**: JSON (`Content-Type: application/json`).
- **Respuesta**: JSON. Dos formatos, según la época en que se escribió cada módulo:
  - Inventario, wizard y configuración del pozo: `{"success": true, "mensaje": "...", ...}` o `{"success": false, "error": "...", "errores": {...}}`.
  - Reporte diario (pestañas): `{"ok": true, "mensaje": "...", ...}` o `{"ok": false, "error": "..."}`.
- **Errores de validación**: HTTP 400 con un mensaje en español listo para mostrar.
- **CSRF**: las APIs de escritura llevan `@csrf_exempt`; las vistas HTML del reporte ponen la cookie con `@ensure_csrf_cookie`.
- **Guardado de listas**: los endpoints `.../guardar/` de grillas **reemplazan la lista completa** (se envían todas las filas, no solo las que cambiaron).
- **Parámetros de ruta**: `<pk>` = id del pozo; `<reporte_pk>` = id del reporte diario.

---

## 1. Inventario de productos

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/` | Pantalla de inventario |
| GET | `/api/productos/` | Lista productos. Filtros por query string: `categoria` (`SOLIDO`/`LIQUIDO`), `estado` (`ALTO`/`MEDIO`/`BAJO`), `search` (código, descripción o unidad) |
| GET | `/api/productos/<pk>/` | Detalle |
| POST | `/api/productos/crear/` | Crea |
| PUT o POST | `/api/productos/<pk>/modificar/` | Modifica |
| DELETE o POST | `/api/productos/<pk>/eliminar/` | Elimina (solo si `cantidad = 0`) |

Cuerpo para crear o modificar:

```json
{
  "codigo": "AOS-1002",
  "descripcion": "ACETATO DE POTASIO (SACOS DE 25 KG)",
  "unidad": "SACOS 55 LBS",
  "libraje": 55,
  "gravedad": 1.57,
  "costo": 0,
  "cantidad": 120,
  "categoria": "SOLIDO",
  "observacion": ""
}
```

Respuesta de la lista:

```json
{"success": true, "productos": [ {...Producto.to_dict()} ], "totales": {"total": 38, "solidos": 30, "liquidos": 8}}
```

`Producto.to_dict()` devuelve además `estado`, `estado_display`, `categoria_display` y `puede_eliminar` (true solo con cantidad 0). El `estado` lo calcula el servidor; ver [inventario/FLUJOS.md](inventario/FLUJOS.md).

---

## 2. Pozos: lista, wizard y Spud Date

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/pozos/` | Lista de pozos (tarjetas) |
| GET | `/pozos/nuevo/` | Wizard nuevo |
| GET | `/pozos/<pk>/continuar/` | Retoma un pozo en BORRADOR |
| GET | `/api/pozos/plantillas/` | Pozos ACTIVOS que se pueden usar como plantilla |
| GET | `/api/pozos/<pk>/` | Datos del pozo |
| POST | `/api/pozos/paso1/` | Paso 1: crea el borrador |
| POST | `/api/pozos/<pk>/paso1/` | Paso 1: actualiza el borrador |
| POST | `/api/pozos/<pk>/paso2/` | Paso 2: sistema de unidades |
| POST | `/api/pozos/<pk>/paso3/` | Paso 3: moneda, impuesto, ecuaciones de sólidos, categorías de pérdida |
| POST | `/api/pozos/<pk>/confirmar/` | Paso 4: activa el pozo y bloquea las unidades |
| GET | `/pozos/<pk>/spud-date/` | Pantalla Spud Date |
| POST | `/api/pozos/<pk>/spud-date/` | Confirma Spud Date (una sola vez) |
| GET | `/pozos/<pk>/` | Pantalla principal del pozo (redirige al wizard si está en BORRADOR, a Spud Date si falta) |

Cuerpos:

```json
// paso1
{"nombre": "PERLA-1X", "pozo_plantilla_id": null}

// paso2
{"sistema_unidades": "STANDARD_OILFIELD"}
{"sistema_unidades": "CUSTOM", "unidades_personalizadas": [{"propiedad": "PROFUNDIDAD", "unidad": "m"}]}

// paso3
{"moneda_simbolo": "USD", "moneda_decimales": 2, "tasa_impuesto": 16,
 "ecuacion_solidos_base_agua": "MI", "ecuacion_solidos_base_aceite": "MI",
 "categoria_perdida_tipo": "MI",
 "categorias_perdida": [{"codigo": 1, "descripcion": "Zarandas", "tipo": "SUPERFICIE"}]}   // solo si CUSTOM

// spud-date
{"fecha_primera_captura": "2026-09-01", "tipo_fluido_inicial": "OIL_BASE",
 "con_tratamiento_disposicion": false, "numero_control_logit": ""}
```

Detalle de cada paso en [reportes/WIZARD_POZO.md](reportes/WIZARD_POZO.md).

---

## 3. Configuración del pozo

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/pozos/<pk>/well-header/` | Pantalla Información General del Pozo |
| GET | `/api/pozos/<pk>/well-header/` | Datos |
| POST | `/api/pozos/<pk>/well-header/guardar/` | Guarda pestaña "Well Information" (todos los campos de `WellHeaderInfo` salvo códigos de mercadeo) |
| POST | `/api/pozos/<pk>/marketing-codes/guardar/` | Guarda pestaña "Marketing Codes" |
| GET | `/pozos/<pk>/casing-intervals/` | Pantalla Intervalos de Revestimiento |
| GET | `/api/pozos/<pk>/casing-intervals/` | Lista |
| POST | `/api/pozos/<pk>/casing-intervals/crear/` | Crea (si no se envía `numero_intervalo`, toma el siguiente) |
| POST o PUT | `/api/pozos/<pk>/casing-intervals/<intervalo_pk>/` | Actualiza |
| POST o DELETE | `/api/pozos/<pk>/casing-intervals/<intervalo_pk>/eliminar/` | Elimina |
| GET | `/pozos/<pk>/pits/` | Pantalla Información de Fosas |
| GET | `/api/pozos/<pk>/pits/` | Fosas y tipos de fosa |
| POST | `/api/pozos/<pk>/pits/guardar/` | Reemplaza fosas: `{"fosas": [{"numero", "descripcion", "capacidad"}]}` |
| POST | `/api/pozos/<pk>/pit-types/guardar/` | Reemplaza tipos: `{"tipos_fosa": [{"codigo", "descripcion"}]}` |
| GET | `/pozos/<pk>/loss-setup/` | Pantalla Configuración de Pérdidas |
| GET | `/api/pozos/<pk>/loss-setup/` | Lista |
| POST | `/api/pozos/<pk>/loss-setup/guardar/` | Reemplaza: `{"categorias": [{"codigo", "descripcion", "tipo"}]}` |
| GET | `/pozos/<pk>/general-setup/` | Pantalla Configuración General |
| GET | `/api/pozos/<pk>/general-setup/` | Datos |
| POST | `/api/pozos/<pk>/general-setup/guardar/` | `tasa_impuesto`, `con_tratamiento_disposicion`, `usar_api_5ta_edicion_hidraulica`, `ecuacion_solidos_base_agua`, `ecuacion_solidos_base_aceite` |
| GET / POST | `/api/pozos/<pk>/almacenes/` y `.../guardar/` | Reemplaza: `{"almacenes": [{"codigo", "nombre"}]}` |
| GET / POST | `/api/pozos/<pk>/tipos-distribucion/` y `.../guardar/` | Reemplaza: `{"tipos_distribucion": [{"numero", "descripcion", "tipo"}]}` |
| GET | `/pozos/<pk>/active-items/` | Pantalla Productos / Equipos / Mallas Activos |
| GET / POST | `/api/pozos/<pk>/productos-activos/` y `.../guardar/` | Reemplaza: `{"productos_activos": [{"producto_id", "abreviatura", "unit_size", "unidad", "empaque", "precio", "gravedad_especifica", "calcular_concentracion", "es_producto_mi", "grupo_producto", "codigo_costo_diario", "calcular_wmgt_conc", "categoria_costo_wmgt", "categoria_costo_cf"}]}` |
| GET / POST | `/api/pozos/<pk>/equipos-activos/` y `.../guardar/` | Reemplaza: `{"equipos_activos": [{"equipo_id", "numero_serie", "descripcion", "precio_renta", "precio_standby"}]}` |
| GET / POST | `/api/pozos/<pk>/mallas-activas/` y `.../guardar/` | Reemplaza: `{"mallas_activas": [{"malla_id", "precio", "descuento_porcentaje"}]}` |
| GET | `/pozos/<pk>/equipment-properties-setup/` | Pantalla Propiedades de Equipo |
| GET / POST | `/api/pozos/<pk>/equipment-properties-setup/` y `.../guardar/` | `{"propiedades_seleccionadas": [{"propiedad_id", "tipo_equipo"}], "extras": [{"tipo_equipo", "descripcion", "unidad"}], "centrifuga_config": {"unidad_flow_rate", "unidad_mass"}}` |
| GET | `/pozos/<pk>/benchmark-setup/` | Pantalla Benchmark |
| GET / POST | `/api/pozos/<pk>/benchmark-setup/definiciones/` y `.../guardar/` | `{"parametro_ids": [1, 2, 3]}` |
| GET / POST | `/api/pozos/<pk>/benchmark-setup/targets/` y `.../guardar/` | `{"targets": [{"parametro_id", "intervalo_id" (null = pozo completo), "min_max" ("VALOR"/"MIN"/"MAX"), "valor"}]}` |

---

## 4. Catálogos maestros (globales, no dependen del pozo)

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/catalogos-maestros/` | Pantalla con 5 pestañas |
| GET | `/api/equipos/` | Lista equipos |
| POST | `/api/equipos/crear/` | `{"codigo", "nombre", "tipo_equipo", "posiciones_malla"}` (0 a 12) |
| PUT o POST | `/api/equipos/<pk>/modificar/` | Modifica |
| DELETE o POST | `/api/equipos/<pk>/eliminar/` | Elimina (falla si algún pozo lo usa: `PROTECT`) |
| GET | `/api/mallas/` | Lista mallas |
| POST | `/api/mallas/crear/` | `{"codigo", "descripcion", "mesh_size"}` |
| PUT o POST / DELETE o POST | `/api/mallas/<pk>/modificar/`, `/eliminar/` | Modifica / elimina |
| GET | `/api/propiedades-equipo/` | Lista propiedades por tipo de equipo |
| POST | `/api/propiedades-equipo/crear/` | `{"tipo_equipo", "descripcion", "unidad", "orden"}` |
| POST o PUT / DELETE o POST | `/api/propiedades-equipo/<pk>/modificar/`, `/eliminar/` | |
| GET | `/api/parametros-benchmark/` | Lista parámetros |
| POST | `/api/parametros-benchmark/crear/` | `{"grupo", "descripcion", "unidad", "tipo_fluido", "tipo_dato"}` |
| POST o PUT / DELETE o POST | `/api/parametros-benchmark/<pk>/modificar/`, `/eliminar/` | |
| GET | `/api/componentes-sarta/` | Lista componentes |
| POST | `/api/componentes-sarta/crear/` | `{"codigo", "descripcion", "tipo", "od_in", "id_in", "tool_joint_od_in", "tool_joint_id_in", "tool_joint_length_in", "largo_tramo_ft"}` |
| PUT o POST / DELETE o POST | `/api/componentes-sarta/<pk>/modificar/`, `/eliminar/` | |

---

## 5. Reportes diarios: hub, creación y datos del pozo

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/pozos/<pk>/drilling-fluids-equipment/` | Hub "Fluidos de Perforación y Equipos" (historial) |
| GET | `/pozos/<pk>/daily-reports/` | Alias del hub |
| GET | `/pozos/<pk>/daily-report/<reporte_pk>/` | Reporte diario, 8 pestañas |
| GET | `/pozos/<pk>/daily-report/<reporte_pk>/excel/` | Descarga el Excel del reporte |
| GET | `/api/pozos/<pk>/reportes-diarios/` | Lista de reportes + sugerencia de fecha y tipo de lodo |
| POST | `/api/pozos/<pk>/reportes-diarios/crear/` | `{"fecha": "2026-09-23", "tipo_lodo": "OBM", "copy_data": true}` |
| **DELETE** | `/api/pozos/<pk>/reportes-diarios/<reporte_pk>/eliminar/` | Borra el reporte y todo lo que cuelga de él |
| POST | `/api/pozos/<pk>/reportes-diarios/<reporte_pk>/general/guardar/` | Pestaña 1 |
| GET | `/api/pozos/<pk>/daily-report/<reporte_pk>/cost-overview/` | Resumen de costos (diario y acumulado) |
| GET / POST | `/api/pozos/<pk>/survey-stations/` y `.../guardar/` | Registro direccional: `{"estaciones": [{"md_ft", "inclinacion_deg", "azimut_deg", "comentarios"}]}`. El servidor recalcula TVD, DLS y sección vertical |
| GET / POST | `/api/pozos/<pk>/formation-tops/` y `.../guardar/` | `{"formation_tops": [{"depth_ft", "formation_top", "lithology", "porcentaje_arena"}]}` |
| GET / POST | `/api/pozos/<pk>/propiedades-extra/` y `.../guardar/` | Etiquetas extra: `{"items": [{"tipo_fluido": "WBM", "numero": 1, "etiqueta", "unidad"}]}` (etiqueta y unidad vacías = borrar) |

Tipos de lodo del reporte: `WBM`, `WBM_CACL2`, `OBM`, `SBM`.

---

## 6. Pestañas del reporte diario

Todas cuelgan de `/api/pozos/<pk>/daily-report/<reporte_pk>/`.

### Pestaña 1 — General

`POST /api/pozos/<pk>/reportes-diarios/<reporte_pk>/general/guardar/`

```json
{"fecha": "2026-09-23", "profundidad_actual": 7023, "profundidad_tvd": 6980, "bit_depth": 7023,
 "actividad_actual": "Perforando", "tipo_fluido_display": "VERSACLEAN", "litologia": "Lutita",
 "operador_representante": "", "contratista_representante": "", "mi_representante_1": "",
 "mi_representante_2": "", "telefono_taladro": "", "telefono_almacen": "", "telefonos": "", "fax_numbers": ""}
```

### Pestaña 2 — Bombas y mecha

| Método | Ruta |
|---|---|
| GET | `pumps-bits/` |
| POST | `pumps-bits/guardar/` |

```json
{"bombas": [{"numero_bomba": 1, "make_model": "EMSCO F-1000", "liner_diameter": 6.5, "stroke_length": 12,
             "rod_diam_duplex": 0, "eficiencia_pct": 97, "pump_rate_spm": 80, "pump_on_report": true, "riser_pump": false}],
 "boquillas": [{"size_32nds": 14, "cantidad": 2}, {"size_32nds": 13, "cantidad": 3}],
 "bit_data": {"bit_description": "", "bit_number": "", "washout_pct": 5, "bit_size": 12.25, "...": "..."}}
```

Respuesta: `total_flow_rate_calculado`, `washout_hole_size` (calculado) y `tfa`.

### Pestaña 3 — Propiedades del lodo

| Método | Ruta |
|---|---|
| GET | `mud-properties/` |
| POST | `mud-properties/guardar/` |

```json
{"config": {"solids_equation": "M-I", "is_weighted": true, "sg_base_oil": 0.84, "sg_weight_material": 4.2,
            "sg_drill_solids": 2.6, "obm_salt_type": "CaCl2"},
 "primary_check_number": 1,
 "checks": [{"check_number": 1, "mud_weight": 11.5, "r600": 60, "r300": 38, "...": "..."}],
 "extra_values": [{"check_number": 1, "propiedad_extra_id": 7, "valor": "12"}]}
```

PV y YP se recalculan en el servidor si vienen R600 y R300. El análisis de sólidos se recalcula en cada guardado.

### Pestaña 4 — Geometría del pozo

| Método | Ruta | |
|---|---|---|
| GET | `well-geometry/` | Sarta, intervalos, riser, perfil del pozo y volúmenes calculados |
| POST | `well-geometry/guardar/` | Reemplaza la sarta del día |
| GET | `well-geometry/sarta-anterior/` | Sarta del reporte anterior, para heredarla |

```json
{"intervalo_costo_id": 3, "orden_impresion_intervalo": 1,
 "pilot_hole_size_in": 0, "pilot_hole_depth_ft": 0,
 "tramos": [{"componente_id": 4, "descripcion": "DP 5\"", "longitud_ft": 6500, "od_in": 5, "id_in": 4.276,
             "tool_joint_od_in": 6.375, "tool_joint_id_in": 3.75, "tool_joint_length_in": 21, "largo_tramo_ft": 31}]}
```

Las filas de `tramos` van **desde la mecha hacia arriba** (la primera es la mecha).

### Pestaña 5 — Comentarios

| Método | Ruta |
|---|---|
| GET | `comentarios/` (devuelve también `recap_anterior`) |
| POST | `comentarios/guardar/` |

```json
{"spec_mud_weight": "11.5-12.0", "spec_viscosidad": "", "spec_filtrado": "3.0-5.0",
 "mud_recap_remarks": "una sola línea", "remarks_and_treatment": "", "remarks": ""}
```

### Pestaña 6 — Control de sólidos

| Método | Ruta | Cuerpo |
|---|---|---|
| GET | `control-solidos/` | Inventario de mallas del día, posiciones, tickets y transacciones |
| POST | `control-solidos/transaccion/` | `{"accion": "INSTALAR_NUEVA", "malla_id": 1, "serie": "ZA-01", "posicion": 2}` |
| POST | `control-solidos/transaccion/deshacer/` | Sin cuerpo. Deshace la última del pozo si es de este reporte |
| POST | `control-solidos/ticket/guardar/` | `{"id": null, "tipo_id": 1, "numero": "T-001", "pedido_por": "", "recibido_por": "", "almacen_codigo": "", "detalles": [{"malla_id": 1, "nuevas_ticket": 10, "nuevas_real": 10, "usadas_ticket": 0, "usadas_real": 0}]}` |
| POST | `control-solidos/ticket/<ticket_pk>/eliminar/` | |
| POST | `control-solidos/tipo-ticket/guardar/` | `{"id": null, "nombre": "Recepción desde almacén", "sentido": "ENTRADA"}` |
| POST | `control-solidos/tipo-ticket/<tipo_pk>/eliminar/` | Falla si hay tickets de ese tipo |
| GET | `control-solidos/equipos/` | Uso de equipos del día con acumulados |
| POST | `control-solidos/equipos/guardar/` | `{"equipos": [{"serie", "horas", "mud_on_cuttings", "porcentaje_recortes", "tipo_perdida_codigo", "caudal_entrada_gpm", "densidad_entrada", "densidad_salida", "densidad_descarte", "cantidad_usada", "codigo_cobro", "es_fluidos", "horas_parada", "observaciones", "propiedades": [{"descripcion", "unidad", "valor"}]}]}` |

Acciones de malla: `INSTALAR_NUEVA`, `INSTALAR_USADA`, `A_ALMACEN`, `DESECHAR_EQUIPO`, `DESECHAR_ALMACEN`. Códigos de cobro: `COMPLETO`, `STANDBY`, `SIN_COBRO`.

### Pestaña 7 — Distribución de tiempo

| Método | Ruta |
|---|---|
| GET | `tiempo/` |
| POST | `tiempo/guardar/` |

```json
{"horas_periodo": 24, "actividades": [{"tipo_numero": 2, "horas": 18.5}, {"tipo_numero": 3, "horas": 5.5}]}
```

### Pestaña 8 — Inventario, hidráulica y concentraciones

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `volumetria/` | Estado completo: fosas, balance por grupo, pérdidas, inventario, costos, concentraciones, movimientos, tickets |
| POST | `volumetria/guardar/` | Datos medidos a mano (ver abajo) |
| POST | `volumetria/transaccion/` | Registra un movimiento |
| POST | `volumetria/transaccion/deshacer/` | Deshace el último movimiento del pozo |
| POST | `volumetria/ticket/guardar/` | Ticket de productos |
| POST | `volumetria/ticket/<ticket_pk>/eliminar/` | |
| GET | `hidraulica/?edicion=4` o `?edicion=5` | Hidráulica API 13D (sin `edicion`, usa la configuración del pozo) |
| GET | `/api/pozos/<pk>/perdidas-reporte/` | Categorías de pérdida que salen en el reporte (máx. 10) |
| POST | `/api/pozos/<pk>/perdidas-reporte/guardar/` | `{"codigos": [1, 3, 5]}` |

`volumetria/guardar/`:

```json
{"fosas": [{"numero": 1, "tipo_codigo": 1, "real": 420.5, "peso": 11.5, "temperatura": 120}],
 "hoyo": {"anular": 0, "sarta": 0, "bajo_mecha": 0},
 "inventario": [{"producto_id": 12, "usado_otro": 0, "ajuste": 0, "en_pedido": 20, "no_imprimir": false}]}
```

`volumetria/transaccion/` según `tipo`:

```json
{"tipo": "QUIMICOS", "fosa": 1, "aceite": 50, "agua": 10, "productos": [{"producto_id": 12, "cantidad": 20}]}
{"tipo": "LODO_ENTERO", "fosa": 2, "volumen": 300, "peso": 11.5, "lodo_producto_id": 40, "origen": "Planta",
 "concentraciones": [{"producto_id": 12, "concentracion": 6}]}
{"tipo": "TRANSFERENCIA", "fosa": 2, "destino": 1, "volumen": 150}
{"tipo": "DEVOLUCION", "fosa": 3, "volumen": 80, "destino_texto": "Almacén Maturín"}
{"tipo": "PERDIDA", "fosa": 1, "volumen": 12, "perdida_codigo": 1}
```

`volumetria/ticket/guardar/`:

```json
{"id": null, "tipo_id": 1, "numero": "", "pedido_por": "", "recibido_por": "", "almacen_codigo": "",
 "detalles": [{"producto_id": 12, "cantidad_ticket": 100, "cantidad_real": 98}]}
```

---

## 7. Módulos opcionales

| Método | Ruta | Cuerpo |
|---|---|---|
| GET / POST | `.../ife/` | `{"fluidos_resumen", "fluidos_plan", "solidos_resumen", "solidos_plan"}` |
| GET | `.../muestras/solidos/` o `.../muestras/retencion/` | Lista de muestras y equipos del pozo |
| POST | `.../muestras/<clave>/guardar/` | Ver abajo |
| POST | `.../muestras/<clave>/<muestra_pk>/eliminar/` | |
| GET | `.../eventos/` | Eventos no programados de **todo el pozo** |
| POST | `.../eventos/guardar/` | `{"id", "categoria", "tipo_problema", "tipo_fluido", "descripcion", "causa", "descripcion_perdida", "horas_perdidas", "volumen_perdido_bbl", "costo"}` |
| POST | `.../eventos/<evento_pk>/eliminar/` | |
| GET | `.../benchmark/` | Evaluación objetivo contra real (solo lectura) |

Muestras (`<clave>` = `solidos` o `retencion`):

```json
{"id": null, "equipo_serie": "CF-01", "hora_inicio": "08:00", "hora_fin": "09:00", "orden": 1,
 "profundidad_ft": 7000, "profundidad_perforada_ft": 200, "comentarios": "",
 "tipo_lodo": "WBM", "tipo_muestra": "descarga",
 "datos": {"mud_weight": 14.2, "water_pct": 60, "oil_pct": 0, "solids_pct": 40, "...": "..."}}
```

Campos de `datos`:

- Sólidos WBM: `mud_weight, water_pct, oil_pct, solids_pct, k_from_kcl, drill_solids_sg, wt_additive_sg, oil_sg, frac_bent, chem_conc, mbt, chlorides`
- Sólidos OBM: `mud_weight, water_pct, oil_pct, solids_pct, oil_sg, wt_additive_sg, drill_solids_sg, chlorides, sal ("CaCl2"/"NaCl")`
- Retención (más `diametro_mecha_in` fuera de `datos`): `peso_lodo, pct_fluido_base, sg_fluido_base, sg_solidos, celda_vacia, celda_humedo, celda_seco, probeta_vacia, agua_cc, probeta_total`

---

## 8. Admin

`/admin/` expone los modelos registrados en `operaciones/admin.py` (productos, pozos con sus unidades y categorías de pérdida en línea, y los demás catálogos).
