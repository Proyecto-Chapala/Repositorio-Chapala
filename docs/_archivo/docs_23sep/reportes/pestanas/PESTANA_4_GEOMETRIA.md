# Pestaña 4 — Geometría del pozo (Well Geometry)

Sarta de perforación del día, intervalo de costo, hoyo piloto y el cálculo de **volúmenes del hoyo** (la pantalla "Hole Volume Results" de ONE-TRAX, que en ONE-TRAX se abre con el botón *Daily Casing / Volume*).

| | |
|---|---|
| Motor de cálculo | `geometria_pozo.py` (sin Django) |
| Vistas | `views_daily_reports.calcular_geometria_reporte`, `api_well_geometry_detail`, `api_well_geometry_guardar`, `api_sarta_reporte_anterior` |
| Modelos | `TramoSarta`, campos `intervalo_costo`, `orden_impresion_intervalo`, `pilot_hole_*` de `ReporteDiario` |
| Catálogo | `ComponenteSarta` (Catálogos Maestros → Componentes de Sarta) |

## Qué captura el ingeniero

### Intervalo de costo

A qué intervalo de revestimiento se imputan los costos del día y su orden de impresión. La pantalla muestra el **avance del intervalo**: profundidad actual contra longitud planeada (%), días planeados y reales.

### Hoyo piloto

Diámetro y profundidad. Solo cuenta si la profundidad del piloto es mayor que la profundidad del hoyo principal; ocupa el tramo desde el fondo del hoyo principal hasta su propia profundidad.

### Sarta de perforación

Tabla de tramos **desde la mecha hacia arriba**: la fila 1 es la mecha.

| Columna | Notas |
|---|---|
| Componente | Opcional. Al elegirlo del catálogo se **autocompletan** los diámetros, que siguen siendo editables |
| Descripción | Texto |
| Longitud (ft) | |
| OD / ID (in) | Diámetro externo e interno del cuerpo |
| Junta: OD, ID, largo (in) | Solo para tubería de perforación y heavy weight |
| Largo de tramo (ft) | 31 por defecto |

Se guarda **reemplazando** toda la sarta del día. Las filas sin longitud, sin OD y sin descripción se descartan.

**Heredar la sarta de ayer**: botón que trae la sarta del reporte anterior (`GET .../well-geometry/sarta-anterior/`). No se hereda sola.

## Cómo calcula

### 1. Perfil de confinamiento del pozo

`construir_perfil_confinamiento()` arma, de superficie hacia abajo, qué diámetro rodea al fluido a cada profundidad. Fondo del hoyo = el mayor entre profundidad actual, profundidad de la mecha y profundidad del piloto.

Prioridad en cada tramo:

1. **Riser** (si el pozo es offshore y lo usa): manda desde superficie hasta su longitud.
2. **Revestidores**: si hay varios a esa profundidad, manda el de **menor ID** (el más interno). Un revestidor ocupa desde su tope de liner (0 si llega a superficie) hasta su zapata.
3. **Hoyo abierto**: diámetro de la mecha con lavado (pestaña 2); si no hay, el diámetro de hoyo del intervalo de costo. Debajo del fondo principal, el **hoyo piloto** si existe.

### 2. Ubicación de la sarta

`construir_perfil_sarta()` apila los tramos desde la profundidad de la mecha hacia arriba.

### 3. Secciones

`calcular_geometria()` corta el pozo en **cada cambio de confinamiento y en cada cambio de componente**. Por eso una misma tubería de perforación puede salir partida en varias filas: *DP / Riser*, *DP / Revestidor 13-3/8"*, *DP / Hoyo Abierto*.

### Fórmulas

```
Capacidad interna   (bbl/ft) = ID² / 1029.4
Capacidad anular    (bbl/ft) = (D_confinamiento² − OD²) / 1029.4
Desplazamiento      (bbl/ft) = (OD² − ID²) / 1029.4
```

**Corrección por juntas** (tubería de perforación y heavy weight). La junta tiene ID más chico y OD más grande que el cuerpo, así que reduce las dos capacidades. Se pondera por la fracción de longitud que ocupa la junta:

```
f = largo_junta_in / (largo_tramo_ft × 12)
capacidad_efectiva = capacidad_cuerpo × (1 − f) + capacidad_junta × f
```

Con 21" de junta en tramos de 31 ft, f = 0.056452. Esta ponderación reproduce exactamente los valores del ejemplo del pozo **Gusher #2** del manual.

Tramos sin tubería:

- **Sin tubería** (por encima del tope de la sarta): todo el diámetro cuenta como volumen anular.
- **Bajo la mecha** (entre la mecha y el fondo): se acumula aparte como volumen bajo la mecha.

### Totales

| Total | Definición |
|---|---|
| Volumen de la sarta | Σ capacidad interna × longitud |
| Volumen anular | Σ capacidad anular × longitud (incluye tramos sin tubería) |
| Volumen bajo la mecha | Hoyo entre la mecha y el fondo |
| Volumen total del hoyo | Sarta + anular + bajo la mecha |
| Desplazamiento de acero | Σ desplazamiento × longitud |
| Fondo arriba (emboladas) | Volumen anular ÷ bbl/embolada de **la primera bomba activa** |
| Fondo arriba (minutos) | Volumen anular ÷ (caudal total de las bombas activas / 42) |

Las emboladas se cuentan contra una sola bomba porque así las cuenta el perforador; los minutos usan todas las bombas. Esa combinación reproduce los valores del manual.

### Avisos

- "La sarta no llega a la mecha: faltan X ft" o "la sarta excede la profundidad de la mecha" (tolerancia 1 ft).
- "La profundidad de la mecha es 0. Captúrala en la pestaña 1."
- "La mecha está más profunda que el fondo del hoyo registrado."

### Continuidad

La respuesta incluye la fecha, profundidad y mecha del reporte anterior y el **avance del día** (profundidad de hoy − profundidad de ayer).

## Qué usa esta pestaña después

| Resultado | Lo usa |
|---|---|
| Secciones (diámetros, longitudes) | Hidráulica (pestaña 8) |
| Volumen anular, sarta y bajo la mecha | Volumetría (pestaña 8): fluido del sistema activo dentro del hoyo |
| Datos de sarta y revestidor | Excel |

La geometría **no se guarda**: se recalcula cada vez que se abre, para que siempre refleje los datos actuales de las pestañas 1 y 2 y de los intervalos.
