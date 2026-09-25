# Pestaña 1 — General

Datos de operación del día, representantes y resumen de costos. Es la pestaña que se abre por defecto.

| | |
|---|---|
| Plantilla | `templates/operaciones/avances_19_sep/reporte_diario_detalle.html` |
| Vista | `views_daily_reports.api_reporte_diario_general_guardar` |
| Modelo | `ReporteDiario` |
| API | `POST /api/pozos/<pk>/reportes-diarios/<reporte_pk>/general/guardar/` |

## Bloques de la pantalla

### Parámetros de operación

| Campo | Modelo | Notas |
|---|---|---|
| Fecha | `fecha` | Se puede cambiar (ver advertencia abajo) |
| Fecha Spud | `WellHeaderInfo.spud_date` | Solo lectura; viene de Información General del Pozo |
| Reporte N° | `numero_reporte` | Calculado: cantidad de reportes del pozo hasta esta fecha |
| Actividad | `actividad_actual` | Texto libre |
| Profundidad (ft) | `profundidad_actual` | Profundidad medida del hoyo. Decimales permitidos (20.5) |
| TVD (ft) | `profundidad_tvd` | |
| Prof. Barrena (ft) | `bit_depth` | **Dispara la geometría de la pestaña 4** |
| Tipo de Fluido | `tipo_fluido_display` | Nombre comercial del fluido |
| Litología | `litologia` | Con sugerencias de los topes de formación del pozo |

Botones del bloque:

- **Configuración de Litología**: topes de formación del pozo (profundidad, formación, litología, % arena). Se guardan por pozo, reemplazando la lista.
- **Registro Direccional (Survey)**: estaciones MD / inclinación / azimut. Al guardar, el servidor recalcula TVD, DLS y sección vertical por **curvatura mínima** (`calcular_survey_curvatura_minima`). Estas estaciones las usa la hidráulica para convertir MD en TVD.

### Personal de guardia

Representantes del operador, contratista y dos de M-I SWACO, teléfonos del taladro, del almacén y otros.

Cuando se crea un reporte:

- si hay reporte anterior y se eligió copiar datos, se heredan profundidad, TVD, mecha, actividad, fluido, litología, representantes y teléfonos;
- si es el primer reporte, los representantes se toman de Información General del Pozo (ingeniero de proyecto, contratista, ingenieros M-I 1 y 2).

### Balance económico de fluidos y equipos

Tabla de solo lectura con costo **diario** y **acumulado** en seis columnas, igual que el reporte ONE-TRAX. Se llena con `GET .../cost-overview/` (`views_inventario.resumen_costos`):

| Columna | Qué suma |
|---|---|
| Químicos / Personal DF | Productos con categoría de costo 1 (químicos) y 2 (ingeniero de fluidos) de la pestaña 8 |
| Ingeniero de Fluidos (IFE / control de sólidos) | Categorías 3 y 4 de la pestaña 8 |
| Total Perforación | Suma de las dos anteriores |
| Equipos / Mallas | Renta de equipos y mallas nuevas instaladas (pestaña 6) |
| Otros Costos (DWM/CF) | Siempre 0 (sin módulo) |
| TOTAL | Todo |

Si la línea de tiempo de volumetría o de mallas tiene un error, esa parte del costo sale en 0 hasta corregirlo.

## Guardado

Todos los campos se envían juntos. Los números vacíos o no válidos conservan el valor anterior.

## Advertencias

- Cambiar la **fecha** mueve el reporte en la línea de tiempo del pozo. El sistema rechaza una fecha que ya tenga otro reporte y revalida mallas (pestaña 6) y volumetría (pestaña 8); si algún día deja de cuadrar, no guarda y dice por qué.
- La profundidad de la mecha es la base de los volúmenes: si queda en 0, la pestaña 4 avisa y los volúmenes del hoyo salen vacíos.

## Barra de navegación del reporte

En la parte superior de todas las pestañas: ir al primer, anterior, siguiente y último reporte, saltar a cualquier fecha y **descargar el Excel** (`GET .../excel/`).
