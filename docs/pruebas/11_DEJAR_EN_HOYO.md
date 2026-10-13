# 11 — Dejar volumen en el hoyo (tapón / side track)

**Punto del doc 23:** 13 · **Migración:** ninguna · **Estado:** sin probar · **Relacionado:** [10](10_CERRAR_SIDETRACK.md)

## Cómo funciona

- **Problema:** el día del tapón de cemento (abandono antes de un side track), el volumen del hoyo viejo bajo el tapón deja de ser fluido del sistema activo. Había que hacer **dos pasos sueltos** en la pestaña 8: escribir ese volumen en "No ocupado por fluido" y registrar aparte una pérdida por lo mismo. Si se olvidaba uno, el balance no cuadraba. Además, el campo era difícil de encontrar: el cliente marcó sidetrack y "no vio el no fluido".
- **Ahora:** en la pestaña 8 → *Balance*, debajo de la tabla **Fluido en el hoyo**, está el botón **"Dejar volumen en el hoyo (tapón / side track)"**. Abre una ventana con:
  - **Parte del hoyo**: por defecto *Bajo la mecha*, que es el hoyo bajo el tapón.
  - **Volumen** (bbl): viene sugerido con el fluido que hoy queda bajo la mecha. Para eso, en la pestaña 1 la mecha va en el tope del tapón.
  - **Tanque activo** de la pérdida. Solo aparecen tanques del sistema activo, porque el hoyo es parte de ese sistema.
  - **Tipo de pérdida**: por defecto *7 · Detrás del Revestimiento / En el Hoyo*.
- Al registrar, en **una sola operación**, el volumen **se suma** al "No ocupado por fluido" de esa parte y se crea la **pérdida**. El sistema activo sigue cuadrando. La pérdida aparece en *Movimientos* y se puede editar o eliminar (prueba 08).
- **Día del kick-off:** si en la pestaña 4 se marcó "Hoy arranca un side track", la pestaña 8 muestra un aviso amarillo que recuerda registrar el hoyo viejo como dejado en el hoyo, si no se hizo el día del tapón.
- Si hay cambios sin guardar en la volumetría, primero pide guardarlos, para no pisarlos.

## Pasos para verificar

Preparación: pozo con un tanque activo y el balance cuadrado (No contabilizado = 0).

- [ ] **Botón.** En la pestaña 8 → *Balance*, debajo de *Fluido en el hoyo*, aparece "Dejar volumen en el hoyo (tapón / side track)".
- [ ] **Sugerencia.** En la pestaña 1, poner la mecha más arriba que el fondo (tope del tapón) y guardar. Abrir la ventana → el volumen sugerido es el "Bajo la mecha" de la tabla del hoyo.
- [ ] **Registrar.** Aceptar con el tanque activo y la categoría 7 → en la tabla del hoyo, "No ocupado por fluido / Bajo la mecha" = ese volumen. En *Pérdidas*, la categoría 7 tiene ese volumen en la columna del activo.
- [ ] **Balance.** Real del tanque activo sin cambios → *No contabilizado* del activo sigue en **0**.
- [ ] **Se suma.** Registrar otra vez 10 bbl → el no fluido aumenta 10 (no se reemplaza).
- [ ] **Solo tanques activos.** En la lista de tanques no aparecen los de reserva ni los de premezcla.
- [ ] **Cambios sin guardar.** Escribir algo en la tabla de tanques sin guardar y pulsar el botón → pide guardar primero.
- [ ] **Aviso de kick-off.** Al día siguiente, en la pestaña 4 marcar "Hoy arranca un side track" con kick-off a 500 ft y guardar → en la pestaña 8 aparece el aviso amarillo "Hoy arranca un side track desde 500 ft…".
- [ ] **Corregir.** En *Movimientos*, la pérdida creada se puede editar o eliminar. Si se elimina, hay que corregir también el no fluido a mano y guardar.

**Notas de la prueba:**
