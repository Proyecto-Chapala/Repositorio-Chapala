# 03 — Modelo de datos

> Este documento se generó **a partir del código real**, por introspección de los modelos de Django, el 25-sep-2026. Cubre los **57 modelos** de la app `operaciones`, repartidos en 5 archivos. Actualizado el 27-sep-2026 con los cambios de las migraciones 0022-0024 (ver "Cambios del 27-sep" al final). Si cambias un modelo, actualiza la sección correspondiente o vuelve a generar las tablas (ver [19](19_GUIA_MANTENIMIENTO.md#regenerar-la-documentación-del-modelo-de-datos)).

## Mapa de relaciones (resumen)

```
                         ┌──────────────── CATÁLOGOS MAESTROS GLOBALES ────────────────┐
                         │ Producto · Equipo · MallaZaranda · ComponenteSarta            │
                         │ PropiedadEquipoTipo · ParametroBenchmark · PlantillaExtraLabels│
                         └───────────────────────────────────────────────────────────────┘
                                         ▲ (FK desde las listas del pozo y los datos diarios)
Pozo ─┬─ configuración (1 por pozo): WellHeaderInfo · CentrifugaUnidadConfig · RecapPozo
      ├─ listas del pozo (borrar-y-recrear): PropiedadUnidadPozo · CategoriaPerdidaItem · TipoFosa · Fosa
      │     AlmacenCodigo · TipoDistribucionTiempo · ProductoActivoPozo · EquipoActivoPozo · MallaActivaPozo
      │     EquipoPropiedadSeleccionada · EquipoPropiedadExtra · BenchmarkSeleccionado · BenchmarkTarget
      │     PropiedadExtraFluido · PerdidaReportePozo · TipoTicketMalla
      ├─ IntervaloRevestimiento (intervalos de costo)  ◄── ReporteDiario.intervalo_costo
      ├─ WellSurveyStation · WellFormationTop
      └─ ReporteDiario (1 por fecha) ─┬─ Pestaña 2: ReporteDiarioBomba · ReporteDiarioBitData · ReporteDiarioBoquilla
                                      ├─ Pestaña 3: ReporteDiarioMudConfig · ReporteDiarioMudCheck ─ ReporteDiarioMudExtraValue
                                      ├─ Pestaña 4: TramoSarta
                                      ├─ Pestaña 5: ReporteDiarioComentarios
                                      ├─ Pestaña 6: TicketMalla ─ TicketMallaDetalle · TransaccionMalla
                                      │             UsoEquipoDia ─ UsoEquipoPropiedad
                                      ├─ Pestaña 7: ReporteDiarioTiempo · ReporteDiarioActividadTiempo
                                      ├─ Pestaña 8: VolumenFosaDia · VolumenHoyoDia · TransaccionVolumen ─ TransaccionVolumenProducto
                                      │             InventarioProductoDia · TicketProducto ─ TicketProductoDetalle
                                      └─ Opcionales: ObservacionesIFE · AnalisisSolidosEquipo · RetencionRecortes · EventoNoProgramado
```

## Reglas de integridad que no están en el esquema

1. **Un reporte por fecha y pozo.** Lo valida `api_reporte_diario_crear`. El número de reporte (`ReporteDiario.numero_reporte`) **no se guarda**: se calcula como la posición del reporte por fecha dentro del pozo. Si se borra un reporte intermedio, los números siguientes se corren.
2. **Borrado en cascada.** Borrar un `Pozo` borra todo lo suyo. Borrar un `ReporteDiario` borra todos sus datos de pestañas, tickets y transacciones, y la línea de tiempo del pozo **se recalcula sin ellos**. Ojo: eso puede dejar sin stock a días posteriores, y ese borrado **no se valida**.
3. **Datos diarios sin FK a listas del pozo.** Guardan el catálogo maestro o el número/código, más una copia del texto (ver [02 § C](02_ARQUITECTURA.md#c-listas-del-pozo-borrar-y-recrear)).
4. **Saldos derivados.** No existen columnas de "stock actual" para mallas ni para productos del pozo. `Producto.cantidad` es el stock **del almacén** (módulo Inventario). Desde la migración `0022_inventario_unificado` (compañero xtal) el reporte diario **descuenta y devuelve** `Producto.cantidad` usando los campos `stock_aplicado` (ver "Cambios del 27-sep").
5. **Inmutables tras el Spud Date:** `Pozo.fecha_primera_captura` y `Pozo.tipo_fluido_inicial`. Tras confirmar el wizard, las unidades del pozo quedan bloqueadas (`unidades_bloqueadas`).

## Historial de migraciones

| Migración | Contenido principal |
|---|---|
| 0001 | `Producto` (inventario de almacén) |
| 0002 | `Pozo`, `CategoriaPerdidaItem`, `PropiedadUnidadPozo` |
| 0003 | `WellHeaderInfo`, `Fosa`, `IntervaloRevestimiento`, `TipoFosa` |
| 0004 | `AlmacenCodigo`, `TipoDistribucionTiempo` y ajustes de campos (64 cambios) |
| 0005 | `Equipo`, `MallaZaranda`, listas activas del pozo |
| 0006 | Tipo de equipo, `PropiedadEquipoTipo`, propiedades seleccionadas/extra, `CentrifugaUnidadConfig`, `ParametroBenchmark`, `BenchmarkSeleccionado`, `BenchmarkTarget` |
| 0007 | `ReporteDiario`, `PropiedadExtraFluido`, `PlantillaExtraLabels`, `PlantillaExtraLabelItem` |
| 0008 | `WellSurveyStation` |
| 0009 | `WellFormationTop` |
| 0010 | Bombas, barrena y boquillas (pestaña 2) |
| 0011 | Configuración y chequeos de lodo (pestaña 3) |
| 0012–0013 | Campos de balance de sólidos del chequeo de lodo |
| 0014 | `ComponenteSarta`, `TramoSarta`, riser, hoyo piloto (pestaña 4) |
| 0015 | `ReporteDiarioComentarios` (pestaña 5) |
| 0016 | Distribución de tiempo (pestaña 7) |
| 0017 | Mallas: tickets y transacciones (pestaña 6) |
| 0018 | Uso diario de equipos (pestaña 6) |
| 0019 | `PerdidaReportePozo` (pestaña 8) |
| 0020 | Volumetría e inventario de productos (pestaña 8) |
| 0021 | Módulos opcionales |
| 0022_inventario_unificado | (compañero) campos `stock_aplicado` / `lodo_stock_aplicado`: el reporte descuenta `Producto.cantidad` |
| 0022_sidetrack | `ReporteDiario.kickoff_sidetrack_ft` y tipo `SIDETRACK` en `IntervaloRevestimiento` (depende de 0021) |
| 0023_recap_pozo | `RecapPozo` (textos del reporte final) |
| 0024_merge | Une las dos ramas (0022_inventario_unificado + 0023_recap_pozo) |
| 0025_add_empaque_to_producto | (compañero) `Producto.empaque` y texto de ayuda de `Producto.unidad` |
| 0026_textos_smart_mud | Quita "M-I": ecuaciones de sólidos solo `API` (datos viejos pasan a API), etiqueta "Estándar" en categorías de pérdida, "¿Producto propio?" |
| 0027_intervalo_cerrado_moneda_secundaria | `IntervaloRevestimiento.cerrado`; `Pozo.moneda_secundaria`, `tasa_cambio_secundaria`, `porcentaje_cobro_secundaria`. Cierra los intervalos viejos menos el último de cada pozo. **La próxima migración depende de esta** |

# Detalle por modelo

## Núcleo: pozo, configuración y catálogos (`models.py`)

### Producto — Producto de Inventario

Tabla: `operaciones_producto` · Migración: `0001_initial` · Orden: `codigo`

| Campo | Tipo | Detalles |
|---|---|---|
| `codigo` | CharField(50) | Código del Producto; único; Código único identificador del producto (SKU) |
| `descripcion` | CharField(255) | Descripción |
| `unidad` | CharField(50) | Unidad Física (0025); Ej: LBS, GAL, BBL, KG, L |
| `empaque` | CharField(50) | (0025) Empaque; Ej: SACOS, TAMBOR, TOTE, LATA, GRANEL |
| `libraje` | DecimalField(12,2) | Libraje (LBS); por defecto `0.0`; Peso o libraje unitario en libras |
| `gravedad` | DecimalField(8,4) | Gravedad Específica; por defecto `1.0` |
| `costo` | DecimalField(14,2) | Costo Unitario ($); por defecto `0.0` |
| `cantidad` | DecimalField(14,2) | Cantidad (Stock); por defecto `0.0` |
| `categoria` | CharField(10) | Categoría; por defecto `'SOLIDO'`; opciones: `SOLIDO`, `LIQUIDO` |
| `estado` | CharField(10) | Estado de Stock; por defecto `'ALTO'`; opciones: `ALTO`, `MEDIO`, `BAJO` |
| `observacion` | TextField | Observación; opcional (null) |
| `created_at` | DateTimeField |  |
| `updated_at` | DateTimeField |  |

### Pozo — Pozo

Tabla: `operaciones_pozo` · Migración: `0002_pozo_categoriaperdidaitem_propiedadunidadpozo` · Orden: `-created_at`

> Representa un Pozo (Well), equivalente al archivo .MDB de ONE-TRAX. Se crea a través del wizard de 4 pasos. Mientras el wizard está en curso, el registro vive en estado BORRADOR (permite autoguardado paso a paso); al confirmar el paso 4 pasa a ACTIVO y las unidades quedan bloqueadas.

| Campo | Tipo | Detalles |
|---|---|---|
| `nombre` | CharField(150) | Nombre del Pozo; único |
| `pozo_plantilla` | ForeignKey | Pozo usado como plantilla; → **Pozo** (on_delete SET_NULL); opcional (null) |
| `sistema_unidades` | CharField(20) | Sistema de Unidades; por defecto `'STANDARD_OILFIELD'`; opciones: `STANDARD_OILFIELD`, `STANDARD_1`, `STANDARD_2`, `STANDARD_3`, `SI_METRIC`, `METRIC_1`, `METRIC_2`, `METRIC_3`, `METRIC_4`, `METRIC_5`, `CUSTOM` |
| `unidades_bloqueadas` | BooleanField | Unidades Bloqueadas; por defecto `False`; Se activa automáticamente al confirmar el paso 4 del wizard. |
| `moneda_simbolo` | CharField(6) | Moneda (código: USD, VES, EUR…; lista en `Pozo.MONEDAS_COMUNES`); por defecto `'USD'`; editable en Configuración General |
| `moneda_secundaria` | CharField(6) | (0027) Segunda moneda de cobro; vacío = no hay |
| `tasa_cambio_secundaria` | Decimal(18,4) | (0027) Unidades de la segunda moneda por 1 de la del pozo |
| `porcentaje_cobro_secundaria` | Decimal(5,2) | (0027) % del costo que se cobra en la segunda moneda; por defecto 0 |
| `moneda_decimales` | PositiveSmallIntegerField | Decimales de Moneda; por defecto `2` |
| `tasa_impuesto` | DecimalField(5,2) | Tasa de Impuesto (%); por defecto `0` |
| `ecuacion_solidos_base_agua` | CharField(5) | Ecuación de Sólidos — Base Agua; por defecto `'API'`; opciones: `API` (0026; antes `MI`) |
| `ecuacion_solidos_base_aceite` | CharField(5) | Ecuación de Sólidos — Base Aceite/Sintética; por defecto `'API'`; opciones: `API` (0026) |
| `usar_api_5ta_edicion_hidraulica` | BooleanField | Usar API 5ta Edición para Cálculo Hidráulico; por defecto `False` |
| `categoria_perdida_tipo` | CharField(20) | Categorías de Pérdida; por defecto `'MI'` (se muestra "Estándar"); opciones: `MI`, `UK`, `HYDRO`, `STATOIL`, `IFE`, `COMPLETION_FLUIDS`, `CUSTOM` |
| `fecha_primera_captura` | DateField | Primera Fecha de Datos; opcional (null); Inmutable una vez confirmada. Puede ser anterior a la fecha de spud. |
| `tipo_fluido_inicial` | CharField(20) | Tipo de Fluido — Primer Chequeo; opcional (null); opciones: `WATER_BASE`, `WATER_BASE_CACL2`, `OIL_BASE`, `SYNTHETIC_BASE`, `COMPLETION_FLUIDS` |
| `con_tratamiento_disposicion` | BooleanField | Con Tratamiento y Disposición de Desechos; por defecto `False` |
| `numero_control_logit` | CharField(50) | Número de Control de Proyecto Log-It |
| `spud_date_completado` | BooleanField | Pantalla Spud Date completada; por defecto `False` |
| `estado` | CharField(10) | Estado; por defecto `'BORRADOR'`; opciones: `BORRADOR`, `ACTIVO`, `CERRADO` |
| `paso_wizard_actual` | PositiveSmallIntegerField | Último paso guardado del wizard; por defecto `1` |
| `creado_por` | ForeignKey | Creado por; → **User** (on_delete SET_NULL); opcional (null) |
| `created_at` | DateTimeField |  |
| `updated_at` | DateTimeField |  |

### PropiedadUnidadPozo — Unidad Personalizada del Pozo

Tabla: `operaciones_propiedadunidadpozo` · Migración: `0002_pozo_categoriaperdidaitem_propiedadunidadpozo` · Único por: (pozo, propiedad) · Orden: `propiedad`

> Una fila por cada propiedad de ingeniería del pozo cuando sistema_unidades = 'CUSTOM' (pantalla 'Unit Selection for New Well'). Tabla relacional (no JSON) para que cada unidad elegida quede como registro auditable e individualmente consultable.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `propiedad` | CharField(30) | opciones: `PROFUNDIDAD`, `HOYO_TUBERIA`, `VOLUMEN`, `CAUDAL`, `BOQUILLA_BROCA`, `VELOCIDAD`, `PRESION`, `FACTOR_K`, `PESO_FLUIDO`, `VISCOSIDAD_PLASTICA`, `PUNTO_CEDENCIA_GELES`, `VELOCIDAD_CHORRO` |
| `unidad` | CharField(20) | Unidad Elegida |

### CategoriaPerdidaItem — Categoría de Pérdida

Tabla: `operaciones_categoriaperdidaitem` · Migración: `0002_pozo_categoriaperdidaitem_propiedadunidadpozo` · Único por: (pozo, codigo) · Orden: `codigo`

> Fila editable de 'Loss Data Categories' cuando el pozo usa categoria_perdida_tipo = 'CUSTOM'. Ej: Shakers, Evaporation, Centrifuge, Formation, Left in Hole, Other.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `codigo` | PositiveSmallIntegerField | Código |
| `descripcion` | CharField(100) | Descripción |
| `tipo` | CharField(12) | Superficie / Subsuelo; por defecto `'SUPERFICIE'`; opciones: `SUPERFICIE`, `SUBSUELO` |

### WellHeaderInfo — Información General del Pozo

Tabla: `operaciones_wellheaderinfo` · Migración: `0003_wellheaderinfo_fosa_intervalorevestimiento_tipofosa`

> 'Well Header Information' — pantalla de 2 pestañas (Well Information + Marketing Codes) dentro del Project Main Screen. Un registro por pozo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | OneToOneField | → **Pozo** (on_delete CASCADE); único |
| `es_offshore` | BooleanField | Proyecto Offshore; por defecto `False` |
| `usa_riser` | BooleanField | El pozo usa Riser; por defecto `False`; Si está activo, el riser se incluye como primer tramo del perfil de confinamiento del pozo. |
| `riser_id_in` | DecimalField(8,3) | Diámetro Interno del Riser (in); opcional (null) |
| `riser_length_ft` | DecimalField(10,2) | Longitud del Riser (ft); opcional (null); Si se deja vacío se asume Air Gap + Water Depth. |
| `air_gap_ft` | DecimalField(10,2) | Altura Libre — Air Gap (ft); opcional (null) |
| `water_depth_ft` | DecimalField(10,2) | Profundidad de Agua (ft); opcional (null) |
| `sea_floor_temp_f` | DecimalField(6,2) | Temperatura del Lecho Marino (°F); opcional (null) |
| `operador` | CharField(150) | Operador |
| `field_area` | CharField(150) | Campo/Área |
| `descripcion` | CharField(255) | Descripción |
| `ubicacion` | CharField(150) | Ubicación |
| `almacen` | CharField(150) | Almacén |
| `contratista` | CharField(150) | Contratista |
| `nombre_taladro` | CharField(150) | Nombre del Taladro |
| `ingeniero_proyecto` | CharField(150) | Ingeniero de Proyecto |
| `ingeniero_miswaco_1` | CharField(150) | Ingeniero M-I SWACO 1 |
| `ingeniero_miswaco_2` | CharField(150) | Ingeniero M-I SWACO 2 |
| `spud_date` | DateField | Fecha de Spud; opcional (null) |
| `td_date` | DateField | Fecha de TD; opcional (null) |
| `td_days` | PositiveIntegerField | Días de TD; opcional (null) |
| `re_entry_depth_ft` | DecimalField(10,2) | Profundidad de Reentrada (ft); opcional (null) |
| `latitud_ns_indicador` | CharField(20) | Indicador de Latitud N/S |
| `longitud_ew_indicador` | CharField(20) | Indicador de Longitud E/O |
| `surface_temp_f` | DecimalField(6,2) | Temperatura Superficial (°F); opcional (null) |
| `temp_gradient_f_100ft` | DecimalField(6,2) | Gradiente de Temperatura (°F/100ft); opcional (null) |
| `total_depth_ft` | DecimalField(10,2) | Profundidad Total (ft); opcional (null) |
| `total_days` | PositiveIntegerField | Días Totales; opcional (null) |
| `maximum_temperature_f` | DecimalField(6,2) | Temperatura Máxima (°F); opcional (null) |
| `tvd_ft` | DecimalField(10,2) | TVD (ft); opcional (null) |
| `end_date` | DateField | Fecha de Fin; opcional (null) |
| `total_cost` | DecimalField(14,2) | Costo Total ($); opcional (null); Calculado; se deja manual hasta integrar el módulo de costos. |
| `horiz_displacement_ft` | DecimalField(10,2) | Desplazamiento Horizontal (ft); opcional (null); Se usa para identificar pozos de Alcance Extendido (Extended Reach). |
| `comentarios` | TextField | Comentarios |
| `numero_control_logit` | CharField(50) | Número de Control de Proyecto Log-It |
| `primary_mud_type_codigo` | CharField(20) | Tipo de Lodo Principal — Código |
| `primary_mud_type_descripcion` | CharField(150) | Tipo de Lodo Principal |
| `well_type_codigo` | CharField(20) | Tipo de Pozo — Código |
| `well_type_descripcion` | CharField(150) | Tipo de Pozo |
| `contract_type_codigo` | CharField(20) | Tipo de Contrato — Código |
| `contract_type_descripcion` | CharField(150) | Tipo de Contrato |
| `completion_fluid_type_codigo` | CharField(20) | Tipo de Fluido de Completación — Código |
| `completion_fluid_type_descripcion` | CharField(150) | Tipo de Fluido de Completación |
| `completado` | BooleanField | Información del Pozo guardada al menos una vez; por defecto `False` |
| `marketing_codes_completado` | BooleanField | Códigos de Mercadeo guardados al menos una vez; por defecto `False` |
| `created_at` | DateTimeField |  |
| `updated_at` | DateTimeField |  |

### IntervaloRevestimiento — Intervalo de Revestimiento (Casing)

Tabla: `operaciones_intervalorevestimiento` · Migración: `0003_wellheaderinfo_fosa_intervalorevestimiento_tipofosa` · Único por: (pozo, numero_intervalo) · Orden: `numero_intervalo`

> 'Well Casing Intervals (Cost)' — una fila por intervalo de revestimiento.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `numero_intervalo` | PositiveSmallIntegerField | Número de Intervalo |
| `tipo` | CharField(15) | Tipo; opciones: `CONDUCTOR`, `SUPERFICIE`, `INTERMEDIO`, `PRODUCCION`, `LINER`, `CASING`, `HOYO_ABIERTO`, `SIDETRACK` (0022) |
| `casing_od_in` | DecimalField(8,3) | OD Revestimiento (in); opcional (null) |
| `casing_id_in` | DecimalField(8,3) | ID Revestimiento (in); opcional (null) |
| `hole_size_in` | DecimalField(8,3) | Diámetro de Hoyo (in); opcional (null) |
| `profundidad_ft` | DecimalField(10,2) | Profundidad (ft); opcional (null) |
| `tvd_ft` | DecimalField(10,2) | TVD (ft); opcional (null) |
| `top_of_liner_ft` | DecimalField(10,2) | Tope de Liner (ft); opcional (null) |
| `maximum_density_lb_gal` | DecimalField(8,2) | Densidad Máxima (lb/gal); opcional (null) |
| `max_bht_f` | DecimalField(6,2) | Temperatura Máx. de Fondo — BHT (°F); opcional (null) |
| `maximum_angle` | DecimalField(6,2) | Ángulo Máximo; opcional (null) |
| `interval_days` | PositiveIntegerField | Días del Intervalo; opcional (null) |
| `planned_days` | PositiveIntegerField | Días Planeados; opcional (null) |
| `planned_length_ft` | DecimalField(10,2) | Longitud Planeada (ft); opcional (null) |
| `interval_cost` | DecimalField(14,2) | Costo del Intervalo ($); opcional (null) |
| `planned_cost` | DecimalField(14,2) | Costo Planeado ($); opcional (null) |
| `frac_grad_lb_gal` | DecimalField(8,2) | Gradiente de Fractura (lb/gal); opcional (null) |
| `fluid_type_code_1` | CharField(50) | Código de Tipo de Fluido 1 |
| `fluid_type_code_2` | CharField(50) | Código de Tipo de Fluido 2 |
| `observaciones_recomendaciones` | TextField | Observaciones y Recomendaciones |
| `comentarios_recap` | TextField | Comentarios del Intervalo para Recap; Hasta 10,000 caracteres. |
| `cerrado` | BooleanField | (0027) Intervalo cerrado (se bajó el revestidor). No se crea otro mientras haya uno abierto. Solo cambia con los botones Cerrar / Reabrir (excluido del formulario) |
| `created_at` | DateTimeField |  |
| `updated_at` | DateTimeField |  |

### TipoFosa — Tipo de Fosa

Tabla: `operaciones_tipofosa` · Migración: `0003_wellheaderinfo_fosa_intervalorevestimiento_tipofosa` · Único por: (pozo, codigo) · Orden: `codigo`

> 'Pit Type Setup' — catálogo de tipos de fosa por pozo (clonable desde plantilla). Por defecto se siembran los 7 tipos estándar de ONE-TRAX; se pueden agregar tipos adicionales (ej: Base Oil, Brine).

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `codigo` | PositiveSmallIntegerField | # |
| `descripcion` | CharField(100) | Descripción |

### Fosa — Fosa / Tanque

Tabla: `operaciones_fosa` · Migración: `0003_wellheaderinfo_fosa_intervalorevestimiento_tipofosa` · Único por: (pozo, numero) · Orden: `numero`

> 'Pits and Tanks Information' — fosas/tanques físicos del sistema de lodo del pozo. El nombre es solo descriptivo; el uso real diario lo determina el TipoFosa elegido en Volume Accounting.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `numero` | PositiveSmallIntegerField | N° de Fosa |
| `descripcion` | CharField(100) | Descripción |
| `capacidad` | DecimalField(12,2) | Capacidad; por defecto `0` |

### AlmacenCodigo — Código de Almacén

Tabla: `operaciones_almacencodigo` · Migración: `0004_alter_fosa_options_alter_tipofosa_options_and_more` · Único por: (pozo, codigo) · Orden: `codigo`

> 'Warehouse Code Setup' — catálogo de almacenes/bodegas usados en el proyecto (pozo). Se pueden agregar en cualquier momento; no trae datos precargados, el usuario los define.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `codigo` | CharField(15) | Código |
| `nombre` | CharField(100) | Nombre del Almacén |

### TipoDistribucionTiempo — Tipo de Distribución de Tiempo

Tabla: `operaciones_tipodistribuciontiempo` · Migración: `0004_alter_fosa_options_alter_tipofosa_options_and_more` · Único por: (pozo, numero) · Orden: `numero`

> 'Time Distribution Setup' — catálogo de categorías que describen la actividad del taladro durante un período de 24h. Se siembra con el catálogo estándar de ONE-TRAX al crear el pozo; se puede editar y ampliar libremente después desde Configuración General.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `numero` | PositiveIntegerField | Número |
| `descripcion` | CharField(120) | Descripción |
| `tipo` | CharField(5) | Tipo; por defecto `'DF'`; opciones: `DF`, `CF`, `DF/CF` |

### Equipo — Equipo (Catálogo Maestro)

Tabla: `operaciones_equipo` · Migración: `0005_equipo_mallazaranda_productoactivopozo_and_more` · Orden: `codigo`

> Catálogo maestro global de equipos ('Master Equipment List').

| Campo | Tipo | Detalles |
|---|---|---|
| `codigo` | CharField(30) | Código de Equipo; único |
| `nombre` | CharField(150) | Nombre Oficial; Nombre oficial del equipo (equivalente a 'Equip. Detail' de ONE-TRAX); no debería modificarse al usarlo en un pozo. |
| `tipo_equipo` | CharField(25) | Tipo de Equipo; por defecto `'OTROS'`; opciones: `CENTRIFUGA`, `LIMPIADOR_LODO`, `ZARANDA`, `SECADOR_RECORTES`, `SISTEMA_VACIO`, `CONTENEDOR_RECORTES`, `OTROS`; Agrupa el equipo para 'Equipment Properties Setup' (Centrífuga, Mud Cleaner, Shale Shaker, etc.). |
| `posiciones_malla` | PositiveSmallIntegerField | Posiciones de Malla; por defecto `0`; Cuántas mallas lleva el equipo (0 = no usa mallas; máximo 12). Ej.: zaranda BEM 3 = 3, BEM 600 = 5. La posición 1 es la más cercana a la línea de flujo. |

### MallaZaranda — Malla de Zaranda (Catálogo Maestro)

Tabla: `operaciones_mallazaranda` · Migración: `0005_equipo_mallazaranda_productoactivopozo_and_more` · Orden: `mesh_size, codigo`

> Catálogo maestro global de mallas de zaranda ('Master Screen List').

| Campo | Tipo | Detalles |
|---|---|---|
| `codigo` | CharField(30) | Código de Malla; único |
| `descripcion` | CharField(150) | Descripción |
| `mesh_size` | PositiveSmallIntegerField | Tamaño de Malla (Mesh) |

### ComponenteSarta — Componente de Sarta (Catálogo Maestro)

Tabla: `operaciones_componentesarta` · Migración: `0014_componentesarta_tramosarta_riser_pilothole` · Orden: `tipo, -od_in, codigo`

> Catálogo maestro global de componentes de sarta ('Master Drill String Component List'). Cada fila es un componente físico con sus diámetros característicos: una mecha de 12¼", un drill collar 8½" x 3", una tubería de perforación 5" x 4.276" con junta 6.375" x 3.75". Al elegirlo en la tabla de Sarta del reporte diario, los diámetros se autocompletan pero quedan editables.

| Campo | Tipo | Detalles |
|---|---|---|
| `codigo` | CharField(30) | Código del Componente; único |
| `descripcion` | CharField(150) | Descripción |
| `tipo` | CharField(20) | Tipo de Componente; por defecto `'DRILL_PIPE'`; opciones: `MECHA`, `MOTOR`, `DRILL_COLLAR`, `HEAVY_WEIGHT`, `DRILL_PIPE`, `ESTABILIZADOR`, `CROSSOVER`, `REVESTIDOR`, `OTROS` |
| `od_in` | DecimalField(8,4) | Diámetro Externo — OD (in) |
| `id_in` | DecimalField(8,4) | Diámetro Interno — ID (in); por defecto `0`; 0 para componentes macizos o para la mecha. |
| `tool_joint_od_in` | DecimalField(8,4) | OD de Junta (in); opcional (null) |
| `tool_joint_id_in` | DecimalField(8,4) | ID de Junta (in); opcional (null) |
| `tool_joint_length_in` | DecimalField(8,2) | Largo de Junta (in); opcional (null); Largo de la junta por tramo, en pulgadas (ONE-TRAX usa 21 in por tramo de 31 ft). |
| `largo_tramo_ft` | DecimalField(8,2) | Largo de Tramo (ft); por defecto `31.0`; Largo nominal de un tramo (joint). Se usa para ponderar el efecto de la junta. |

### ProductoActivoPozo — Producto Activo del Pozo

Tabla: `operaciones_productoactivopozo` · Migración: `0005_equipo_mallazaranda_productoactivopozo_and_more` · Orden: `producto__codigo`

> 'Active Product List' — productos del catálogo maestro seleccionados para este pozo, con sus datos propios del proyecto (precio, código de costo diario, etc.). Se permite más de una fila para el mismo producto maestro (ej. mismo código con dos abreviaciones distintas), igual que en ONE-TRAX 1.5.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `producto` | ForeignKey | Producto (Catálogo Maestro); → **Producto** (on_delete PROTECT) |
| `abreviatura` | CharField(30) | Abreviación |
| `unit_size` | DecimalField(12,2) | Tamaño de Unidad; opcional (null) |
| `unidad` | CharField(30) | Unidad |
| `empaque` | CharField(30) | Empaque |
| `precio` | DecimalField(14,2) | Precio; opcional (null) |
| `gravedad_especifica` | DecimalField(8,4) | Gravedad Específica; opcional (null) |
| `calcular_concentracion` | BooleanField | ¿Calcular Concentración?; por defecto `True` |
| `es_producto_mi` | BooleanField | ¿Producto propio? (columna "¿Propio?"; nombre interno heredado); por defecto `True` |
| `grupo_producto` | PositiveSmallIntegerField | Grupo de Producto; por defecto `1` |
| `codigo_costo_diario` | PositiveSmallIntegerField | Código de Costo Diario; por defecto `1` |
| `calcular_wmgt_conc` | BooleanField | ¿Calcular Conc. WMgt?; por defecto `True` |
| `categoria_costo_wmgt` | PositiveSmallIntegerField | Categoría de Costo WMgt; por defecto `1` |
| `categoria_costo_cf` | PositiveSmallIntegerField | Categoría de Costo CF; por defecto `1` |

### EquipoActivoPozo — Equipo Activo del Pozo

Tabla: `operaciones_equipoactivopozo` · Migración: `0005_equipo_mallazaranda_productoactivopozo_and_more` · Único por: (pozo, numero_serie) · Orden: `equipo__codigo, numero_serie`

> 'Active Equipment List' — equipos seleccionados para este pozo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `equipo` | ForeignKey | Equipo (Catálogo Maestro); → **Equipo** (on_delete PROTECT) |
| `numero_serie` | CharField(30) | N° de Serie |
| `descripcion` | CharField(150) | Descripción; Editable para necesidades de reporte; el nombre oficial vive en el Equipo maestro. |
| `precio_renta` | DecimalField(12,2) | Precio de Renta; por defecto `0` |
| `precio_standby` | DecimalField(12,2) | Precio Stand-By; por defecto `0` |

### MallaActivaPozo — Malla Activa del Pozo

Tabla: `operaciones_mallaactivapozo` · Migración: `0005_equipo_mallazaranda_productoactivopozo_and_more` · Único por: (pozo, malla) · Orden: `malla__mesh_size`

> 'Active Screen List' — mallas de zaranda seleccionadas para este pozo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `malla` | ForeignKey | Malla (Catálogo Maestro); → **MallaZaranda** (on_delete PROTECT) |
| `precio` | DecimalField(12,2) | Precio; por defecto `0` |
| `descuento_porcentaje` | DecimalField(5,2) | Descuento (%); por defecto `0` |

### PropiedadEquipoTipo — Propiedad de Equipo (Catálogo Maestro)

Tabla: `operaciones_propiedadequipotipo` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more` · Único por: (tipo_equipo, descripcion) · Orden: `tipo_equipo, orden, descripcion`

> Catálogo maestro global (editable) de propiedades disponibles por Tipo de Equipo (ej: para Centrífuga: Flow Rate, WT In, Bowl Speed...). Es la lista que aparece pre-cargada en ONE-TRAX; aquí el ingeniero puede agregar, modificar o eliminar propiedades libremente.

| Campo | Tipo | Detalles |
|---|---|---|
| `tipo_equipo` | CharField(25) | Tipo de Equipo; opciones: `CENTRIFUGA`, `LIMPIADOR_LODO`, `ZARANDA`, `SECADOR_RECORTES`, `SISTEMA_VACIO`, `CONTENEDOR_RECORTES`, `OTROS` |
| `descripcion` | CharField(100) | Descripción de la Propiedad |
| `unidad` | CharField(30) | Unidad |
| `orden` | PositiveIntegerField | Orden; por defecto `1` |

### EquipoPropiedadSeleccionada — Propiedad de Equipo Seleccionada

Tabla: `operaciones_equipopropiedadseleccionada` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more` · Único por: (pozo, propiedad) · Orden: `tipo_equipo, propiedad__orden`

> Propiedades estándar seleccionadas (checkbox) para un pozo, por tipo de equipo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `tipo_equipo` | CharField(25) | Tipo de Equipo; opciones: `CENTRIFUGA`, `LIMPIADOR_LODO`, `ZARANDA`, `SECADOR_RECORTES`, `SISTEMA_VACIO`, `CONTENEDOR_RECORTES`, `OTROS` |
| `propiedad` | ForeignKey | Propiedad; → **PropiedadEquipoTipo** (on_delete PROTECT) |

### EquipoPropiedadExtra — Propiedad de Equipo Extra

Tabla: `operaciones_equipopropiedadextra` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more` · Orden: `tipo_equipo, descripcion`

> Propiedades adicionales de texto libre capturadas para un pozo, por tipo de equipo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `tipo_equipo` | CharField(25) | Tipo de Equipo; opciones: `CENTRIFUGA`, `LIMPIADOR_LODO`, `ZARANDA`, `SECADOR_RECORTES`, `SISTEMA_VACIO`, `CONTENEDOR_RECORTES`, `OTROS` |
| `descripcion` | CharField(100) | Descripción |
| `unidad` | CharField(30) | Unidad |

### CentrifugaUnidadConfig — Configuración de Unidades de Centrífuga

Tabla: `operaciones_centrifugaunidadconfig` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more`

> 'Centrifuge Flexible Units Selection' — configuración de unidades, una por pozo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | OneToOneField | → **Pozo** (on_delete CASCADE); único |
| `unidad_flow_rate` | CharField(15) | Unidad de Flow Rate; por defecto `'gal/min'`; opciones: `gal/min`, `bbl/min`, `bbl/hr`, `L/min`, `m3/hr` |
| `unidad_mass` | CharField(10) | Unidad de Mass; por defecto `'Ton'`; opciones: `Ton`, `lb`, `kg`, `bbl` |

### ParametroBenchmark — Parámetro de Benchmark (Catálogo Maestro)

Tabla: `operaciones_parametrobenchmark` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more` · Único por: (grupo, descripcion, tipo_fluido) · Orden: `grupo, descripcion`

> Catálogo maestro global (editable) de parámetros disponibles para Benchmark Setup (ej: Mud Weight(WBM), PV(WBM), YP(OBM)...).

| Campo | Tipo | Detalles |
|---|---|---|
| `grupo` | CharField(60) | Grupo; Categoría para agrupar en la lista de selección (ej: 'Mud Properties'). |
| `descripcion` | CharField(100) | Descripción |
| `unidad` | CharField(30) | Unidad |
| `tipo_fluido` | CharField(5) | Tipo de Fluido; por defecto `'NA'`; opciones: `WBM`, `OBM`, `AMBOS`, `NA` |
| `tipo_dato` | CharField(10) | Tipo de Dato; por defecto `'MIN_MAX'`; opciones: `NUMERICO`, `MIN_MAX`, `TEXTO` |

### BenchmarkSeleccionado — Benchmark Seleccionado

Tabla: `operaciones_benchmarkseleccionado` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more` · Único por: (pozo, parametro) · Orden: `parametro__grupo, parametro__descripcion`

> 'Benchmark Definitions' — parámetros elegidos para monitorear en este pozo.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `parametro` | ForeignKey | Parámetro; → **ParametroBenchmark** (on_delete PROTECT) |

### BenchmarkTarget — Objetivo de Benchmark

Tabla: `operaciones_benchmarktarget` · Migración: `0006_equipo_tipo_equipo_centrifugaunidadconfig_and_more` · Único por: (pozo, parametro, intervalo, min_max) · Orden: `parametro__grupo, parametro__descripcion, min_max`

> 'Target Entry' — valores objetivo por parámetro, por sección (Whole Well o Intervalo).

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `parametro` | ForeignKey | Parámetro; → **ParametroBenchmark** (on_delete PROTECT) |
| `intervalo` | ForeignKey | Intervalo; → **IntervaloRevestimiento** (on_delete CASCADE); opcional (null); Vacío = 'Whole Well' (todo el pozo). |
| `min_max` | CharField(5) | Min/Max; por defecto `'VALOR'`; opciones: `VALOR`, `MIN`, `MAX` |
| `valor` | CharField(50) | Valor |

## Reporte diario, pestañas 1 a 5 y 7 (`models_daily_reports.py`)

### ReporteDiario — Reporte Diario

Tabla: `operaciones_reportediario` · Migración: `0007_plantillaextralabels_plantillaextralabelitem_and_more` · Único por: (pozo, fecha) · Orden: `-fecha`

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `fecha` | DateField | Fecha del Reporte |
| `tipo_lodo` | CharField(20) | Tipo de Lodo (Mud Check Type); por defecto `'WBM'`; opciones: `WBM`, `WBM_CACL2`, `OBM`, `SBM` |
| `profundidad_actual` | FloatField | Profundidad (Depth); por defecto `0.0` |
| `profundidad_tvd` | FloatField | Profundidad TVD; por defecto `0.0` |
| `bit_depth` | FloatField | Profundidad de Mecha (Bit Depth); por defecto `0.0`; Disparador principal de la geometría. |
| `actividad_actual` | CharField(255) | Actividad (Present Activity) |
| `tipo_fluido_display` | CharField(150) | Nombre Comercial del Fluido (Fluid Type) |
| `litologia` | CharField(150) | Litología |
| `operador_representante` | CharField(150) | Representante del Operador |
| `contratista_representante` | CharField(150) | Representante del Contratista |
| `mi_representante_1` | CharField(150) | Ingeniero M-I SWACO 1 |
| `mi_representante_2` | CharField(150) | Ingeniero M-I SWACO 2 |
| `telefono_taladro` | CharField(100) | Teléfono del Taladro |
| `telefono_almacen` | CharField(100) | Teléfono del Almacén |
| `telefonos` | CharField(255) | Otros Teléfonos |
| `fax_numbers` | CharField(255) | Pagers/FAX |
| `intervalo_costo` | ForeignKey | Intervalo de Costo (Interval Number); → **IntervaloRevestimiento** (on_delete SET_NULL); opcional (null); Intervalo del pozo al que se imputan los costos del día. |
| `orden_impresion_intervalo` | PositiveSmallIntegerField | Orden de Impresión (Print Order); opcional (null) |
| `pilot_hole_size_in` | FloatField | Diámetro del Hoyo Piloto (in); por defecto `0.0` |
| `pilot_hole_depth_ft` | FloatField | Profundidad del Hoyo Piloto (ft); por defecto `0.0` |
| `kickoff_sidetrack_ft` | FloatField | (0022) Profundidad de Kick-off del Side Track (ft); por defecto `0.0`; solo el día en que arranca el side track: el hoyo perforado se cuenta desde aquí |
| `creado_en` | DateTimeField |  |
| `actualizado_en` | DateTimeField |  |

### PropiedadExtraFluido — Propiedad Extra de Fluido

Tabla: `operaciones_propiedadextrafluido` · Migración: `0007_plantillaextralabels_plantillaextralabelitem_and_more` · Único por: (pozo, tipo_fluido, numero) · Orden: `tipo_fluido, numero`

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `tipo_fluido` | CharField(5) | opciones: `WBM`, `OBM` |
| `numero` | PositiveIntegerField | Numero de propiedad del 1 al 60 |
| `etiqueta` | CharField(100) | Etiqueta (Label) |
| `unidad` | CharField(50) | Unidad (Unit) |
| `orden_impresion` | PositiveIntegerField | Print Order; por defecto `0`; Orden de impresion en reportes. 0 = oculto. |

### PlantillaExtraLabels — Plantilla de Extra Labels

Tabla: `operaciones_plantillaextralabels` · Migración: `0007_plantillaextralabels_plantillaextralabelitem_and_more` · Orden: `nombre`

> Plantilla predefinida de Extra Report Labels (ej. Statoil, Custom).

| Campo | Tipo | Detalles |
|---|---|---|
| `nombre` | CharField(100) | Nombre de la Plantilla; único |
| `descripcion` | CharField(255) |  |
| `creado_en` | DateTimeField |  |

### PlantillaExtraLabelItem — Item de Plantilla Extra Labels

Tabla: `operaciones_plantillaextralabelitem` · Migración: `0007_plantillaextralabels_plantillaextralabelitem_and_more` · Único por: (plantilla, tipo_fluido, numero) · Orden: `tipo_fluido, numero`

> Cada etiqueta individual dentro de una plantilla predefinida.

| Campo | Tipo | Detalles |
|---|---|---|
| `plantilla` | ForeignKey | → **PlantillaExtraLabels** (on_delete CASCADE) |
| `tipo_fluido` | CharField(5) | opciones: `WBM`, `OBM` |
| `numero` | PositiveIntegerField |  |
| `etiqueta` | CharField(100) |  |
| `unidad` | CharField(50) |  |

### WellSurveyStation — Estación de Well Survey

Tabla: `operaciones_wellsurveystation` · Migración: `0008_wellsurveystation` · Orden: `md_ft, estacion`

> Estaciones de trayectoria direccional del pozo (Well Survey). Registra MD, Inclinación, Azimut y calcula automáticamente TVD, DLS y Sección Vertical.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `estacion` | PositiveIntegerField | N° de Estación; por defecto `1` |
| `md_ft` | FloatField | Profundidad Medida - MD (ft); por defecto `0.0` |
| `inclinacion_deg` | FloatField | Inclinación (°); por defecto `0.0` |
| `azimut_deg` | FloatField | Azimut (°); por defecto `0.0` |
| `tvd_ft` | FloatField | Profundidad Vertical Verdadera - TVD (ft); por defecto `0.0` |
| `dls_deg_100ft` | FloatField | Dogleg Severity (°/100ft); por defecto `0.0` |
| `seccion_vertical_ft` | FloatField | Sección Vertical (ft); por defecto `0.0` |
| `comentarios` | CharField(150) | Comentarios |
| `fecha_registro` | DateTimeField |  |

### WellFormationTop — Tope de Formación y Litología

Tabla: `operaciones_wellformationtop` · Migración: `0009_wellformationtop` · Orden: `depth_ft, id`

> Topes de formación y litología por pozo (Lithology Setup). Columnas exactas de ONE-TRAX: Depth (ft), Formation Top, Lithology, % Sand.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `depth_ft` | FloatField | Depth (ft); por defecto `0.0` |
| `formation_top` | CharField(150) | Formation Top |
| `lithology` | CharField(150) | Lithology |
| `porcentaje_arena` | FloatField | % Sand; por defecto `0.0` |
| `fecha_registro` | DateTimeField |  |

### ReporteDiarioBomba — Bomba de Reporte Diario

Tabla: `operaciones_reportediariobomba` · Migración: `0010_reportediariobitdata_reportediarioboquilla_and_more` · Único por: (reporte, numero_bomba) · Orden: `numero_bomba`

> Bombas de lodo del taladro registradas en el reporte diario (Tab #2 - Pumps / Bits).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `numero_bomba` | PositiveIntegerField | N° Bomba; por defecto `1` |
| `make_model` | CharField(100) | Make and Model |
| `liner_diameter` | FloatField | Liner Diameter (in); por defecto `6.5` |
| `stroke_length` | FloatField | Stroke Length (in); por defecto `12.0` |
| `rod_diam_duplex` | FloatField | Rod Diam Duplex Only (in); opcional (null); por defecto `0.0` |
| `eficiencia_pct` | FloatField | Eff %; por defecto `97.0` |
| `pump_rate_spm` | FloatField | Pump Rate (spm); por defecto `0.0` |
| `pump_on_report` | BooleanField | Pump On Report; por defecto `True` |
| `riser_pump` | BooleanField | Riser Pump; por defecto `False` |

### ReporteDiarioBitData — Datos de Barrena y Perforación

Tabla: `operaciones_reportediariobitdata` · Migración: `0010_reportediariobitdata_reportediarioboquilla_and_more`

> Datos de barrena, parámetros de perforación, presiones hidráulicas y datos de ECD (Tab #2 - Pumps / Bits).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | OneToOneField | → **ReporteDiario** (on_delete CASCADE); único |
| `bit_description` | CharField(150) | Bit Description; por defecto `'Hycalog X-175'` |
| `bit_number` | CharField(50) | Bit Number; por defecto `'1'` |
| `washout_pct` | FloatField | % Washout; por defecto `0.0` |
| `bit_size` | FloatField | Bit Size / Hole Diameter (in); por defecto `12.25` |
| `washout_hole_size` | FloatField | Washout Hole Size (in); por defecto `12.25` |
| `bit_serial_no` | CharField(100) | Serial Number |
| `bit_iadc_code` | CharField(50) | IADC Code |
| `bit_manufacturer` | CharField(100) | Manufacturer |
| `rotary_rpm` | FloatField | Rotary RPM; por defecto `0.0` |
| `rotating_hours` | FloatField | Rotating Hours; por defecto `0.0` |
| `weight_on_bit` | FloatField | Weight on Bit (lbs); por defecto `0.0` |
| `rop` | FloatField | ROP (ft/hr); por defecto `0.0` |
| `riser_pump_flow_rate` | FloatField | Riser Pump Flow Rate (gpm); por defecto `0.0` |
| `pump_flow_rate` | FloatField | Pump Flow Rate (gpm); por defecto `0.0` |
| `pump_pressure` | FloatField | Pump Pressure (psi); por defecto `0.0` |
| `dp_mwd` | FloatField | dP MWD (psi); por defecto `0.0` |
| `dp_motor` | FloatField | dP Motor (psi); por defecto `0.0` |
| `motor_rpm` | FloatField | Motor RPM; por defecto `0.0` |
| `surface_code` | CharField(20) | Surface Code (1-5); por defecto `'1'` |
| `surface_pressure` | FloatField | Surface Pressure (psi); por defecto `0.0` |
| `ref_flow_rate` | FloatField | Ref. Flow Rate (gal/min); por defecto `0.0` |
| `on_off_bottom_pressure` | FloatField | On/Off Bottom (psi); por defecto `0.0` |

### ReporteDiarioBoquilla — Boquilla de Barrena

Tabla: `operaciones_reportediarioboquilla` · Migración: `0010_reportediariobitdata_reportediarioboquilla_and_more` · Orden: `-size_32nds, id`

> Boquillas (jets/nozzles) instaladas en la barrena para el cálculo de TFA.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `size_32nds` | PositiveIntegerField | Size (32nds of inch); por defecto `14` |
| `cantidad` | PositiveIntegerField | Quantity; por defecto `1` |

### ReporteDiarioMudConfig — Configuración de Lodo y Sólidos

Tabla: `operaciones_reportediariomudconfig` · Migración: `0011_reportediariomudcheck_reportediariomudconfig_and_more`

> Configuración global de propiedades de lodo y análisis de sólidos para el reporte diario (Tab #3).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | OneToOneField | → **ReporteDiario** (on_delete CASCADE); único |
| `solids_equation` | CharField(20) | Current Solids Analysis Equations; por defecto `'API'`; opciones: `API` (0026; antes `M-I`). No cambia ningún cálculo |
| `is_weighted` | BooleanField | Weighted Mud; por defecto `True` |
| `sg_base_oil` | FloatField | Base Oil S.G.; por defecto `0.84` |
| `sg_weight_material` | FloatField | Weight Material S.G.; por defecto `4.2` |
| `sg_drill_solids` | FloatField | Drill Solids S.G.; por defecto `2.6` |
| `obm_salt_type` | CharField(10) | Internal Phase Salt; por defecto `'CaCl2'`; opciones: `CaCl2`, `NaCl` |
| `creado_en` | DateTimeField |  |
| `actualizado_en` | DateTimeField |  |

### ReporteDiarioMudCheck — Chequeo de Lodo (Mud Check)

Tabla: `operaciones_reportediariomudcheck` · Migración: `0011_reportediariomudcheck_reportediariomudconfig_and_more` · Único por: (reporte, check_number) · Orden: `check_number`

> Chequeos diarios de lodo (Tab #3 - Mud Properties). Permite hasta 4 chequeos diarios (#1 Primary, #2, #3, #4) en orden cronológico inverso.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `check_number` | PositiveIntegerField | N° Chequeo (1-4); por defecto `1` |
| `is_primary` | BooleanField | Primary Check; por defecto `False` |
| `sample_from` | CharField(50) | Sample From; por defecto `'In'` |
| `time_taken` | CharField(20) | Time Taken; por defecto `'09:00'` |
| `flowline_temp` | FloatField | Flow Line Temp (°F); opcional (null) |
| `depth` | FloatField | Depth (ft); opcional (null) |
| `tvd` | FloatField | TVD (ft); opcional (null) |
| `mud_weight` | FloatField | Mud Weight (lb/gal); opcional (null) |
| `mw_temp` | FloatField | MW Temp (°F); opcional (null) |
| `funnel_viscosity` | FloatField | Funnel Viscosity (s/qt); opcional (null) |
| `rheology_temp` | FloatField | Rheology Temp (°F); opcional (null); por defecto `120.0` |
| `r600` | FloatField | R600; opcional (null) |
| `r300` | FloatField | R300; opcional (null) |
| `r200` | FloatField | R200; opcional (null) |
| `r100` | FloatField | R100; opcional (null) |
| `r6` | FloatField | R6; opcional (null) |
| `r3` | FloatField | R3; opcional (null) |
| `pv` | FloatField | PV (cP); opcional (null) |
| `yp` | FloatField | YP (lb/100ft²); opcional (null) |
| `gel_10s` | FloatField | 10s Gel (lb/100ft²); opcional (null) |
| `gel_10m` | FloatField | 10m Gel (lb/100ft²); opcional (null) |
| `gel_30m` | FloatField | 30m Gel (lb/100ft²); opcional (null) |
| `api_fluid_loss` | FloatField | API Fluid Loss (cc/30min); opcional (null) |
| `hthp_fluid_loss` | FloatField | HPHT Fluid Loss (cc/30min); opcional (null) |
| `cake_api` | FloatField | Cake API (1/32 in); opcional (null) |
| `cake_hthp` | FloatField | Cake HPHT (1/32 in); opcional (null) |
| `solids_pct` | FloatField | Solids (%Vol); opcional (null) |
| `oil_pct` | FloatField | Oil (%Vol); opcional (null) |
| `water_pct` | FloatField | Water (%Vol); opcional (null) |
| `sand_pct` | FloatField | Sand (%Vol); opcional (null) |
| `retort_mud_weight` | FloatField | Retort Mud Wt (lb/gal); opcional (null) |
| `retort_mud_temp` | FloatField | Retort Mud Temp (°F); opcional (null); por defecto `75.0` |
| `k_from_kcl` | FloatField | K+ From KCl (mg/l); opcional (null); por defecto `0.0` |
| `wt_additive_sg` | FloatField | Wt Additive SG; opcional (null); por defecto `4.2` |
| `oil_sg` | FloatField | Oil SG; opcional (null); por defecto `0.7` |
| `frac_bent` | FloatField | Frac Bent (Activity Ratio); opcional (null); por defecto `0.1111` |
| `chem_conc` | FloatField | Chem Conc (lb/bbl); opcional (null); por defecto `0.0` |
| `drill_solids_sg` | FloatField | Drill Solids SG; opcional (null); por defecto `2.6` |
| `nacl_pct` | FloatField | NaCl (%Vol); opcional (null) |
| `nacl_ppb` | FloatField | NaCl (lb/bbl); opcional (null) |
| `kcl_pct` | FloatField | KCl (%Vol); opcional (null) |
| `kcl_ppb` | FloatField | KCl (lb/bbl); opcional (null) |
| `lgs_pct` | FloatField | LGS (%Vol); opcional (null) |
| `lgs_ppb` | FloatField | LGS (lb/bbl); opcional (null) |
| `bentonite_pct` | FloatField | Bentonite (%Vol); opcional (null) |
| `bentonite_ppb` | FloatField | Bentonite (lb/bbl); opcional (null) |
| `drill_solids_pct` | FloatField | Drill Solids (%Vol); opcional (null) |
| `drill_solids_ppb` | FloatField | Drill Solids (lb/bbl); opcional (null) |
| `hgs_pct` | FloatField | HGS (%Vol); opcional (null) |
| `hgs_ppb` | FloatField | HGS (lb/bbl); opcional (null) |
| `salt_pct_wt` | FloatField | Salt (%wt); opcional (null) |
| `salt_ppb` | FloatField | Salt (lb/bbl); opcional (null) |
| `adjusted_solids_pct` | FloatField | Adjusted Solids (%Vol); opcional (null) |
| `oil_water_ratio` | CharField(20) | Oil/Water Ratio; por defecto `''` |
| `avg_sg_solids` | FloatField | Avg SG Solids; opcional (null) |
| `ph` | FloatField | pH; opcional (null) |
| `ph_temp` | FloatField | pH Temp (°F); opcional (null) |
| `pm` | FloatField | Pm; opcional (null) |
| `pf` | FloatField | Pf; opcional (null) |
| `mf` | FloatField | Mf; opcional (null) |
| `chlorides` | FloatField | Chlorides (mg/L); opcional (null) |
| `calcium_hardness` | FloatField | Hardness Ca++ (mg/L); opcional (null) |
| `mbt` | FloatField | MBT (lb/bbl); opcional (null) |
| `electrical_stability` | FloatField | Electrical Stability (V); opcional (null) |
| `excess_lime` | FloatField | Excess Lime (lb/bbl); opcional (null) |
| `creado_en` | DateTimeField |  |
| `actualizado_en` | DateTimeField |  |

### TramoSarta — Tramo de Sarta de Perforación

Tabla: `operaciones_tramosarta` · Migración: `0014_componentesarta_tramosarta_riser_pilothole` · Único por: (reporte, orden) · Orden: `orden, id`

> Un componente de la sarta de perforación instalado en el hoyo en la fecha del reporte (Tab #4 - Well Geometry, tabla 'Drill String'). Las filas se ordenan DESDE LA MECHA HACIA ARRIBA (orden=1 es la mecha), que es como el ingeniero arma físicamente el ensamblaje. Cada tramo aporta un volumen interno (su propio ID) y un volumen anular (su OD contra el diámetro que lo confina, que lo da el perfil del pozo).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `orden` | PositiveSmallIntegerField | Orden (1 = mecha); por defecto `1`; Posición desde la mecha hacia superficie. |
| `componente` | ForeignKey | Componente del Catálogo; → **ComponenteSarta** (on_delete SET_NULL); opcional (null); Opcional: al elegirlo se autocompletan los diámetros, que siguen siendo editables. |
| `descripcion` | CharField(150) | Descripción / Tipo |
| `longitud_ft` | FloatField | Longitud (ft); por defecto `0.0` |
| `od_in` | FloatField | Diámetro Externo — OD (in); por defecto `0.0` |
| `id_in` | FloatField | Diámetro Interno — ID (in); por defecto `0.0` |
| `tool_joint_od_in` | FloatField | OD de Junta (in); por defecto `0.0` |
| `tool_joint_id_in` | FloatField | ID de Junta (in); por defecto `0.0` |
| `tool_joint_length_in` | FloatField | Largo de Junta (in); por defecto `0.0` |
| `largo_tramo_ft` | FloatField | Largo de Tramo (ft); por defecto `31.0` |

### ReporteDiarioComentarios — Comentarios del Reporte Diario

Tabla: `operaciones_reportediariocomentarios` · Migración: `0015_reportediariocomentarios`

> Comentarios del día (Tab #5 - Comments). Tres bloques de texto con destinos distintos, más la especificación de propiedades del lodo (el rango objetivo acordado con el operador, no el valor medido del día: eso vive en los Mud Checks de la pestaña 3).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | OneToOneField | → **ReporteDiario** (on_delete CASCADE); único |
| `spec_mud_weight` | CharField(50) | Peso del Lodo — Especificación; Rango objetivo acordado, por ejemplo 11.5-12.0 |
| `spec_viscosidad` | CharField(50) | Viscosidad — Especificación |
| `spec_filtrado` | CharField(50) | Filtrado — Especificación; Rango objetivo acordado, por ejemplo 3.0-5.0 |
| `mud_recap_remarks` | TextField | Resumen del Día (Mud Recap Remarks); Una sola línea: es lo que se imprime en el Well Recap del pozo (y en el recap diario del reporte final). |
| `remarks_and_treatment` | TextField | Observaciones y Tratamiento; Actividad y servicio de fluidos prestado durante el día. |
| `remarks` | TextField | Observaciones de Operaciones; Operaciones generales del taladro; normalmente se toma de la hoja IADC. |
| `creado_en` | DateTimeField |  |
| `actualizado_en` | DateTimeField |  |

### ReporteDiarioMudExtraValue — Valor de Propiedad Extra de Lodo

Tabla: `operaciones_reportediariomudextravalue` · Migración: `0011_reportediariomudcheck_reportediariomudconfig_and_more` · Único por: (mud_check, propiedad_extra)

> Valor de una propiedad extra (definida en PropiedadExtraFluido del pozo) para un chequeo específico.

| Campo | Tipo | Detalles |
|---|---|---|
| `mud_check` | ForeignKey | → **ReporteDiarioMudCheck** (on_delete CASCADE) |
| `propiedad_extra` | ForeignKey | → **PropiedadExtraFluido** (on_delete CASCADE) |
| `valor` | CharField(100) | Valor; por defecto `''` |

### ReporteDiarioTiempo — Distribución de Tiempo del Reporte

Tabla: `operaciones_reportediariotiempo` · Migración: `0016_distribucion_tiempo`

> Distribución de Tiempo del día (Tab #7 - Time Distribution). Guarda cuántas horas cubre el período del reporte. Casi siempre son 24, pero hay días que no: el primer día del pozo (se empezó a perforar a mitad del período), el último (se liberó el taladro) o cuando la operadora cambia la hora de corte. Por eso el total de horas se compara contra este valor y no contra 24 fijo.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | OneToOneField | → **ReporteDiario** (on_delete CASCADE); único |
| `horas_periodo` | DecimalField(5,2) | Horas del Período; por defecto `24`; 24 por defecto. Se cambia solo en días especiales (inicio, fin o cambio de hora de corte). |
| `creado_en` | DateTimeField |  |
| `actualizado_en` | DateTimeField |  |

### ReporteDiarioActividadTiempo — Actividad de Distribución de Tiempo

Tabla: `operaciones_reportediarioactividadtiempo` · Migración: `0016_distribucion_tiempo` · Único por: (reporte, tipo_numero) · Orden: `orden, id`

> Horas dedicadas a una actividad del taladro durante el período del reporte. La actividad sale del catálogo 'Time Distribution Setup' del pozo (TipoDistribucionTiempo), pero se guarda por NÚMERO y con una copia de la descripción, no con una llave foránea: ese catálogo se guarda reemplazando todas sus filas.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `orden` | PositiveSmallIntegerField | Orden; por defecto `0` |
| `tipo_numero` | PositiveIntegerField | Número de Actividad (catálogo del pozo) |
| `descripcion` | CharField(120) | Actividad |
| `horas` | DecimalField(5,2) | Horas; por defecto `0` |

## Pestaña 6 — Control de sólidos (`models_control_solidos.py`)

### TipoTicketMalla — Tipo de Ticket de Mallas

Tabla: `operaciones_tipoticketmalla` · Migración: `0017_control_solidos_mallas` · Único por: (pozo, nombre) · Orden: `sentido, nombre`

> Tipos de ticket de mallas del pozo (catálogo editable). El usuario todavía no sabe qué tipos maneja AOS, así que se siembran ejemplos y se pueden renombrar, agregar o quitar desde la pantalla de tickets. Lo único que importa para el cálculo es el sentido: si el ticket ENTRA mallas al pozo o las SACA.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `nombre` | CharField(80) | Tipo de Ticket |
| `sentido` | CharField(8) | Sentido; por defecto `'ENTRADA'`; opciones: `ENTRADA`, `SALIDA` |

### TicketMalla — Ticket de Mallas

Tabla: `operaciones_ticketmalla` · Migración: `0017_control_solidos_mallas` · Orden: `id`

> Ticket de entrega o devolución de mallas (ONE-TRAX: Transfer Ticket Transactions).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `tipo` | ForeignKey | Tipo; → **TipoTicketMalla** (on_delete RESTRICT) |
| `numero` | CharField(40) | N° de Ticket |
| `pedido_por` | CharField(100) | Pedido por |
| `recibido_por` | CharField(100) | Recibido por |
| `almacen_codigo` | CharField(15) | Código de Almacén |
| `almacen_nombre` | CharField(100) | Almacén |
| `creado_en` | DateTimeField |  |
| `actualizado_en` | DateTimeField |  |

### TicketMallaDetalle — Detalle de Ticket de Mallas

Tabla: `operaciones_ticketmalladetalle` · Migración: `0017_control_solidos_mallas` · Único por: (ticket, malla) · Orden: `malla__mesh_size, malla__codigo`

> Cantidades de una malla en un ticket. Se guarda lo que dice el papel ("según ticket") y lo que llegó o salió de verdad ("real"); el inventario usa siempre lo real.

| Campo | Tipo | Detalles |
|---|---|---|
| `ticket` | ForeignKey | → **TicketMalla** (on_delete CASCADE) |
| `malla` | ForeignKey | → **MallaZaranda** (on_delete PROTECT) |
| `nuevas_ticket` | PositiveIntegerField | Nuevas según ticket; por defecto `0` |
| `nuevas_real` | PositiveIntegerField | Nuevas reales; por defecto `0` |
| `usadas_ticket` | PositiveIntegerField | Usadas según ticket; por defecto `0` |
| `usadas_real` | PositiveIntegerField | Usadas reales; por defecto `0` |

### TransaccionMalla — Transacción de Malla

Tabla: `operaciones_transaccionmalla` · Migración: `0017_control_solidos_mallas` · Orden: `secuencia`

> Movimiento de una malla en los equipos (ONE-TRAX: Shaker Screen Transactions). 'secuencia' crece con cada transacción del pozo: la última registrada es la única que se puede deshacer (igual que 'Undo Last Transaction' de ONE-TRAX).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `secuencia` | PositiveIntegerField | N° de Transacción |
| `accion` | CharField(20) | Acción; opciones: `INSTALAR_NUEVA`, `INSTALAR_USADA`, `A_ALMACEN`, `DESECHAR_EQUIPO`, `DESECHAR_ALMACEN` |
| `malla` | ForeignKey | → **MallaZaranda** (on_delete PROTECT) |
| `equipo` | ForeignKey | → **Equipo** (on_delete PROTECT); opcional (null) |
| `equipo_serie` | CharField(30) | N° de Serie del Equipo |
| `equipo_descripcion` | CharField(150) | Equipo |
| `posicion` | PositiveSmallIntegerField | Posición; opcional (null) |
| `precio_unitario` | DecimalField(12,2) | Precio Unitario (neto); por defecto `0`; Solo en 'Instalar malla nueva': precio neto de la malla en ese momento. |
| `creado_en` | DateTimeField |  |

### UsoEquipoDia — Uso Diario de Equipo

Tabla: `operaciones_usoequipodia` · Migración: `0018_uso_equipos` · Único por: (reporte, equipo_serie) · Orden: `tipo_equipo, equipo_serie`

> Lo que hizo un equipo del pozo en el día: rendimiento, costo de renta y paradas. Solo se guardan los datos que captura el ingeniero; los volúmenes descargados, el lodo perdido en los sólidos y todos los acumulados se CALCULAN (control_solidos.py), porque dependen de la profundidad y del diámetro del hoyo, que pueden corregirse después en las pestañas 1 y 2.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `equipo` | ForeignKey | → **Equipo** (on_delete PROTECT) |
| `equipo_serie` | CharField(30) | N° de Serie |
| `equipo_descripcion` | CharField(150) | Equipo |
| `tipo_equipo` | CharField(25) | Tipo de Equipo |
| `horas` | DecimalField(5,2) | Horas en operación; opcional (null) |
| `mud_on_cuttings` | DecimalField(8,3) | Lodo en recortes (bbl/bbl); opcional (null); Volumen de lodo que sale pegado a cada volumen de recortes descargados. |
| `porcentaje_recortes` | DecimalField(5,2) | % de recortes; opcional (null); Qué parte del hoyo perforado en el día descarga este equipo (100 % = todo). |
| `tipo_perdida_codigo` | PositiveSmallIntegerField | Tipo de pérdida (código); opcional (null) |
| `tipo_perdida_descripcion` | CharField(100) | Tipo de pérdida |
| `caudal_entrada_gpm` | DecimalField(8,2) | Caudal de entrada (gpm); opcional (null) |
| `densidad_entrada` | DecimalField(6,3) | Densidad de entrada (lb/gal); opcional (null) |
| `densidad_salida` | DecimalField(6,3) | Densidad de salida (lb/gal); opcional (null) |
| `densidad_descarte` | DecimalField(6,3) | Densidad de descarte (lb/gal); opcional (null) |
| `cantidad_usada` | DecimalField(8,2) | Cantidad usada; por defecto `0` |
| `codigo_cobro` | CharField(10) | Código de cobro; por defecto `'COMPLETO'`; opciones: `COMPLETO`, `STANDBY`, `SIN_COBRO` |
| `tarifa` | DecimalField(12,2) | Tarifa aplicada; por defecto `0`; Copia de la tarifa del pozo (renta o stand-by) el día que se registró. |
| `es_fluidos` | BooleanField | ¿Equipo de fluidos de perforación?; por defecto `False` |
| `horas_parada` | DecimalField(5,2) | Horas de parada; opcional (null) |
| `observaciones` | TextField | Observaciones de uso |

### UsoEquipoPropiedad — Propiedad Diaria de Equipo

Tabla: `operaciones_usoequipopropiedad` · Migración: `0018_uso_equipos` · Orden: `orden, id`

> Valor del día de una propiedad adicional del equipo (las definidas en Equipment Properties Setup: ángulo de la canasta, fuerza G, velocidad del tazón, etc.). Se guarda por descripción: esa configuración también se guarda recreando filas.

| Campo | Tipo | Detalles |
|---|---|---|
| `uso` | ForeignKey | → **UsoEquipoDia** (on_delete CASCADE) |
| `orden` | PositiveSmallIntegerField | por defecto `0` |
| `descripcion` | CharField(100) | Propiedad |
| `unidad` | CharField(30) | Unidad |
| `valor` | CharField(60) | Valor |

## Pestaña 8 — Volumetría e inventario (`models_inventario.py`)

### PerdidaReportePozo — Pérdida Mostrada en el Reporte

Tabla: `operaciones_perdidareportepozo` · Migración: `0019_perdidas_reporte` · Único por: (pozo, codigo) · Orden: `orden, codigo`

> Categorías de pérdida que se muestran en el reporte diario (máximo 10), en orden. El pozo puede tener hasta 20 categorías (Configuración de Pérdidas), pero el reporte diario solo imprime 10. La selección es POR POZO (decisión del usuario) y se guarda por CÓDIGO de categoría. Si el pozo no tiene selección guardada, se usan las 10 primeras.

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | ForeignKey | → **Pozo** (on_delete CASCADE) |
| `codigo` | PositiveSmallIntegerField | Código de la categoría de pérdida |
| `orden` | PositiveSmallIntegerField | Orden en el reporte; por defecto `0` |

### VolumenFosaDia — Volumen Diario de Fosa

Tabla: `operaciones_volumenfosadia` · Migración: `0020_volumetria` · Único por: (reporte, fosa_numero) · Orden: `fosa_numero`

> Datos del día de una fosa: el tipo con que se usó (activa, reserva, premezcla...) y lo que el ingeniero MIDIÓ al cierre. El volumen calculado no se guarda: sale de los movimientos. El manual insiste: el volumen real no se cambia para cuadrar el balance.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `fosa_numero` | PositiveSmallIntegerField | N° de Fosa |
| `fosa_descripcion` | CharField(100) | Fosa |
| `capacidad` | DecimalField(12,2) | Capacidad (bbl); por defecto `0` |
| `tipo_codigo` | PositiveSmallIntegerField | Tipo de fosa (código); opcional (null) |
| `tipo_descripcion` | CharField(100) | Tipo de fosa |
| `volumen_final` | DecimalField(12,2) | Volumen final real (bbl); opcional (null) |
| `peso_fluido` | DecimalField(6,2) | Peso del fluido (lb/gal); opcional (null) |
| `temperatura` | DecimalField(6,1) | Temperatura (°F); opcional (null) |

### VolumenHoyoDia — Volumen del Hoyo del Día

Tabla: `operaciones_volumenhoyodia` · Migración: `0020_volumetria`

> Volumen del hoyo que NO ocupa el fluido del sistema activo (Volume Not Fluids). Se usa el día del abandono en un side track.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | OneToOneField | → **ReporteDiario** (on_delete CASCADE); único |
| `no_fluido_anular` | DecimalField(12,2) | No fluido — anular (bbl); por defecto `0` |
| `no_fluido_sarta` | DecimalField(12,2) | No fluido — sarta (bbl); por defecto `0` |
| `no_fluido_bajo_mecha` | DecimalField(12,2) | No fluido — bajo la mecha (bbl); por defecto `0` |

### TransaccionVolumen — Movimiento de Volumetría

Tabla: `operaciones_transaccionvolumen` · Migración: `0020_volumetria` · Orden: `secuencia`

> Movimiento de fluido o de productos (Add Chemicals, Add Whole Mud, Transfer/Loss). 'secuencia' crece por pozo: solo la última se puede deshacer (Undo Last Transaction).

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `secuencia` | PositiveIntegerField | N° de Movimiento |
| `tipo` | CharField(15) | Tipo; opciones: `QUIMICOS`, `LODO_ENTERO`, `TRANSFERENCIA`, `DEVOLUCION`, `PERDIDA` |
| `fosa_numero` | PositiveSmallIntegerField | Fosa |
| `fosa_descripcion` | CharField(100) |  |
| `destino_numero` | PositiveSmallIntegerField | Fosa destino; opcional (null) |
| `destino_descripcion` | CharField(100) |  |
| `volumen_bbl` | DecimalField(12,2) | Volumen (bbl); por defecto `0` |
| `aceite_bbl` | DecimalField(12,2) | Fluido base agregado (bbl); por defecto `0` |
| `agua_bbl` | DecimalField(12,2) | Agua agregada (bbl); por defecto `0` |
| `peso_lodo` | DecimalField(6,2) | Peso del lodo (lb/gal); opcional (null) |
| `lodo_producto` | ForeignKey | → **Producto** (on_delete PROTECT); opcional (null) |
| `lodo_producto_texto` | CharField(255) |  |
| `lodo_cantidad` | DecimalField(12,3) | Cantidad consumida; por defecto `0` |
| `lodo_precio` | DecimalField(14,2) | por defecto `0` |
| `lodo_categoria` | PositiveSmallIntegerField | por defecto `1` |
| `lodo_stock_aplicado` | DecimalField(12,3) | (0022_inventario_unificado) Unidades del producto de lodo entero que este movimiento restó de `Producto.cantidad` |
| `origen_destino` | CharField(120) | Recibido de / Devuelto a |
| `perdida_codigo` | PositiveSmallIntegerField | Tipo de pérdida (código); opcional (null) |
| `perdida_descripcion` | CharField(100) |  |
| `creado_en` | DateTimeField |  |

### TransaccionVolumenProducto — Producto de Movimiento de Volumetría

Tabla: `operaciones_transaccionvolumenproducto` · Migración: `0020_volumetria` · Orden: `id`

> Producto de un movimiento. En 'Agregar químicos' es la CANTIDAD agregada (en la unidad del producto); en 'Agregar lodo entero' es la CONCENTRACIÓN del lodo (lb/bbl), que solo sirve para el cálculo de concentraciones. Guarda copia de los datos del producto.

| Campo | Tipo | Detalles |
|---|---|---|
| `transaccion` | ForeignKey | → **TransaccionVolumen** (on_delete CASCADE) |
| `producto` | ForeignKey | → **Producto** (on_delete PROTECT) |
| `descripcion` | CharField(255) |  |
| `cantidad` | DecimalField(12,3) | por defecto `0` |
| `es_concentracion` | BooleanField | por defecto `False` |
| `unidad` | CharField(30) |  |
| `tamano` | DecimalField(12,3) | por defecto `0` |
| `gravedad` | DecimalField(8,4) | por defecto `0` |
| `precio` | DecimalField(14,2) | por defecto `0` |
| `categoria_costo` | PositiveSmallIntegerField | por defecto `1` |
| `calcula_concentracion` | BooleanField | por defecto `True` |
| `stock_aplicado` | DecimalField(12,3) | (0022_inventario_unificado) Cantidad que este movimiento restó de `Producto.cantidad` (0 en concentraciones y servicios) |

### InventarioProductoDia — Inventario Diario de Producto

Tabla: `operaciones_inventarioproductodia` · Migración: `0020_volumetria` · Único por: (reporte, producto)

> Columnas del inventario que el ingeniero llena a mano: uso en otro módulo (personal de servicio, por ejemplo días de ingeniero), ajuste, cantidad pedida y "no imprimir".

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `producto` | ForeignKey | → **Producto** (on_delete PROTECT) |
| `usado_otro` | DecimalField(12,3) | Usado en otro módulo; por defecto `0` |
| `ajuste` | DecimalField(12,3) | Ajuste (+ suma / − resta); por defecto `0` |
| `en_pedido` | DecimalField(12,3) | En pedido; por defecto `0` |
| `no_imprimir` | BooleanField | No imprimir; por defecto `False` |
| `precio` | DecimalField(14,2) | Precio aplicado; por defecto `0` |
| `categoria_costo` | PositiveSmallIntegerField | por defecto `1` |
| `stock_aplicado` | DecimalField(12,3) | (0022_inventario_unificado) Neto (usado en otro módulo − ajuste) ya aplicado a `Producto.cantidad` |

### TicketProducto — Ticket de Productos

Tabla: `operaciones_ticketproducto` · Migración: `0020_volumetria` · Orden: `id`

> Ticket de entrega o devolución de productos. Usa los mismos tipos de ticket que las mallas.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `tipo` | ForeignKey | → **TipoTicketMalla** (on_delete RESTRICT) |
| `numero` | CharField(40) |  |
| `pedido_por` | CharField(100) |  |
| `recibido_por` | CharField(100) |  |
| `almacen_codigo` | CharField(15) |  |
| `almacen_nombre` | CharField(100) |  |
| `creado_en` | DateTimeField |  |

### TicketProductoDetalle — Detalle de Ticket de Productos

Tabla: `operaciones_ticketproductodetalle` · Migración: `0020_volumetria` · Único por: (ticket, producto)

| Campo | Tipo | Detalles |
|---|---|---|
| `ticket` | ForeignKey | → **TicketProducto** (on_delete CASCADE) |
| `producto` | ForeignKey | → **Producto** (on_delete PROTECT) |
| `cantidad_ticket` | DecimalField(12,3) | Según ticket; por defecto `0` |
| `cantidad_real` | DecimalField(12,3) | Real; por defecto `0` |

## Módulos opcionales (`models_opcionales.py`)

### ObservacionesIFE — Observaciones IFE

Tabla: `operaciones_observacionesife` · Migración: `0021_modulos_opcionales`

> Los cuatro textos "IFE Remarks" de la pantalla principal de Solids Equipment.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | OneToOneField | → **ReporteDiario** (on_delete CASCADE); único |
| `fluidos_resumen` | TextField | Fluidos de perforación — resumen |
| `fluidos_plan` | TextField | Fluidos de perforación — plan siguiente |
| `solidos_resumen` | TextField | Control de sólidos — resumen |
| `solidos_plan` | TextField | Control de sólidos — plan siguiente |

### AnalisisSolidosEquipo — Análisis de Sólidos por Equipo

Tabla: `operaciones_analisissolidosequipo` · Migración: `0021_modulos_opcionales` · Orden: `orden, id`

> Análisis de sólidos de una muestra tomada en un equipo (Equipment Solids Analysis).

| Campo | Tipo | Detalles |
|---|---|---|
| `equipo_serie` | CharField(30) | N° de Serie |
| `equipo_descripcion` | CharField(150) | Equipo |
| `hora_inicio` | CharField(5) | Hora de inicio |
| `hora_fin` | CharField(5) | Hora de fin |
| `orden` | PositiveSmallIntegerField | Orden de impresión; por defecto `1` |
| `profundidad_ft` | FloatField | Profundidad medida (ft); opcional (null) |
| `profundidad_perforada_ft` | FloatField | Profundidad perforada representada (ft); opcional (null) |
| `comentarios` | CharField(255) | Comentarios |
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `tipo_lodo` | CharField(3) | por defecto `'WBM'`; opciones: `WBM`, `OBM` |
| `tipo_muestra` | CharField(60) | Tipo de muestra (ej. descarga) |
| `datos` | JSONField | Datos de la muestra; por defecto `dict` |

### RetencionRecortes — Retención en Recortes

Tabla: `operaciones_retencionrecortes` · Migración: `0021_modulos_opcionales` · Orden: `orden, id`

> Prueba de retención de fluido en recortes (Cuttings Retention).

| Campo | Tipo | Detalles |
|---|---|---|
| `equipo_serie` | CharField(30) | N° de Serie |
| `equipo_descripcion` | CharField(150) | Equipo |
| `hora_inicio` | CharField(5) | Hora de inicio |
| `hora_fin` | CharField(5) | Hora de fin |
| `orden` | PositiveSmallIntegerField | Orden de impresión; por defecto `1` |
| `profundidad_ft` | FloatField | Profundidad medida (ft); opcional (null) |
| `profundidad_perforada_ft` | FloatField | Profundidad perforada representada (ft); opcional (null) |
| `comentarios` | CharField(255) | Comentarios |
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `diametro_mecha_in` | FloatField | Diámetro de mecha (in); opcional (null) |
| `datos` | JSONField | Datos de la prueba; por defecto `dict` |

### EventoNoProgramado — Evento No Programado

Tabla: `operaciones_eventonoprogramado` · Migración: `0021_modulos_opcionales` · Orden: `id`

> Evento no programado del pozo (Unscheduled Events), registrado en un reporte.

| Campo | Tipo | Detalles |
|---|---|---|
| `reporte` | ForeignKey | → **ReporteDiario** (on_delete CASCADE) |
| `categoria` | CharField(10) | por defecto `'FLUIDOS'`; opciones: `FLUIDOS`, `CALIDAD`, `LOGISTICA`, `EQUIPO` |
| `tipo_problema` | CharField(100) | Tipo de problema |
| `tipo_fluido` | CharField(100) | Tipo de fluido |
| `descripcion` | TextField | Descripción |
| `causa` | TextField | Causa sospechada |
| `descripcion_perdida` | TextField | Descripción de la pérdida |
| `horas_perdidas` | FloatField | Tiempo perdido (h); opcional (null) |
| `volumen_perdido_bbl` | FloatField | Volumen perdido (bbl); opcional (null) |
| `costo` | FloatField | Costo estimado; opcional (null) |

## Reporte final (`models_recap.py`)

### RecapPozo — Reporte Final del Pozo

Tabla: `operaciones_recappozo` · Migración: `0023_recap_pozo`

> Textos que escribe el ingeniero al cierre del pozo. Los números del reporte final **no se guardan**: salen de los reportes diarios (`recap_pozo.py`).

| Campo | Tipo | Detalles |
|---|---|---|
| `pozo` | OneToOneField | → **Pozo** (on_delete CASCADE); related_name `recap` |
| `resumen` | TextField | Resumen del pozo |
| `conclusiones` | TextField | Conclusiones |
| `recomendaciones` | TextField | Recomendaciones |
| `lecciones` | TextField | Lecciones aprendidas / buenas prácticas |
| `actualizado_en` | DateTimeField | auto_now |

## Cambios del 27-sep-2026

- `ReporteDiario.kickoff_sidetrack_ft` y tipo `SIDETRACK` de intervalo (0022_sidetrack). Ver [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md).
- `RecapPozo` (0023_recap_pozo).
- Del compañero: campos `stock_aplicado` / `lodo_stock_aplicado` (0022_inventario_unificado): el reporte diario descuenta y devuelve `Producto.cantidad`. Los datos viejos se marcaron como "ya aplicados" (la cantidad del Inventario se toma como correcta).
- `0024_merge` une ambas ramas.

## Cambios del 02-oct-2026

- Migraciones **0025** (compañero), **0026** y **0027**: ver el historial arriba y [22](22_CAMBIOS_02OCT_SMART_MUD.md).
- `Pozo.MONEDAS_COMUNES`: lista de 18 monedas para los selectores (no es un campo; `moneda_simbolo` acepta otro código).
