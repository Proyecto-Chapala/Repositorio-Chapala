# Reportes — Modelo de datos

Todos los modelos viven en la app `operaciones`, repartidos en cinco archivos:

| Archivo | Contenido |
|---|---|
| `models.py` | `Producto`, `Pozo` y toda su configuración; catálogos maestros globales |
| `models_daily_reports.py` | `ReporteDiario` y pestañas 1 a 5 y 7 |
| `models_control_solidos.py` | Pestaña 6 |
| `models_inventario.py` | Pestaña 8 |
| `models_opcionales.py` | Módulos opcionales |

`models.py` importa los otros cuatro al final, así que todo se puede importar desde `operaciones.models`.

---

## Diagrama general

```
                          ┌───────────── Catálogos maestros globales ─────────────┐
                          │ Producto · Equipo · MallaZaranda · ComponenteSarta     │
                          │ PropiedadEquipoTipo · ParametroBenchmark               │
                          │ PlantillaExtraLabels → PlantillaExtraLabelItem         │
                          └───────────────────────────────────────────────────────┘
Pozo ─┬─ PropiedadUnidadPozo          (unidades personalizadas)
      ├─ CategoriaPerdidaItem         (configuración de pérdidas)
      ├─ WellHeaderInfo (1:1)         (información general + riser)
      ├─ IntervaloRevestimiento       (revestidores y costo)
      ├─ TipoFosa · Fosa              (fosas)
      ├─ AlmacenCodigo · TipoDistribucionTiempo
      ├─ ProductoActivoPozo · EquipoActivoPozo · MallaActivaPozo
      ├─ EquipoPropiedadSeleccionada · EquipoPropiedadExtra · CentrifugaUnidadConfig (1:1)
      ├─ BenchmarkSeleccionado · BenchmarkTarget
      ├─ PropiedadExtraFluido · WellSurveyStation · WellFormationTop
      ├─ TipoTicketMalla · PerdidaReportePozo
      └─ ReporteDiario (uno por fecha) ─┬─ pestaña 2: ReporteDiarioBomba · ReporteDiarioBitData (1:1) · ReporteDiarioBoquilla
                                        ├─ pestaña 3: ReporteDiarioMudConfig (1:1) · ReporteDiarioMudCheck → ReporteDiarioMudExtraValue
                                        ├─ pestaña 4: TramoSarta
                                        ├─ pestaña 5: ReporteDiarioComentarios (1:1)
                                        ├─ pestaña 6: TicketMalla → TicketMallaDetalle · TransaccionMalla · UsoEquipoDia → UsoEquipoPropiedad
                                        ├─ pestaña 7: ReporteDiarioTiempo (1:1) · ReporteDiarioActividadTiempo
                                        ├─ pestaña 8: VolumenFosaDia · VolumenHoyoDia (1:1) · TransaccionVolumen → TransaccionVolumenProducto
                                        │             InventarioProductoDia · TicketProducto → TicketProductoDetalle
                                        └─ opcionales: ObservacionesIFE (1:1) · AnalisisSolidosEquipo · RetencionRecortes · EventoNoProgramado
```

Borrar un pozo borra en cascada todo lo que cuelga de él. Borrar un reporte borra todo lo de ese día.

---

## Regla clave: listas activas "borrar y recrear"

Las grillas de configuración del pozo se guardan **reemplazando todas las filas**:

`Fosa`, `TipoFosa`, `CategoriaPerdidaItem`, `AlmacenCodigo`, `TipoDistribucionTiempo`, `ProductoActivoPozo`, `EquipoActivoPozo`, `MallaActivaPozo`, `EquipoPropiedadSeleccionada`, `EquipoPropiedadExtra`, `BenchmarkSeleccionado`, `BenchmarkTarget`, `PropiedadUnidadPozo`, `WellSurveyStation`, `WellFormationTop`, `PerdidaReportePozo`.

Por eso **ningún dato diario tiene llave foránea a esas filas**. Los datos diarios guardan una referencia estable + una copia del texto:

