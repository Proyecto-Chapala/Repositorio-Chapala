# 18 — Inventario de consumo separado del balance de volumen

**Documento:** [26](../26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md) · **Migración:** 0036 · **Estado:** sin probar

## Cómo funciona

- **Separación de responsabilidades:**
  - *Agregar químicos* (balance de volumen): calcula el volumen de químicos con la gravedad específica (GE) del producto y la masa (lb / (350 × GE)), sumándolo al volumen del tanque y a las concentraciones. **No** descuenta inventario, **no** genera costo y **no** se rechaza por falta de existencia del producto.
  - *Inventario de consumo*: el consumo de lodo del día se escribe a mano en la columna **Usado en fluidos** de la tabla *Inventario diario de productos* (deshabilitada para servicios).
- **Ventana *Agregar químicos*:**
  - Muestra la columna **GE** de cada producto activo.
  - Ya no muestra la columna *Disponible* ni la advertencia roja por pasarse del stock.
  - No muestra "Costo de los productos" en el resumen (solo volumen de químicos y volumen total agregado).
  - La nota del pie aclara que no descuenta inventario y que el consumo se anota en *Inventario de productos*.
- **Tabla de inventario:**
  - La columna *Usado en fluidos* tiene una casilla numérica (`<input>`).
  - Si ese producto se agregó hoy con *Agregar químicos*, muestra debajo en gris un texto de referencia: `Balance: {cantidad}`.
  - Existencia final: `Final = Inicial + Recibido (tickets) − Devuelto (tickets) − Usado en fluidos (a mano) − Usado otro módulo (a mano) ± Ajuste`.
  - Costo diario del producto: `(Usado en fluidos + Usado otro módulo) × precio`.
  - La edición en vivo de *Usado en fluidos* actualiza al instante el *Final*, el *Usado hoy*, el *Costo diario*, el *Acumulado de fluidos* y el resumen de costos.

- **Reportes (Excel diario y Recap):**
  - El Excel diario (`reporte_excel.py`, hoja *Inv Quimico (completo)*) lee directamente las cantidades usadas y costos calculados a partir de las columnas manuales.
  - El Recap del pozo (`recap_pozo.py`, secciones *Productos* y *Costos*) consolida el consumo acumulado y el costo total de químicos basándose en la simulación del inventario.

## Pasos para verificar

- [ ] **Ventana Agregar químicos.** Abrir el modal *Agregar químicos* en un tanque:
  - Aparece la columna **GE** con el valor configurado en productos activos (o "—").
  - Ya no existe la columna *Disponible*.
  - En el resumen abajo solo aparecen *Volumen de químicos* y *Volumen total agregado* (sin costo).
- [ ] **Agregar químicos sin existencia.** Registrar 20 sacos de un producto sin tickets de recepción previos:
  - El movimiento se guarda sin error.
  - El volumen se suma al tanque en la contabilidad de volumen y en las concentraciones.
  - En la tabla de inventario, el producto sigue con sus existencias y costos intactos.
- [ ] **Referencia de balance.** En la tabla de inventario, la celda *Usado en fluidos* de ese producto muestra debajo en texto chico: `Balance: 20`.
- [ ] **Casilla Usado en fluidos.** Escribir un número (por ejemplo 15) en *Usado en fluidos*:
  - La celda *Usado hoy* se actualiza en vivo (15).
  - La existencia final disminuye en 15.
  - El costo diario del producto y el total de la categoría aumentan según `15 × precio`.
  - La columna *Usado en fluidos* del grupo *Acumulado del pozo* aumenta en 15.
- [ ] **Guardar volumetría.** Al hacer clic en *Guardar volumetría*, los datos se persisten en base de datos.
- [ ] **Servicios protegidos.** En filas de servicios (como días de ingeniero con unidad vacía), la casilla *Usado en fluidos* permanece deshabilitada.
- [ ] **Validación de inventario negativo.** Si se escribe en *Usado en fluidos* una cantidad mayor a lo disponible (`Inicial + Recibido`) y se intenta guardar, el sistema rechaza el guardado con el mensaje indicando que no hay suficiente existencia.
- [ ] **Excel del reporte diario.** Descargar el Excel diario (`GET /pozos/<id>/daily-report/<id_rep>/excel/`):
  - En la hoja *Inv Quimico (completo)*, la fila del producto muestra la cantidad en la columna *Diario Usado* (columna F) y el costo diario en la columna *Costo* (columna M).
  - En el encabezado (celda F7), el costo total diario coincide con la suma calculada en el inventario.
- [ ] **Recap del pozo.** Acceder a la vista o Excel del recap (`/pozos/<id>/recap/`):
  - En *Productos consumidos*, el producto refleja la cantidad usada acumulada y su costo total acumulado.
  - En *Costos*, el rubro *Químicos / Personal DF* suma correctamente los costos derivados del consumo manual.

**Notas de la prueba:**

