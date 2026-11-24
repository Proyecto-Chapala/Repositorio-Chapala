# 14 — Reporte diario en Excel

Archivos: `reporte_excel.py` (`generar_reporte_excel`), `plantillas/reporte_diario_onetrax.xlsx` y `plantillas/crear_plantilla.py`.
Ruta de descarga: `GET /pozos/<id>/daily-report/<id_reporte>/excel/`. Nombre del archivo: `Reporte_<N°>_<Pozo>_<AAAAMMDD>.xlsx`.

## Cómo se construye

1. **La plantilla** se creó una sola vez con `crear_plantilla.py` a partir del Excel original de ONE-TRAX (*Mud Report 16 PERLA-1X.xlsx*). El script conserva formato, celdas combinadas, anchos y áreas de impresión, **traduce los rótulos al español** y vacía los datos. No hay que volver a correrlo, salvo para rehacer la plantilla.
2. `_datos()` reúne todo lo del reporte con **las mismas funciones que usan las pantallas**: geometría, volumetría, costos, mallas, equipos, hidráulica y propiedades extra. Por eso el Excel y la pantalla muestran los mismos números.
3. Se abre la plantilla, se **eliminan las hojas de lodo** que no corresponden al tipo de fluido del reporte, se llenan las demás, se **crea por código la hoja de Concentraciones** y se agrega el logo en A1 de cada hoja, si existe `static/operaciones/img/logo_reporte.png`.

## Hojas

| Hoja | Contenido |
|---|---|
| **Lodo Base Agua / Lodo CALDRIL / Lodo Base Aceite / Lodo Base Sintetica** | *Solo queda una*, según el tipo del reporte: WBM → Base Agua, WBM_CACL2 → CALDRIL, OBM → Base Aceite, SBM → Base Sintética. Encabezado, sarta y revestidor, volúmenes y circulación (el **avance del día** toma en cuenta side track y ampliación de piloto), bombas y mecha, hasta 4 chequeos de lodo con propiedades extra 1-8, productos usados y equipos con sus mallas ("4X170"), especificación y comentarios, distribución de tiempo (10 filas), contabilidad de volumen y pérdidas (hasta 10), análisis de sólidos del chequeo principal, reología e hidráulica, costos diarios y acumulados (fluidos, C.S. e ingeniería, equipos, **otros (trailer)** y totales: la fila de otros la agrega `_agregar_fila_otros_costos`, que baja TOTALES una fila), contactos |
| **Prop Extra Base Agua / Prop Extra Aceite-Sint** | Solo queda la del tipo de fluido. Propiedades extra 9-60 que tienen orden de impresión **o un valor cargado ese día** (misma regla que la pantalla: `propiedades_extra_del_reporte`) |
| **Contabilidad de Volumen** | Tanques (capacidad, peso, volumen con 1 decimal, clase), suma por grupo, lodo en el hoyo (total, no fluido, fluido), balance por grupo (activo, reserva, premezcla), transferencias entre grupos y desglose de pérdidas. **Balance, hoyo y pérdidas sin decimales**, como se reporta en campo (formato *Mud Volume Accounting*) |
| **Concentraciones** | *Nueva (27-sep).* Formato del reporte "Sistema Activo" de ONE-TRAX. Un bloque por compartimento (primero el sistema activo, luego cada tanque, cada uno en su página): encabezado del pozo, volúmenes del día en bbl y m³ (fluido base, agua, aumento por material, lodo reciclado, volumen inicial, final y cambio) y por producto: tamaño, cantidad agregada, concentración inicial/cambio/final en **lb/bbl y kg/m³**, con total. Ver [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) |
| **Inv Quimico (completo)** | Única hoja de inventario químico: consolida todos los productos asignados y con movimiento en la locación/pozo |
| **Equipos** | Hasta 36 equipos: horas, rendimiento, cobro, tarifa y costo |
| **Inventario de Mallas** | Existencias nuevas/usadas, instaladas y costo por malla |

### Hojas de inventario químico

- Hasta **3 páginas de 50 productos** cada una (filas 11-60, 71-120, 131-180).
- Columnas: descripción, tamaño/unidad, precio, inicial, usado día y acumulado, recibido día y acumulado, devuelto día y acumulado, final y costo del día. Para los **servicios** se dejan vacíos inicial y final.
- En el encabezado van el costo del día, el **impuesto** (`costo × tasa_impuesto`) y el costo acumulado.
- **Solo quedan las páginas usadas** (02-oct-2026): `_quitar_paginas_vacias()` borra las filas, uniones y saltos de página de las páginas 2 y 3 si no hay más de 50 productos. Probado con la plantilla: 1 página al imprimir.

