# 19 — Dotación por tickets y columnas Recibido/Devuelto manuales

**Documento:** [23](../23_CORRECCIONES_REVISION_OCT.md) · **Migración:** 0037 · **Estado:** sin probar

## Cómo funciona

- **Tickets alimentan la dotación inicial (`INICIAL`):**
  - Los tickets de entrada (guías de despacho del pozo) representan la dotación inicial de productos que llega al taladro según ticket.
  - Al registrar una guía/ticket de entrada, la cantidad ("Según Ticket") alimenta automáticamente la existencia **INICIAL** del producto (`ini_auto`).
  - La casilla de *Inicial* en la tabla muestra directamente este valor inicial como número (con el chip del N° de ticket al lado). El ingeniero no necesita escribirlo a mano.
  - Si desea sobreescribir la existencia inicial, la casilla permite escribir un valor manual que manda sobre el calculado.
- **Encadenamiento día tras día (Inicial del día siguiente = Final del día anterior):**
  - Al guardar el reporte diario de un día, su existencia **FINAL** pasa automáticamente a ser la existencia **INICIAL** del día siguiente, y así sucesivamente.
  - Los tickets de dotación de días anteriores no se re-suman al inicial en días posteriores: una vez que el producto entra al pozo, su existencia inicial día a día es estrictamente el final del día anterior.
- **`RECIBIDO` y `DEVUELTO` se escriben a mano en la tabla:**
  - Ambas columnas son casillas numéricas editables (`<input type="number">`), idénticas a *Usado en fluidos*, *Usado otro módulo* y *Ajuste*.
  - En el día a día, las recepciones o devoluciones rutinarias se introducen directamente en la celda correspondiente sin necesidad de abrir el modal de tickets.
  - Se guardan en base de datos en `InventarioProductoDia.recibido` y `InventarioProductoDia.devuelto` (migración 0038).
- **Fórmula de existencia final:**
  $$\text{Final} = \text{Inicial (ticket/anterior)} + \text{Recibido (a mano)} - \text{Devuelto (a mano)} - \text{Usado fluidos (a mano)} - \text{Usado otro módulo (a mano)} \pm \text{Ajuste (a mano)}$$
- **Cálculo en vivo:**
  - Escribir en *Recibido* o *Devuelto* actualiza instantáneamente en pantalla el *Final*, el *Recibido acumulado* y el *Devuelto acumulado*.
- **Servicios:**
  - En productos de servicio (ingenieros, trailers), las casillas de existencias permanecen deshabilitadas.

## Pasos para verificar

- [ ] **Migración aplicada:** Ejecutar `python manage.py migrate` para aplicar la migración `0038_inventario_recibido_devuelto_manual`.
- [ ] **Casillas editables en la grilla:** Entrar al reporte diario (Pestaña 8 › Inventario):
  - La columna **Recibido** es un `<input>` editable de fondo blanco.
  - La columna **Devuelto** es un `<input>` editable de fondo blanco.
- [ ] **Carga de ticket de dotación inicial:**
  - Abrir *Tickets de entrega / devolución* y registrar un ticket de ENTRADA con 10 sacos de Barita (Según Ticket = 10).
  - Al guardar el ticket, en la tabla de inventario la columna **Inicial** de Barita muestra `10,00` como dotación inicial (y el chip con el número de ticket).
  - La columna **Recibido** permanece en 0 (esperando ingresos del día a día si hubiere).
  - La existencia **Final** refleja `10,00`.
- [ ] **Edición manual de Recibido y Devuelto:**
  - En la casilla *Recibido*, escribir `5`.
  - La existencia *Final* aumenta en vivo a `15,00`.
  - El *Recibido acumulado* aumenta en vivo a `5,00`.
  - En la casilla *Devuelto*, escribir `2`.
  - La existencia *Final* disminuye en vivo a `13,00`.
  - El *Devuelto acumulado* aumenta en vivo a `2,00`.
- [ ] **Guardar volumetría:**
  - Pulsar el botón verde *Guardar volumetría*.
  - Mensaje de éxito *"Volumetría guardada"*.
  - Al recargar la página (F5), los valores de Recibido (5) y Devuelto (2) permanecen intactos.
- [ ] **Al día siguiente:**
  - Abrir el siguiente reporte diario del pozo.
  - La columna *Inicial* toma automáticamente el final del día anterior (`13,00`).
  - Las casillas *Recibido* y *Devuelto* inician limpias en 0.

