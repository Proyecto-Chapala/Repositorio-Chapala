# 04 — Número de ticket en el inventario

**Punto del doc 23:** 5 · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- En la tabla de inventario de la pestaña 8, junto a la cantidad **Recibido**, aparece el número del ticket de entrada del día como etiqueta: **N° 8888**. Lo mismo pasa con **Devuelto** y los tickets de salida.
- Si el mismo producto llegó en varios tickets ese día, se ven todos los números (N° 8888 N° 8889).
- Un ticket guardado sin número no muestra etiqueta. La cantidad se suma igual.
- Los números son los del día del reporte: al día siguiente, como *Recibido* vuelve a 0, tampoco aparece el número.

## Pasos para verificar

Preparación: un pozo con BARITA activa (ver la prueba [01](01_INVENTARIO_POR_POZO.md)).

- [ ] **Ticket de entrada.** Crear un ticket de recepción N° **8888** con BARITA, 35 → en el inventario, la celda *Recibido* muestra "35" y la etiqueta **N° 8888**.
- [ ] **Varios productos.** Agregar GEL al mismo ticket → los dos productos muestran **N° 8888**.
- [ ] **Segundo ticket.** Otro ticket de recepción N° **8889** con BARITA, 10 → BARITA muestra *Recibido* 45 con **N° 8888** y **N° 8889**.
- [ ] **Devolución.** Ticket de salida N° **D-12** con BARITA → la celda *Devuelto* muestra **N° D-12**.
- [ ] **Sin número.** Un ticket guardado sin número suma la cantidad, pero no agrega etiqueta.
- [ ] **Día siguiente.** En el reporte del día siguiente, BARITA no muestra etiquetas de ticket.
- [ ] **Diferencia con el ticket.** Si según ticket es 30 y real 25, se ven las dos etiquetas: "≠ ticket" y el número.

**Notas de la prueba:**