| Dato diario | Se refiere a... | Guarda |
|---|---|---|
| `VolumenFosaDia`, `TransaccionVolumen` | Fosa | `fosa_numero` + `fosa_descripcion` |
| `VolumenFosaDia` | Tipo de fosa | `tipo_codigo` + `tipo_descripcion` |
| `TransaccionVolumen`, `UsoEquipoDia` | Categoría de pérdida | `perdida_codigo` / `tipo_perdida_codigo` + descripción |
| `ReporteDiarioActividadTiempo` | Actividad de tiempo | `tipo_numero` + `descripcion` |
| `TransaccionMalla`, `UsoEquipoDia`, muestras opcionales | Equipo activo | FK a `Equipo` (maestro) + `equipo_serie` + `equipo_descripcion` |
| `TicketMalla`, `TicketProducto` | Almacén | `almacen_codigo` + `almacen_nombre` |
| Mallas y productos | Malla / producto activo | FK al **maestro** (`MallaZaranda`, `Producto`) |
| `UsoEquipoPropiedad` | Propiedad de equipo | `descripcion` + `unidad` |

---

## Migraciones

| Migración | Crea o cambia |
|---|---|
| `0001_initial` | `Producto` |
| `0002` | `Pozo`, `CategoriaPerdidaItem`, `PropiedadUnidadPozo` |
| `0003` | `WellHeaderInfo`, `Fosa`, `IntervaloRevestimiento`, `TipoFosa` |
| `0004` | `AlmacenCodigo`, `TipoDistribucionTiempo`; ajustes a fosas, intervalos, pozo y encabezado |
| `0005` | `Equipo`, `MallaZaranda`, `ProductoActivoPozo`, `EquipoActivoPozo`, `MallaActivaPozo` |
| `0006` | `Equipo.tipo_equipo`; `CentrifugaUnidadConfig`, `EquipoPropiedadExtra`, `PropiedadEquipoTipo`, `EquipoPropiedadSeleccionada`, `ParametroBenchmark`, `BenchmarkSeleccionado`, `BenchmarkTarget` |
| `0007` | `PlantillaExtraLabels`, `PlantillaExtraLabelItem`, `PropiedadExtraFluido`, **`ReporteDiario`** |
| `0008` | `WellSurveyStation` |
| `0009` | `WellFormationTop` |
| `0010` | `ReporteDiarioBitData`, `ReporteDiarioBoquilla`, `ReporteDiarioBomba` |
| `0011` | `ReporteDiarioMudCheck`, `ReporteDiarioMudConfig`, `ReporteDiarioMudExtraValue` |
| `0012` | Campos de análisis de sólidos WBM en `ReporteDiarioMudCheck` (bentonita, drill solids, etc.) |
| `0013` | Campos OBM (`adjusted_solids_pct`, OWR, SG promedio) y `obm_salt_type` |
| `0014` | `ComponenteSarta`, `TramoSarta`; riser en `WellHeaderInfo`; hoyo piloto e intervalo de costo en `ReporteDiario` |
| `0015` | `ReporteDiarioComentarios` |
| `0016` | `ReporteDiarioTiempo`, `ReporteDiarioActividadTiempo` |
| `0017` | `Equipo.posiciones_malla`; `TipoTicketMalla`, `TicketMalla`, `TicketMallaDetalle`, `TransaccionMalla` |
| `0018` | `UsoEquipoDia`, `UsoEquipoPropiedad`; ajustes de tipos de equipo y propiedades |
| `0019` | `PerdidaReportePozo` |
| `0020` | Volumetría: `VolumenFosaDia`, `VolumenHoyoDia`, `TransaccionVolumen`, `TransaccionVolumenProducto`, `InventarioProductoDia`, `TicketProducto`, `TicketProductoDetalle` |
| `0021` | Opcionales: `ObservacionesIFE`, `AnalisisSolidosEquipo`, `RetencionRecortes`, `EventoNoProgramado` |
| `0022` | Inventario unificado: `stock_aplicado` / `lodo_stock_aplicado`. Marca los consumos existentes como ya aplicados (no descuenta nada) |

