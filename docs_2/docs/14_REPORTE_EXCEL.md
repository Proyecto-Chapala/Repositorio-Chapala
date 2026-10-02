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
| **Lodo Base Agua / Lodo CALDRIL / Lodo Base Aceite / Lodo Base Sintetica** | *Solo queda una*, según el tipo del reporte: WBM → Base Agua, WBM_CACL2 → CALDRIL, OBM → Base Aceite, SBM → Base Sintética. Encabezado, sarta y revestidor, volúmenes y circulación (el **avance del día** toma en cuenta side track y ampliación de piloto), bombas y mecha, hasta 4 chequeos de lodo con propiedades extra 1-8, productos usados y equipos con sus mallas ("4X170"), especificación y comentarios, distribución de tiempo (10 filas), contabilidad de volumen y pérdidas (hasta 10), análisis de sólidos del chequeo principal, reología e hidráulica, costos diarios y acumulados, contactos |
| **Prop Extra Base Agua / Prop Extra Aceite-Sint** | Solo queda la del tipo de fluido. Propiedades extra 9-60 con orden de impresión > 0 |
| **Contabilidad de Volumen** | Fosas (capacidad, peso, volumen con 1 decimal, clase), suma por grupo, lodo en el hoyo (total, no fluido, fluido), balance por grupo (activo, reserva, premezcla), transferencias entre grupos y desglose de pérdidas. **Balance, hoyo y pérdidas sin decimales**, como se reporta en campo (formato *Mud Volume Accounting*) |
| **Concentraciones** | *Nueva (27-sep).* Formato del reporte "Sistema Activo" de ONE-TRAX. Un bloque por compartimento (primero el sistema activo, luego cada fosa, cada uno en su página): encabezado del pozo, volúmenes del día en bbl y m³ (fluido base, agua, aumento por material, lodo entero, volumen inicial, final y cambio) y por producto: tamaño, cantidad agregada, concentración inicial/cambio/final en **lb/bbl y kg/m³**, con total. Ver [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) |
| **Inv Quimico (DF)** | Inventario de productos con movimiento, sin los marcados *No imprimir*, ordenado por código |
| **Inv Quimico (por nombre)** | La misma lista, ordenada por descripción |
| **Inv Quimico (completo)** | Todos los productos activos o con movimiento, incluidos los *No imprimir* |
| **Equipos** | Hasta 36 equipos: horas, rendimiento, cobro, tarifa y costo |
| **Inventario de Mallas** | Existencias nuevas/usadas, instaladas y costo por malla |

### Hojas de inventario químico

- Hasta **3 páginas de 50 productos** cada una (filas 11-60, 71-120, 131-180).
- Columnas: descripción, tamaño/unidad, precio, inicial, usado día y acumulado, recibido día y acumulado, devuelto día y acumulado, final y costo del día. Para los **servicios** se dejan vacíos inicial y final.
- En el encabezado van el costo del día, el **impuesto** (`costo × tasa_impuesto`) y el costo acumulado.
- El área de impresión se ajusta a las páginas usadas, pero **la plantilla trae dibujadas las 3 páginas**. Al abrir el archivo en Excel se ven encabezados repetidos y vacíos debajo de los datos (ver abajo).

## Por qué aparecen hojas o páginas "repetidas y sin datos"

Es el bug 3 de la lista del usuario. No viene de otros pozos: el Excel **siempre es de un solo pozo y un solo reporte**. Las causas son:

1. **Tres hojas de inventario químico con los mismos datos** en distinto orden o filtro (DF, por nombre, completo). Así lo hace ONE-TRAX.
2. **Páginas 2 y 3 de cada hoja de inventario** (y bloques equivalentes en otras hojas) vienen **pre-dibujadas** en la plantilla. Si hay menos de 50 productos, quedan con su encabezado y sin filas. El área de impresión sí se recorta (`A1:M60`), así que **al imprimir no salen**, pero en pantalla se ven.
3. **Hojas sin información ese día**: por ejemplo, *Equipos* o *Inventario de Mallas* si no hubo uso. Salen igual, solo con el encabezado.

Posibles mejoras (no implementadas): borrar las filas de las páginas no usadas, eliminar las hojas vacías o dejar que el usuario elija qué hojas descargar. Ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).

## Formato de números

`_t()` y `_g()` escriben los números **con coma decimal**, como los imprime ONE-TRAX en español (6,5 · 12 · 0,25). Los campos numéricos puros se escriben como número.

## Hidráulica en el Excel

Usa la edición configurada en el pozo (*Configuración General → Usar API 5ª edición*). **Ojo**: la pantalla abre por defecto en la 5ª, pero el ajuste del pozo por defecto está desactivado (4ª). Si la pantalla y el Excel no coinciden, revisa ese ajuste.

## Errores

Si falla la geometría o la hidráulica, el Excel **se genera igual** con esas secciones vacías. Los errores se capturan en silencio.
