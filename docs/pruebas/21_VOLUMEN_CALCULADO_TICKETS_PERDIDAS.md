# 21 — Volumen calculado en el Excel, tickets como recibido y pérdidas del sistema activo

Detalle en [27](../27_VOLUMEN_CALCULADO_TICKETS_Y_PERDIDAS.md). Sin migraciones nuevas.

## Cómo funciona

- El final **calculado** de cada tanque pasa como inicial del reporte siguiente.
- En el Excel diario, *Tanques activos* y *Volumen total de circulación* muestran lo calculado, no lo medido.
- Lo del ticket de entrada es lo **Recibido** del día; lo del ticket de salida, lo **Devuelto**. El inicial es el final del día anterior.
- Una pérdida solo se puede registrar en un tanque del sistema activo (volumen circulante).
- *Agregar químicos* muestra la existencia de cada producto, cuánto quedaría y el volumen del tanque antes y después.

## Pasos para verificar

Usar un pozo nuevo con un tanque activo y uno de reserva y dos reportes (día 1 y día 2).

- [ ] Día 1: *Agregar químicos* con 400 bbl de agua al tanque activo. Medir 650 en el tanque. Guardar.
- [ ] Día 1: registrar una pérdida de 18 bbl. El selector de tanque **solo** muestra tanques activos.
- [ ] Día 1, Excel: *Tanques activos* = 382 (400 − 18), no 650. *Volumen total de circulación* = hoyo + 382.
- [ ] Día 2: el *Volumen inicial* del sistema activo es 382 (más el hoyo). Medir otro valor (por ejemplo 700).
- [ ] Día 2, Excel: *Tanques activos* sigue en 382, no 700.
- [ ] Balance de volumen: la columna *Reserva* no tiene pérdidas.
- [ ] Ticket de recepción del día 1 con 35 sacos de un producto: en *Inventario de productos* el inicial es 0, en la casilla de *Recibido* aparece **35** (con el chip del número de ticket) y el final es 35. No aparece texto redundante "Ticket: 35".
- [ ] Guardar volumetría: *Recibido* se mantiene en 35 y *Final* en 35 (no se duplica a 70). Si se modifica la casilla a 40 (añadiendo 5 manuales adicionales), el final se calcula en 40.
- [ ] Día 2: el inicial de ese producto es 35 (o 40). Un ticket nuevo de 6 se plasma en la casilla *Recibido* como 6 y deja el final en 41 (o 46).
- [ ] Excel, hoja de inventario: la columna *Recibido* incluye lo de los tickets.
- [ ] *Agregar químicos*: se ven *Existencia* y *Quedan*; al escribir 40 de un producto con 35, *Quedan* sale −5 en rojo. Abajo aparece el volumen del tanque antes → después.