---

## Pozo y configuración

### `Pozo`

Equivale al archivo `.MDB` de un pozo en ONE-TRAX.

| Grupo | Campos |
|---|---|
| Paso 1 | `nombre` (único), `pozo_plantilla` (FK a otro pozo ACTIVO) |
| Paso 2 | `sistema_unidades` (`STANDARD_OILFIELD`, `STANDARD_1..3`, `SI_METRIC`, `METRIC_1..5`, `CUSTOM`), `unidades_bloqueadas` |
| Paso 3 | `moneda_simbolo` (USD), `moneda_decimales` (0-4), `tasa_impuesto` (0-100 %), `ecuacion_solidos_base_agua` y `_base_aceite` (`MI`/`API`), `categoria_perdida_tipo` (`MI`, `UK`, `HYDRO`, `STATOIL`, `IFE`, `COMPLETION_FLUIDS`, `CUSTOM`) |
| Hidráulica | `usar_api_5ta_edicion_hidraulica` |
| Spud Date | `fecha_primera_captura`, `tipo_fluido_inicial` (`WATER_BASE`, `WATER_BASE_CACL2`, `OIL_BASE`, `SYNTHETIC_BASE`, `COMPLETION_FLUIDS`), `con_tratamiento_disposicion`, `numero_control_logit`, `spud_date_completado` |
| Control | `estado` (`BORRADOR`, `ACTIVO`, `CERRADO`), `paso_wizard_actual`, `creado_por`, fechas |

Métodos: `clonar_configuracion_desde_plantilla()`, `clonar_categorias_perdida()`, `clonar_unidades_personalizadas()`, `clonar_fosas_y_tipos()`, `activar()`.

### Otras tablas del pozo

| Modelo | Clave única | Campos principales |
|---|---|---|
| `PropiedadUnidadPozo` | pozo + propiedad | 16 propiedades (profundidad, volumen, caudal, presión...) con sus unidades válidas en `OPCIONES_UNIDAD` |
| `CategoriaPerdidaItem` | pozo + código | `codigo`, `descripcion`, `tipo` (`SUPERFICIE`/`SUBSUELO`). 15 estándar sembradas |
| `WellHeaderInfo` (1:1) | pozo | Offshore (`es_offshore`, `air_gap_ft`, `water_depth_ft`, `sea_floor_temp_f`), riser (`usa_riser`, `riser_id_in`, `riser_length_ft`), operador, campo, taladro, ingenieros, fechas, temperatura de superficie y gradiente (5ª edición), datos de cierre del pozo, códigos de mercadeo |
| `IntervaloRevestimiento` | pozo + número | `tipo`, OD/ID del revestidor, diámetro de hoyo, profundidad de zapata, TVD, tope de liner, densidad máxima, BHT, ángulo, días y longitud planeados/reales, costos, gradiente de fractura, comentarios de recap (máx. 10 000 caracteres) |
| `TipoFosa` | pozo + código | 0 Vacía, 1 Activa, 2 Reserva, 3 Premix, 4 Espaciador, 5 Píldora, 6 Rompedor |
| `Fosa` | pozo + número | `numero`, `descripcion`, `capacidad` (bbl) |
| `AlmacenCodigo` | pozo + código | `codigo`, `nombre` |
| `TipoDistribucionTiempo` | pozo + número | `numero`, `descripcion`, `tipo` (`DF`, `CF`, `DF/CF`). 20 estándar sembradas |
| `ProductoActivoPozo` | (sin única) | FK `Producto` + abreviatura, `unit_size`, `unidad`, `empaque`, `precio`, `gravedad_especifica`, `calcular_concentracion`, `es_producto_mi`, `grupo_producto`, `codigo_costo_diario`, categorías de costo WMgt y CF. Se permite el mismo producto dos veces (como ONE-TRAX 1.5) |
| `EquipoActivoPozo` | pozo + número de serie | FK `Equipo` + `numero_serie`, `descripcion`, `precio_renta`, `precio_standby` |
| `MallaActivaPozo` | pozo + malla | FK `MallaZaranda` + `precio`, `descuento_porcentaje` |
| `EquipoPropiedadSeleccionada` | pozo + propiedad | Propiedades estándar marcadas por tipo de equipo |
| `EquipoPropiedadExtra` | — | Propiedades de texto libre por tipo de equipo |
| `CentrifugaUnidadConfig` (1:1) | pozo | Unidades de caudal y masa de la centrífuga |
| `BenchmarkSeleccionado` | pozo + parámetro | Parámetros a monitorear |
| `BenchmarkTarget` | pozo + parámetro + intervalo + min_max | Valor objetivo; `intervalo` vacío = pozo completo |

