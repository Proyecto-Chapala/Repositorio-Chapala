# 19 — El inventario usa la cantidad "según ticket"

**Documento:** [09](../09_PESTANA_8_VOLUMETRIA_INVENTARIO.md) (Tickets de productos) · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- El inventario de la pestaña 8 es del pozo y no toma nada de la matriz (ni cantidad ni precio). Un pozo nuevo arranca con **inicial 0**.
- Cada guía de recepción suma en *Recibido* y cada guía de devolución en *Devuelto*, con la cantidad **"Según ticket"** (la que dice la guía). Si llegan varias guías en el día, se suman.
- La cantidad **"Real"** es opcional. Si se escribe y es distinta, se marca "≠ real" en ámbar, pero el inventario sigue usando la de la guía.
- `Final = Inicial + Recibido − Devuelto − Usado en fluidos − Usado otro módulo ± Ajuste`. El final de un día es el inicial del siguiente.
- La ventana de tickets ya no muestra precios.
- Un ticket con "Real" pero sin "Según ticket" se rechaza.

## Pasos para verificar

- [ ] **Pozo nuevo.** En un pozo nuevo con Barita activa, la Barita arranca con Inicial 0 y Final 0.
- [ ] **Sin precio.** Abrir *Tickets de entrega / devolución* → la tabla tiene Producto, Unidad, Según ticket y Real (opcional); **no** hay columna Precio.
- [ ] **Recepción solo con la guía.** Ticket de recepción de 200 de Barita, solo en *Según ticket* → *Recibido* 200, Final 200, sin marca de diferencia.
- [ ] **Uso del día.** Escribir 100 en *Usado en fluidos* y guardar → Final 100.
- [ ] **Día siguiente.** Crear el reporte del día 2 → Inicial 100.
- [ ] **Varias guías.** En el día 2, cargar dos guías de recepción (30 y 20) → *Recibido* 50.
- [ ] **Real distinta.** Una guía de 40 con *Real* 38 → *Recibido* suma 40 y aparece "≠ real" (al pasar el mouse dice el real); el ticket sale "Con diferencias".
- [ ] **Devolución.** Ticket de devolución de 15 solo en *Según ticket* → *Devuelto* 15 y el final baja 15.
- [ ] **Solo real.** Guardar un ticket con *Real* y sin *Según ticket* → mensaje "escribe la cantidad según ticket".

**Notas de la prueba:**