## Hojas de inventario químico y productos usados (actualizado 20-oct-2026)

1. **Hoja única de inventario químico:** se mantiene una sola hoja oficial de inventario, `Inv Quimico (completo)`, eliminando las hojas redundantes o vacías `Inv Quimico (DF)` e `Inv Quimico (por nombre)`.
2. **Productos usados en hoja de lodo (filas 19-33):** se calcula el consumo tomando `max(usado_dia, usado_fluido, agregado_balance)`, asegurando que tanto los agregados en fosa como los anotados a mano en inventario se reporten. Las celdas sobrantes se limpian a `None` para evitar ceros residuales de la plantilla.
3. Las páginas 2 y 3 de inventario sin productos se **borran** (ver arriba).
4. *Equipos* e *Inventario de Mallas* se quitan si ese día no tienen datos.
5. **Rediseño visual y cuadrícula:** pestañas con colores corporativos diferenciados (azul marino `#1E3A8A`, teal `#0D9488`, celeste `#0284C7`, esmeralda `#059669`, púrpura `#7C3AED`, índigo `#4F46E5`) y líneas de división (gridlines) activas en todas las hojas.

## Logo y textos (02-oct-2026)

- **Logo de AOS** (`static/operaciones/img/logo_reporte.png`) en la esquina superior izquierda (`A1`, 45 px de alto) de **todas las hojas**. Requiere **Pillow**; si no está instalado, el Excel sale sin logo (`_pillow_disponible()`).
- `_textos_tanques()` cambia al generar: *Fosas Activas* → **Tanques Activos**, *FOSA* → **TANQUE**, *SUMA DE FOSAS* → **SUMA DE TANQUES**, *Fecha Spud :* → **Fecha Inicial :**. La plantilla `.xlsx` no se modificó.
- El reporte final (`recap_pozo.generar_recap_excel`) también lleva el logo en cada hoja, con el título corrido a la derecha.

## Formato de números

`_t()` y `_g()` escriben los números **con coma decimal**, como los imprime ONE-TRAX en español (6,5 · 12 · 0,25). Los campos numéricos puros se escriben como número.

## Hidráulica en el Excel

Usa la edición configurada en el pozo (*Configuración General → Usar API 5ª edición*). **Ojo**: la pantalla abre por defecto en la 5ª, pero el ajuste del pozo por defecto está desactivado (4ª). Si la pantalla y el Excel no coinciden, revisa ese ajuste.

## Configuración de impresión predeterminada (hoja Carta / Letter)

Todas las hojas de los reportes en Excel (`generar_reporte_excel`, `generar_reporte_propiedades_excel` y `generar_recap_excel`) vienen configuradas de forma predeterminada para impresión:
- **Papel:** Tamaño Carta (`paperSize = 1`, Letter, 8.5" × 11").
- **Ajuste:** `fitToPage = True`, `scale = None`.
- **Ancho:** `fitToWidth = 1` (todo el contenido cabe exactamente en 1 página de ancho sin dividir columnas ni cortar información a la derecha).
- **Alto:**
  - Hojas de una sola página (`Lodo Base Agua/Aceite/CALDRIL/Sintética`, `Prop Extra`, `Contabilidad de Volumen`, `Equipos`, `Inventario de Mallas`): `fitToHeight = 1` (cabe exactamente en 1 página vertical u horizontal según corresponda).
  - Hojas tabulares o por bloques (`Concentraciones`, `Inv Quimico (completo)`, `Reportito de Propiedades`, `Recap del Pozo`): `fitToHeight = 0` (flujo vertical dinámico que respeta los saltos de página por compartimento o bloque de 50 productos).
- **Márgenes:** Estrechos y balanceados (0.3" a 0.4") para aprovechar el área imprimible.
- **Cuadrícula y aspecto visual:** Líneas de división visibles activas (`showGridLines = True`) y colores corporativos elegantes en las pestañas.

## Errores

Si falla la geometría o la hidráulica, el Excel **se genera igual** con esas secciones vacías. Los errores se capturan en silencio.
