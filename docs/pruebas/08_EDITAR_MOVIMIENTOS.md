# 08 — Editar y eliminar movimientos (pérdidas, transferencias, devoluciones)

**Punto del doc 23:** 11 (y lo que faltaba del 1) · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- En la pestaña 8, la ventana **Movimientos de fluidos del día** muestra junto a cada movimiento del reporte:
  - **Editar**, en transferencias, devoluciones y pérdidas. Abre la misma ventana de registro con los datos cargados. Se puede cambiar el tanque, el destino, el volumen o el tipo de pérdida. El **tipo de movimiento no cambia**: si es otro tipo, se elimina y se carga de nuevo.
  - **Eliminar**, en cualquier movimiento, también químicos y lodo reciclado. Pide confirmación.
- Funciona con cualquier movimiento del reporte, no solo con el último. "Deshacer último" sigue disponible.
- La fórmula se mantiene: después de cada cambio se recalcula toda la historia del pozo (volúmenes, balance, pérdidas, inventario y concentraciones). Si el cambio deja algo imposible (un tanque sin tipo, un producto sin existencia), **no se guarda** y aparece el motivo.
- Solo se editan movimientos del reporte abierto. Los de otro día se corrigen desde su reporte.
- Las validaciones al editar son las mismas que al registrar: origen y destino distintos, "devuelto a" obligatorio, tipo de pérdida obligatorio.
- Al imprimir la lista de movimientos, los botones no aparecen.

## Pasos para verificar

Preparación: pozo con un tanque activo (1) y uno de reserva (2), los dos con tipo guardado.

- [ ] **Cargar.** Registrar en orden: químicos con 300 bbl de agua en reserva (#1), transferencia de 100 bbl de reserva a activo (#2), pérdida de 20 bbl del activo (#3) y devolución de 10 bbl de reserva al almacén (#4).
- [ ] **Botones.** En *Movimientos*, el #1 (químicos) muestra solo **Eliminar**. Del #2 al #4 muestran **Editar** y **Eliminar**.
- [ ] **Editar uno del medio.** Editar el #2 y cambiar el volumen a 150 → la ventana dice "Modificar el movimiento #2" con los datos cargados. Guardar → el balance muestra activo 130 (150 − 20) y reserva 140 (300 − 150 − 10).
- [ ] **El tipo queda fijo.** Al editar el #2, los botones "Devolución" y "Pérdida y descarte" aparecen deshabilitados.
- [ ] **Tipo de pérdida y tanque.** Editar el #3: cambiar el tanque a reserva y el tipo de pérdida → la tabla de pérdidas mueve el volumen a la nueva categoría y a la columna de reserva.
- [ ] **Eliminar uno del medio.** Eliminar el #2 → la lista queda #1, #3, #4 y el balance se recalcula.
- [ ] **Cambio imposible.** Editar una transferencia y elegir como destino un tanque de tipo "Vacía" → error "No se puede modificar: … no tiene tipo asignado" y el movimiento queda como estaba.
- [ ] **Validación.** Editar una transferencia con origen igual a destino → error "El tanque de origen y el de destino son el mismo".
- [ ] **Otro día.** En el reporte del día siguiente, los movimientos del día anterior no aparecen en la lista. Se editan desde su reporte.
- [ ] **Cancelar.** Abrir *Editar* y cancelar → nada cambia. Después, *Transferencia/Pérdida* abre la ventana vacía y en modo registro.

**Notas de la prueba:**
