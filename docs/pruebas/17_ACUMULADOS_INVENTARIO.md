# 17 — Acumulados por columna en el inventario

**Documento:** [26](../26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md) · **Migración:** — · **Estado:** sin probar

## Cómo funciona

- La tabla *Inventario diario de productos* (pestaña 8) incluye el grupo de columnas **Acumulado del pozo** situado entre los costos y la columna *Peso (lb)*.
- Muestra los acumulados históricos del pozo hasta la fecha del reporte actual para:
  1. **Recibido**: total de entradas registradas por tickets de recepción.
  2. **Devuelto**: total de salidas por tickets de devolución.
  3. **Usado en fluidos**: total consumido en químicos y lodo en el sistema de fluidos.
  4. **Usado otro módulo**: total transferido a otras líneas del taladro (ej. cementación).
- La columna acumulada de *Usado otro módulo* se actualiza **en vivo** al tipear en la casilla diaria de *Usado otro módulo*.
- El filtro *"Solo con existencia o movimiento"* considera también los acumulados para no ocultar productos con historial en el pozo.

## Pasos para verificar

- [ ] **Cabecera de la tabla.** En la pestaña 8, la tabla *Inventario diario de productos* muestra el grupo **Acumulado del pozo** con cuatro columnas: *Recibido*, *Devuelto*, *Usado en fluidos* y *Usado otro módulo*.
- [ ] **Valores en el día 1.** Con un ticket de recepción de 50 de Barita, 10 agregados en químicos y 3 cargados en *Usado otro módulo*:
  - Recibido acumulado: 50
  - Devuelto acumulado: 0
  - Usado en fluidos acumulado: 10
  - Usado otro módulo acumulado: 3
- [ ] **Cálculo en vivo.** Al modificar el valor diario en *Usado otro módulo* (por ejemplo de 3 a 5), la celda *Usado otro módulo* del acumulado se actualiza en vivo al instante (a 5).
- [ ] **Acumulación en el día 2.** En el siguiente reporte, recibir 20 por ticket, devolver 4 por ticket, consumir 5 en químicos y escribir 2 en *Usado otro módulo*. Guardar volumetría:
  - Recibido acumulado: 70 (50 + 20)
  - Devuelto acumulado: 4 (0 + 4)
  - Usado en fluidos acumulado: 15 (10 + 5)
  - Usado otro módulo acumulado: 5 (3 + 2)
- [ ] **Filtro de movimiento.** Marcar *"Solo con existencia o movimiento"* en un reporte donde el producto no tenga movimientos ese día pero sí acumulados anteriores → el producto no se oculta si tiene historial acumulado.

**Notas de la prueba:**
