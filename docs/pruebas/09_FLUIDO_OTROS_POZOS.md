# 09 — Recepción y envío de fluido (otros pozos y almacén)

**Punto del doc 23:** 12 · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- El recuadro **Datos del inventario** de la pestaña 8 muestra, además del peso y el volumen de químicos del día:
  - **Recepción desde almacén (hoy)**: lodo reciclado del día con "Recibido de" = un almacén.
  - **Recepción desde otro pozo (hoy)**: lodo reciclado del día con "Recibido de" = "Otro taladro / pozo".
  - **Devolución a almacén (hoy)**: devoluciones del día a un almacén.
  - **Envío a otro pozo (hoy)**: devoluciones del día a "Otro taladro / pozo".
- Los valores salen de los movimientos de la volumetría del reporte, en bbl. Las transferencias entre tanques, las pérdidas y los químicos no cuentan aquí, porque no entran ni salen del pozo.
- Si se edita o elimina uno de esos movimientos (prueba 08), el recuadro se actualiza.
- La recepción de **productos** desde el almacén u otro pozo sigue entrando por los **tickets** (prueba 04). Su número aparece en el inventario y el último número de cada tipo de ticket se ve en el mismo recuadro.
- Decisión del usuario: no se elige el pozo por nombre ni se crea el movimiento solo en el otro pozo. Cada pozo registra lo suyo.

## Pasos para verificar

Preparación: pozo con un tanque activo, un almacén configurado y un producto de lodo reciclado (BBL) con ticket de entrada.

- [ ] **Sin movimientos.** Las cuatro filas nuevas muestran 0,0 bbl.
- [ ] **Recepción desde otro pozo.** *Agregar lodo reciclado* de 80 bbl con "Recibido de" = Otro taladro / pozo → **Recepción desde otro pozo** = 80,0.
- [ ] **Recepción desde almacén.** *Agregar lodo reciclado* de 50 bbl desde un almacén → **Recepción desde almacén** = 50,0.
- [ ] **Envío a otro pozo.** *Devolución* de 30 bbl a Otro taladro / pozo → **Envío a otro pozo** = 30,0.
- [ ] **Devolución a almacén.** *Devolución* de 15 bbl a un almacén → **Devolución a almacén** = 15,0.
- [ ] **No cuentan.** Una transferencia entre tanques o una pérdida no cambia ninguna de las cuatro filas.
- [ ] **Editar.** Editar el envío y cambiarlo a 40 → **Envío a otro pozo** = 40,0. Eliminarlo → 0,0.
- [ ] **Otro día.** En el reporte del día siguiente, las cuatro filas vuelven a 0 (son del día).

**Notas de la prueba:**