### Catálogos maestros globales

| Modelo | Campos |
|---|---|
| `Equipo` | `codigo` (único), `nombre`, `tipo_equipo` (`CENTRIFUGA`, `LIMPIADOR_LODO`, `ZARANDA`, `SECADOR_RECORTES`, `SISTEMA_VACIO`, `CONTENEDOR_RECORTES`, `OTROS`), `posiciones_malla` (0-12; la 1 es la más cercana a la línea de flujo) |
| `MallaZaranda` | `codigo` (único), `descripcion`, `mesh_size` |
| `ComponenteSarta` | `codigo`, `descripcion`, `tipo` (`MECHA`, `MOTOR`, `DRILL_COLLAR`, `HEAVY_WEIGHT`, `DRILL_PIPE`, `ESTABILIZADOR`, `CROSSOVER`, `REVESTIDOR`, `OTROS`), `od_in`, `id_in`, junta (`tool_joint_od_in`, `_id_in`, `_length_in`), `largo_tramo_ft` (31 por defecto) |
| `PropiedadEquipoTipo` | `tipo_equipo`, `descripcion`, `unidad`, `orden` |
| `ParametroBenchmark` | `grupo`, `descripcion`, `unidad`, `tipo_fluido` (`WBM`, `OBM`, `AMBOS`, `NA`), `tipo_dato` (`NUMERICO`, `MIN_MAX`, `TEXTO`) |
| `PlantillaExtraLabels` → `PlantillaExtraLabelItem` | Plantillas de etiquetas extra (por ejemplo "Statoil") |

---

## Reporte diario

### `ReporteDiario`

Un reporte por pozo y fecha (`unique_together = (pozo, fecha)`). Orden: fecha descendente.

| Grupo | Campos |
|---|---|
| Identificación | `pozo`, `fecha`, `tipo_lodo` (`WBM`, `WBM_CACL2`, `OBM`, `SBM`) |
| Pestaña 1 | `profundidad_actual`, `profundidad_tvd`, `bit_depth`, `actividad_actual`, `tipo_fluido_display`, `litologia`, representantes y teléfonos |
| Pestaña 4 | `intervalo_costo` (FK a `IntervaloRevestimiento`, SET_NULL), `orden_impresion_intervalo`, `pilot_hole_size_in`, `pilot_hole_depth_ft` |

`numero_reporte` es una propiedad calculada: cantidad de reportes del pozo con fecha menor o igual.

### Pestaña 2

| Modelo | Clave | Notas |
|---|---|---|
| `ReporteDiarioBomba` | reporte + número | Siempre 4 bombas. `desplazamiento_bbl_stk = 0.000243 × liner² × carrera × eficiencia`; `caudal_gpm = bbl/stk × 42 × spm` (0 si `pump_on_report` es falso) |
| `ReporteDiarioBitData` (1:1) | reporte | Mecha, parámetros de perforación, presiones, datos de ECD (código de superficie 1-5, presión y caudal de referencia) |
| `ReporteDiarioBoquilla` | — | `size_32nds`, `cantidad`; `area_sq_in` para el TFA |

### Pestaña 3

