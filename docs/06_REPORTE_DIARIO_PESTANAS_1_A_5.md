# 06 — Reporte diario: hub y pestañas 1 a 5

> Pestaña 4: las etiquetas del bloque *Contexto del pozo* (ej. **Orden de Impresión**) se muestran completas desde el 02-oct-2026.

Archivos principales: `views_daily_reports.py`, `models_daily_reports.py`, `templates/operaciones/avances_19_sep/daily_reports_hub.html` y `reporte_diario_detalle.html`. Las pestañas 1 a 5 tienen su JS en línea dentro de la plantilla del reporte.

## 1. Hub "Fluidos de Perforación y Equipos"

Ruta: `/pozos/<id>/drilling-fluids-equipment/` (alias `/daily-reports/`).

| Zona | Función |
|---|---|
| **Historial de reportes diarios** | Tabla cronológica con fecha, profundidad, actividad y tipo de lodo. Solo botón **Abrir** |
| **+ Nuevo Reporte** | Abre el modal de creación |
| **Etiquetas de propiedades extra** | Propiedades extra del lodo del pozo por tipo (WBM y OBM/SBF): etiqueta y unidad (1 a 8). **Bloqueadas** (solo lectura); el botón **Modificar etiquetas** las habilita y al guardar se vuelven a bloquear |

> **Página bloqueada (02-oct-2026, pedido de AOS):** el hub solo sirve para **crear** el reporte del día y **abrir** los anteriores. Se quitaron *Editar*, *Eliminar*, la X de cada fila, el *modo de eliminación*, el selector "Reporte Diario Especial", la barra de plantillas predefinidas y el botón de etiquetas 9–60 (no hacían nada).

### Crear un reporte (`api/pozos/<id>/reportes-diarios/crear/`)

| Campo | Regla |
|---|---|
| Fecha | Obligatoria. Atajos **Hoy** y **Fecha Inicio**. **No puede haber dos reportes en la misma fecha** |
| Tipo de fluido | Base Agua (WBM), Base Agua CaCl2 (`WBM_CACL2`), Base Aceite (OBM), Base Sintética (SBM) |
| ¿Copiar datos del día anterior? | **Sí (recomendado)**: copia profundidades, actividad, litología, representantes y teléfonos del reporte con fecha anterior más cercana. **No**: arranca en blanco, con los representantes tomados de la Información General del Pozo |

Aunque no se copien los datos generales, **bombas, barrena, chequeos de lodo, comentarios y tiempo** se heredan del día anterior la primera vez que se abre cada pestaña (patrón *obtener o crear*, ver [02 § D](02_ARQUITECTURA.md)). La sarta se hereda con el botón **"Heredar del día anterior"** de la pestaña 4.

### Número de reporte

No se guarda: es la cantidad de reportes del pozo con fecha menor o igual a la de este. Si se crea un reporte con fecha intermedia o se borra uno, **los números se recalculan**.

### Eliminar un reporte

Desde el 02-oct-2026 **no hay botón en pantalla** (hub bloqueado). La API sigue existiendo y devuelve al inventario general lo consumido: `DELETE api/pozos/<id>/reportes-diarios/<id_reporte>/eliminar/` borra el reporte **y todo su contenido**: tickets, transacciones de mallas y volumetría, usos de equipos, etc. ⚠ No se vuelve a validar la línea de tiempo: si el reporte borrado tenía un ticket de entrada del que dependían días posteriores, esos días quedan con inventario inconsistente, y el error aparecerá la próxima vez que se escriba en ellos.

## 2. Estructura de la pantalla del reporte

- **Encabezado**: fecha, pozo, operador, tipo de lodo, sistema de unidades y número de reporte. Flecha para volver al hub y migas de pan.
- **Barra de 8 pestañas**: `switchTab(n)` muestra el contenedor `tabContent-*` correspondiente.
- Cada pestaña **guarda por separado** con su botón. Excepción: la **pestaña 6 (mallas)** y los **movimientos de la pestaña 8**, que se registran al instante.

