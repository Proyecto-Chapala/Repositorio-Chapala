# 10 — Cerrar un intervalo como side track

**Punto del doc 23:** 14 · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- **Causa del error del cliente:** "Cerrar intervalo" cerraba con los datos **ya guardados**. Si en el formulario se cambiaba el tipo a *Side Track* y se pulsaba Cerrar sin pulsar antes Guardar, el cambio se perdía y el intervalo quedaba como *Producción*. La ventana de confirmación avisaba "Guarda antes los cambios", pero era fácil pasarlo por alto.
- **Ahora:** el botón se llama **"Guardar y cerrar intervalo"**. Guarda lo que está en el formulario (tipo, profundidad, diámetros…) y cierra el intervalo en la misma operación, con las mismas validaciones que *Guardar*.
- La confirmación dice con qué tipo se va a cerrar: *¿Guardar y cerrar el intervalo 3 como "Side Track (desvío)"?*.
- Si falta el tipo o la profundidad, o algún dato es inválido, **no se guarda ni se cierra** y aparece el motivo.
- Al cerrar el side track con el tapón, el volumen que queda bajo el tapón se carga en la pestaña 8 en **"No ocupado por fluido"** y, si corresponde, se registra la pérdida "entrampado en el hoyo". Eso es el punto 13.

## Pasos para verificar

Preparación: pozo con un intervalo abierto de tipo *Producción*.

- [ ] **Botón.** En *Intervalos de revestimiento*, al abrir el intervalo, el botón dice **"Guardar y cerrar intervalo"**.
- [ ] **El caso del cliente.** Cambiar el tipo a *Side Track (desvío)*, **sin pulsar Guardar**, y pulsar "Guardar y cerrar intervalo" → la confirmación dice "como Side Track (desvío)". Aceptar → la lista muestra el intervalo **cerrado y de tipo Side Track**.
- [ ] **Otros datos.** Cambiar también la profundidad antes de cerrar → queda guardada.
- [ ] **Sin tipo.** En otro intervalo abierto, dejar el tipo vacío y cerrar → error "Para cerrar el intervalo indica el tipo" y el intervalo sigue abierto.
- [ ] **Cancelar.** Pulsar cerrar y cancelar la confirmación → no cambia nada.
- [ ] **Siguiente.** Después de cerrar, se puede crear el siguiente intervalo (el nuevo side track).
- [ ] **Reabrir.** "Reabrir" el último intervalo sigue funcionando igual.
- [ ] **Programa del martes.** Piloto de 8½" → ampliación a 12¼" → tres side tracks, cerrando cada uno como Side Track → cada uno queda con su tipo y su costo en el recap.

**Notas de la prueba:**