| Modelo | Clave | Notas |
|---|---|---|
| `ReporteDiarioMudConfig` (1:1) | reporte | Ecuación de sólidos, lodo densificado, SG de aceite base, material densificante y sólidos perforados, sal de la fase interna (CaCl2/NaCl) |
| `ReporteDiarioMudCheck` | reporte + número (1-4) | Todos los parámetros del chequeo y resultados del análisis de sólidos. Métodos `calcular_reologia_automatica`, `calcular_solids_analysis_wbm`, `calcular_solids_analysis_obm` |
| `PropiedadExtraFluido` | pozo + tipo + número | Hasta 60 etiquetas extra por tipo de fluido; `orden_impresion` 0 = no se imprime |
| `ReporteDiarioMudExtraValue` | chequeo + propiedad | Valor de una propiedad extra en un chequeo |

### Pestaña 4

`TramoSarta` (reporte + orden). Orden 1 = mecha, hacia arriba. FK opcional a `ComponenteSarta` (SET_NULL). Diámetros de cuerpo y junta, longitud, largo de tramo. Propiedad `fraccion_junta`.

Por pozo: `WellSurveyStation` (MD, inclinación, azimut, TVD, DLS, sección vertical) y `WellFormationTop` (profundidad, formación, litología, % arena).

### Pestaña 5

`ReporteDiarioComentarios` (1:1): especificación de lodo (`spec_mud_weight`, `spec_viscosidad`, `spec_filtrado`) y tres textos (`mud_recap_remarks`, `remarks_and_treatment`, `remarks`).

### Pestaña 6

| Modelo | Notas |
|---|---|
| `TipoTicketMalla` | Por pozo. `nombre` + `sentido` (`ENTRADA`/`SALIDA`). También lo usan los tickets de productos |
| `TicketMalla` → `TicketMallaDetalle` | Por malla: nuevas y usadas "según ticket" y "reales". El inventario usa las reales |
| `TransaccionMalla` | `secuencia` por pozo, `accion`, malla, equipo + serie + descripción, `posicion`, `precio_unitario` (solo al instalar nueva) |
| `UsoEquipoDia` | Por reporte y serie: horas, MOC, % recortes, tipo de pérdida, datos de centrífuga, cantidad usada, código de cobro, tarifa copiada, horas de parada, observaciones. `costo_diario = cantidad × tarifa` (0 sin cobro) |
| `UsoEquipoPropiedad` | Valores del día de las propiedades de equipo |

### Pestaña 7

`ReporteDiarioTiempo` (1:1): `horas_periodo` (24 por defecto). `ReporteDiarioActividadTiempo`: `tipo_numero`, `descripcion`, `horas`. Las actividades 1 a 4 son fijas.

### Pestaña 8

| Modelo | Notas |
|---|---|
| `PerdidaReportePozo` | Por pozo, máximo 10 códigos de pérdida en orden |
| `VolumenFosaDia` | Por reporte y fosa: tipo del día, volumen real medido, peso, temperatura |
| `VolumenHoyoDia` (1:1) | Volumen del hoyo **no** ocupado por fluido (anular, sarta, bajo la mecha) |
| `TransaccionVolumen` | `secuencia` por pozo, `tipo` (`QUIMICOS`, `LODO_ENTERO`, `TRANSFERENCIA`, `DEVOLUCION`, `PERDIDA`), fosa y destino, volumen, aceite, agua, peso, lodo entero consumido, origen/destino, pérdida |
| `TransaccionVolumenProducto` | Producto de un movimiento: cantidad o concentración, con copia de unidad, tamaño, gravedad, precio y categoría. `stock_aplicado`: cuánto se descontó del inventario general |
| `InventarioProductoDia` | Columnas a mano: usado en otro módulo, ajuste (±), en pedido, no imprimir. `stock_aplicado`: neto descontado del inventario general |
| `TicketProducto` → `TicketProductoDetalle` | Tickets de productos; cantidades según ticket y reales |

### Opcionales

Ver [MODULOS_OPCIONALES.md](MODULOS_OPCIONALES.md). `AnalisisSolidosEquipo` y `RetencionRecortes` guardan los datos de la muestra en un campo JSON `datos`.
