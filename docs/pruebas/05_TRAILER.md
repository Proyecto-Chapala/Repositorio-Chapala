# 05 — Categoría Trailer

**Punto del doc 23:** 18 (y aclara el 17) · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- El trailer funciona igual que el ingeniero de fluidos: es un **servicio**. Tiene una tarifa diaria y lleva un **costo diario** y un **acumulado**. No tiene existencias, no aporta volumen ni concentraciones y **no** es un equipo de control de sólidos.
- **Configuración** (una sola vez por pozo):
  1. En la matriz (pantalla *Inventario*), crear el producto, por ejemplo código `TRAILER`, descripción "Trailer", unidad `DIA`. La matriz pide una unidad.
  2. En *Productos activos* del pozo, agregarlo con la **Unidad vacía** (eso lo marca como servicio), el **Precio** = tarifa diaria del contrato y el **Cód. Costo Diario = 5**.
- **Uso diario:** en la pestaña 8, en la fila del trailer, escribir los días cobrados en **Usado otro módulo** (normalmente 1) y guardar.
- Dónde se ve el costo:
  - Pestaña 8, tabla de costos por categoría: una fila **Trailer** con diario y acumulado.
  - Resumen de costos (pestaña 1): columna **Otros Costos (Trailer)**. Suma en el total, pero **no** en *Total Perforación*.
  - Recap del pozo (pantalla y Excel): línea **Otros costos (trailer)**.
  - Excel del reporte diario, hoja del lodo: la fila **Otros (Trailer)** va debajo de *Equipos*, y **TOTALES** baja una fila. La plantilla no se modifica: la fila la agrega el código, en un espacio libre que ya estaba dentro del área de impresión.
- **Punto 17 (ingeniero de fluidos):** se carga igual que el trailer, pero con **Cód. Costo Diario = 2**, y suma en *Químicos / Personal DF*. La columna del resumen que decía "Ingeniero de Fluidos" en realidad mostraba el costo del ingeniero IFE y de control de sólidos (códigos 3 y 4). Ahora dice **Ingeniero IFE / Control de Sólidos**.

## Pasos para verificar

- [ ] **Configuración.** Crear `TRAILER` en la matriz y activarlo en el pozo con unidad vacía, precio 250 y código 5 → se guarda sin pedir GE.
- [ ] **Etiqueta de servicio.** En la pestaña 8, el trailer aparece con la etiqueta "Servicio" e *Inicial* y *Final* en "—".
- [ ] **Costo del día.** *Usado otro módulo* = 1, guardar → tabla de costos: fila **Trailer** con diario 250 y acumulado 250.
- [ ] **Acumulado.** En el día 2, cargar otra vez 1 → Trailer diario 250, acumulado 500.
- [ ] **Resumen de costos.** En la pestaña 1, la columna **Otros Costos (Trailer)** muestra 250 en el diario y 500 en el acumulado, y el **TOTAL** los incluye.
- [ ] **Sin volumen.** La volumetría no cambia: *Volumen de químicos agregados* sigue igual.
- [ ] **Recap.** En el recap del pozo aparece la línea **Otros costos (trailer)** = 500.
- [ ] **Excel diario.** Descargar el Excel del día 2 → bloque de costos: *Fluidos Perf.*, *C.S. e Ing.*, *Equipos*, **Otros (Trailer)** con 250 / 500 y **TOTALES** debajo, con su formato (negrita y bordes), sin celdas desalineadas.
- [ ] **Excel en base aceite.** Lo mismo con un reporte de tipo base aceite o sintética: el bloque empieza una fila más abajo.
- [ ] **Vista de impresión.** En la vista previa de impresión del Excel, la fila de TOTALES se ve completa dentro de la página.
- [ ] **Ingeniero de fluidos.** Un servicio con código 2 a 500 por día suma en **Químicos / Personal DF**, no en la columna de IFE.
- [ ] **Nota de categorías.** Debajo de la tabla de costos de la pestaña 8, la nota lista los códigos del 1 al 5 y explica cómo se cargan los servicios.

**Notas de la prueba:**
