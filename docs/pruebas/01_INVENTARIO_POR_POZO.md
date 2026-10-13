# 01 — Inventario por pozo

**Puntos del doc 23:** 1 (en parte), 2, 3 y 4 · **Migración:** `0028_inventario_por_pozo` · **Estado:** sin probar

## Cómo funciona

- La **matriz** (pantalla *Inventario*) es solo catálogo: código, descripción, libraje y GE. No pasa cantidades ni precios al pozo, y el reporte diario **no modifica** su cantidad.
- Cada pozo lleva su propio inventario a partir de los **tickets**:
  - Un ticket de **entrada** suma en *Recibido* la cantidad **real**. La cantidad *según ticket* queda para comparar: si difiere, aparece "≠ ticket".
  - Un ticket de **salida** suma en *Devuelto*.
  - `Final = Inicial + Recibido − Devuelto − Usado en fluidos − Usado otro módulo ± Ajuste`.
  - Al día siguiente: *Inicial* = *Final* del día anterior y *Recibido* = 0.
- Usar un producto sin existencia en el pozo se rechaza con el mensaje *"Registra primero el ticket de recepción."*
- El **precio** arranca en 0 al activar un producto y lo carga el usuario según el contrato. Nunca viene de la matriz.
- Borrar un reporte o un pozo ya no devuelve nada a la matriz.

## Pasos para verificar

Preparación: crear un pozo nuevo con al menos un tanque activo, y activar BARITA (LBS, tamaño 100, GE 4,2) en *Productos activos*.

- [ ] **Precio en 0.** Al activar BARITA, la columna Precio aparece en 0, aunque la matriz tenga un costo cargado.
- [ ] **Uso sin ticket.** En el reporte del día 1, *Agregar químicos* con 10 sacos de BARITA → error "Registra primero el ticket de recepción".
- [ ] **Recepción.** Crear un ticket de entrada con BARITA: según ticket 30, real 25 → *Recibido* = 25 con la marca "≠ ticket", *Final* = 25.
- [ ] **Uso.** *Agregar químicos* con 10 sacos → *Usado en fluidos* = 10, *Final* = 15.
- [ ] **Otro módulo y ajuste.** *Usado otro módulo* = 2 y *Ajuste* = +1, guardar → *Final* = 14.
- [ ] **Día siguiente.** Crear el reporte del día 2 → *Inicial* = 14, *Recibido* = 0.
- [ ] **Segunda recepción.** En el día 2, ticket de entrada con 100 → *Final* = 114.
- [ ] **Devolución.** Ticket de salida con 4 → *Devuelto* = 4, *Final* = 110.
- [ ] **Matriz intacta.** En la pantalla *Inventario*, la cantidad de BARITA es la misma que antes de empezar.
- [ ] **Borrar.** Borrar el reporte del día 2 → la matriz sigue sin cambios y el día 1 conserva su *Final* = 14.

**Notas de la prueba:**