| # | Pestaña | Contenedor | Guarda en |
|---|---|---|---|
| 1 | General | `tabContent-general` | `general/guardar/` |
| 2 | Bombas / Barrenas | `tabContent-pumps-bits` | `pumps-bits/guardar/` |
| 3 | Propiedades del lodo | `tabContent-mud-properties` | `mud-properties/guardar/` |
| 4 | Geometría del pozo | `tabContent-well-geometry` | `well-geometry/guardar/` |
| 5 | Comentarios | `tabContent-comentarios` | `comentarios/guardar/` |
| 6 | Control de sólidos | `tabContent-solidos` | ver [07](07_PESTANA_6_CONTROL_SOLIDOS.md) |
| 7 | Distribución de tiempo | `tabContent-tiempo` | ver [08](08_PESTANA_7_DISTRIBUCION_TIEMPO.md) |
| 8 | Inventario / Hidráulica / Concentraciones | `tabContent-inventario` | ver [09](09_PESTANA_8_VOLUMETRIA_INVENTARIO.md) |

## 3. Pestaña 1 — General

### Parámetros de operación
Fecha, **Fecha Spud** (heredada de la Información General del Pozo, solo lectura), N° de reporte, actividad, **profundidad MD (ft)**, **TVD (ft)**, **profundidad de la barrena (ft)**, tipo de fluido y litología. Los valores admiten decimales, por ejemplo 20.5 ft.

