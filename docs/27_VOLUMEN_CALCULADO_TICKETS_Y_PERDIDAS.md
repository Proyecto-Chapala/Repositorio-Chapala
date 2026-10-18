# 27 — Volumen calculado, tickets como recibido y pérdidas del sistema activo (18-oct-2026)

Revisión del cliente del **15-oct-2026** (mensajes de WhatsApp, capturas de la pestaña 8 y una nota a mano). Fuentes en `docs/fuentes/notas_cliente/2026-10-15_*`.

## Lo que pidió el cliente

1. El volumen perdido no se suma a los volúmenes activos: es independiente y **se descuenta del volumen circulante**.
2. **El volumen final de un reporte es el inicial del próximo.** El Excel salía bien el día de la carga, pero al día siguiente volvía a mostrar el volumen medido (real).
3. En el Excel, **tanques activos** y **volumen total de circulación** llevan lo **calculado** de los tanques.
4. Lo ingresado en el **ticket es lo recibido**. El inicial cambia el segundo día al final del día anterior.
5. En **Agregar químicos**: mostrar la cantidad de los productos (o del tanque) y, al escribir la cantidad, cuánto queda.
6. Balance de volumen: la pérdida total no debe quedar sumada en la reserva.

### Análisis de las imágenes

- **Capturas 1 y 2** (`2026-10-15_balance_perdidas_en_reserva_*.jpg`): las pérdidas de 18 bbl (evaporación) y 50 bbl (perdido en formación) se registraron sobre *Reserva 1* y *Reserva 2*. Por eso la reserva calculada queda en −68, el "no contabilizado" de la reserva sube a 568 y aparecen los avisos de volumen negativo. La pérdida debió salir del sistema activo.
- **Nota a mano** (`2026-10-15_nota_quimicos_inventario_balance.jpg`): "Agrega químico — mostrar inventario, cantidad, que se refleje en tanques y en inventario"; "volumen inicial cuadra con volúmenes agregados y pérdidas"; ejemplo 1000 inicial → 1100.

## Qué se cambió

| Punto | Dónde | Cambio |
|---|---|---|
| 1, 6 | `views_inventario._llenar_movimiento_de_volumen` y modal de pérdida (`reporte_inventario.js`) | Una pérdida **solo se registra o edita sobre un tanque del sistema activo**. El servidor rechaza otro tanque y el formulario solo ofrece tanques activos. Las pérdidas ya guardadas en reserva no se tocan: si se editan, piden cambiar a un tanque activo. |
| 2 | `volumetria.simular` (commit `79c53f3` del compañero) | El inicial de cada tanque es el **final calculado** del día anterior, no el medido. |
| 2, 3 | `reporte_excel._volumen_y_circulacion` | "Tanques activos" (F10) = suma de lo **calculado** de los tanques activos; "Volumen total de circulación" (E12) = hoyo + eso. Esta era la causa de que al día siguiente apareciera el real. |
| 4 | `volumetria.simular`, `views_inventario` (`recibido_total`, `devuelto_total`), Excel de inventario | Tickets de entrada → **Recibido** del día; tickets de salida → **Devuelto**. Inicial = final del día anterior (0 el primer día) o el escrito a mano. Antes el ticket iba al *Inicial* y un segundo ticket de un producto ya iniciado se perdía. En pantalla, la casilla *Recibido* sigue siendo lo escrito a mano; debajo aparecen los números de ticket y "Ticket: X", y el final ya los suma. |
| 5 | Modal *Agregar químicos* | Columnas **Existencia** (final del día en inventario) y **Quedan** (existencia − cantidad; en rojo si queda negativa) y el volumen calculado del tanque antes → después. Es informativo: agregar químicos sigue sin descontar inventario (Parte C de [26](26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md)); el consumo se escribe en *Usado en fluidos*. |

Sin migraciones nuevas. Pruebas: `test_excel_volumen_calculado.py`, `test_volumetria_inventario.py`, `test_ticket_segun_guia.py`, `test_editar_movimientos.py` (`test_la_perdida_no_se_descuenta_de_la_reserva`).

Guía de prueba en pantalla: [pruebas/21](pruebas/21_VOLUMEN_CALCULADO_TICKETS_PERDIDAS.md).