Desde aquí se abren dos ventanas que se guardan **por pozo**, no por día:
- **Litología y topes de formación** (*Lithology Setup*): profundidad, tope de formación, litología y % de arena. Alimentan la lista de sugerencias del campo Litología.
- **Registro direccional** (*Well Survey*): estaciones con MD, inclinación y azimut. Al guardar, el servidor calcula **TVD, DLS y sección vertical** por el método de **curvatura mínima** (ver [11](11_CALCULOS_INGENIERIA.md#registro-direccional-curvatura-mínima)). La hidráulica usa esta TVD.

### Personal de guardia
Representantes del operador, del contratista e **ingenieros de fluido 1 y 2** (campos internos `mi_representante_1/2`), teléfonos del taladro y del almacén, otros teléfonos y fax.

### Resumen de costos diarios y acumulados
Tarjeta **"Balance económico de fluidos y equipos"** con las columnas de ONE-TRAX: Químicos/Personal DF, Ingeniero IFE/Control de sólidos, Total perforación, Equipos/Mallas, Otros y Total, en valores del día y acumulados. El botón de detalle abre el modal **Cost Overview** (`cost-overview/`) con el desglose por ítem. Todos los costos salen de `views_inventario.resumen_costos()`. Ver [13](13_COSTOS.md).

## 4. Pestaña 2 — Bombas y barrena

### Bombas de lodo
Hasta **4 bombas**. La primera vez, sin día anterior, se crean con valores de ejemplo: 2 × EMSCO F-1000 de 6,5" × 12" a 80 SPM activas, una tercera inactiva y una cuarta vacía.

| Campo | Uso |
|---|---|
| Marca/modelo | Texto libre con lista de sugerencias: EMSCO, National, Gardner Denver, Ideco, Wirth, Weatherford |
| Diámetro de camisa (in), carrera (in), vástago (dúplex), eficiencia (%) | Desplazamiento por embolada |
| SPM | Caudal |
| ¿En el reporte? (`pump_on_report`) | Solo las bombas activas suman caudal |
| ¿Bomba del riser? | Marca de bomba de riser |

Cálculos (bomba **tríplex**): ver [11 § Bombas](11_CALCULOS_INGENIERIA.md#bombas-y-boquillas).

### Boquillas de la barrena
Pares **tamaño (32avos de pulgada) × cantidad**. El **TFA** (área total de flujo, in²) se calcula en vivo.

### Datos de la barrena y la perforación
Descripción, número, serie, fabricante, código IADC, tamaño de la barrena, **washout (%)** y **diámetro con washout** (el que usa la geometría para el hoyo abierto), RPM, horas rotando, peso sobre la barrena, ROP, caudales (bombas y riser), presión de bomba, ΔP de MWD y motor, RPM del motor y **presión o código de equipo de superficie** (casos 1 a 4 de la hidráulica), caudal de referencia y presión en/fuera de fondo.

## 5. Pestaña 3 — Propiedades del lodo

### Configuración (una por reporte)
Ecuación de sólidos (solo `API` desde el 02-oct; no cambia el cálculo), densificado/no densificado, GE del aceite base, del material densificante y de los sólidos perforados, y tipo de sal en OBM (CaCl2 o NaCl).

### Chequeos de lodo (hasta 4 por día)
Matriz en **orden cronológico inverso**: **#1 = Principal** es el último chequeo del día y es el que usan la hidráulica, el Excel y el benchmark. Grupos de campos:

- **Muestra**: punto de muestra, hora, profundidad, TVD, temperatura en la línea de flujo.
- **Densidad y viscosidad**: densidad y su temperatura, embudo Marsh, temperatura de reología, lecturas **R600, R300, R200, R100, R6, R3**. **PV y YP se calculan** con Bingham (PV = R600 − R300; YP = R300 − PV). Geles de 10 s, 10 min y 30 min.
- **Filtrado y revoque**: API y HPHT.
- **Retorta**: densidad y temperatura, % sólidos, aceite, agua y arena.
- **Análisis de sólidos (calculado)**: KCl, NaCl, **LGS, HGS, bentonita, sólidos perforados** (% y lb/bbl), sal, sólidos ajustados, relación aceite/agua y GE promedio. Ver [11 § Balance de sólidos](11_CALCULOS_INGENIERIA.md#balance-de-sólidos-pestaña-3).
- **Química**: pH y su temperatura, Pm, Pf, Mf, cloruros, dureza cálcica, MBT, estabilidad eléctrica (volts) y exceso de cal.
- **Propiedades extra**: una fila por cada etiqueta definida en el hub, con el valor por chequeo (`ReporteDiarioMudExtraValue`).

## 6. Pestaña 4 — Geometría del pozo

### Sarta de perforación
Tabla ordenada **desde la mecha hacia arriba** (fila 1 = mecha). Por tramo: componente del catálogo maestro (se copian sus diámetros), descripción, **longitud (ft)**, OD, ID, junta (OD, ID, largo en pulgadas) y largo del tramo (ft). Botón **"Heredar del día anterior"**. Al guardar, la sarta **se reemplaza completa**.

### Contexto del pozo
- **Intervalo de costo** del reporte, que se elige entre los intervalos de revestimiento, y su orden de impresión. Muestra el avance planeado contra real (% de longitud).
- **Hoyo piloto**: diámetro y profundidad. Solo se usa si es más profundo que la profundidad actual.
- **Perfil del pozo**: tramos de riser, revestidores, liner y hoyo abierto con su diámetro de confinamiento.

### Volúmenes del hoyo (solo lectura, en vivo)
Equivale a *Daily Casing / Volume* de ONE-TRAX. Por sección: longitud, diámetro, OD/ID, volumen interno (sarta) y anular. Totales: volumen de sarta, anular, **bajo la mecha**, total del hoyo, **desplazamiento de acero**, **fondo arriba** (emboladas y minutos), bbl/embolada y caudal. Muestra avisos si falta información. Fórmulas en [11 § Geometría](11_CALCULOS_INGENIERIA.md#geometría-y-volúmenes-del-hoyo-pestaña-4).

**Diámetro del hoyo abierto**: se toma el de la barrena corregido por washout; si falta, el tamaño de la barrena; si falta, el diámetro de hoyo del intervalo de costo.

## 7. Pestaña 5 — Comentarios

| Bloque | Destino |
|---|---|
| **Especificación de propiedades del lodo** (peso, viscosidad, filtrado) | El **rango objetivo** acordado con el operador (ej. `11.5-12.0`), no el valor medido. Se hereda del día anterior |
| **Resumen del día** (*Mud Recap Remarks*) | Se imprime en el **recap del pozo** |
| **Observaciones y tratamiento** (*Remarks and Treatment*) | Tratamientos aplicados |
| **Observaciones del día** (*Remarks*) | Comentarios generales |

Como referencia se muestra el resumen del reporte anterior. La ventana de **Eventos no programados** quedó **oculta** el 02-oct-2026 (pedido de AOS); ver [12](12_MODULOS_OPCIONALES.md).
