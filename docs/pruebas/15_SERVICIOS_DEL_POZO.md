# 15 — Servicios del pozo (ingenieros, trailers…)

**Documento:** [25](../25_SERVICIOS_DEL_POZO.md) · **Migración:** 0035 · **Estado:** sin probar

## Cómo funciona

- En la pestaña 8 hay una pestaña **Servicios** al lado de *Inventario de productos*.
- Abajo, en **Agregar servicio**, se da de alta cada servicio del contrato con su descripción, categoría (ingeniero de fluidos, ingeniero de control de sólidos, ingeniero IFE o trailer) y tarifa diaria.
- Arriba, en **Servicios del día**, se escriben los días cobrados de ese reporte (normalmente 1). La tarifa aplicada viene de la del contrato y se puede corregir para ese día. Se guarda con **Guardar volumetría**.
- El costo suma en el resumen de costos según la categoría. Cada día guarda su tarifa: cambiar la del contrato no toca los días ya cargados.
- "Usado otro módulo" del inventario queda solo para los productos que se transfieren a otra línea (por ejemplo, cementación).

## Pasos para verificar

- [ ] **Migración.** `python manage.py migrate` aplica la `0035_servicios_del_pozo` sin errores.
- [ ] **Pestaña.** En la pestaña 8 aparece la pestaña **Servicios** al lado de *Inventario de productos*. Sin servicios, la tabla dice que el pozo no tiene servicios.
- [ ] **Alta.** Agregar "Ingeniería de fluidos (coordinador + 2 ingenieros)", categoría *Ingeniero de fluidos*, tarifa 1500 → aparece en la tabla con tarifa del contrato 1500.
- [ ] **Validación.** Guardar un servicio sin descripción → mensaje "Escribe la descripción del servicio."
- [ ] **Segundo servicio.** Agregar "Control de sólidos", categoría *Ingeniero de control de sólidos*, tarifa 800.
- [ ] **Cobro del día.** Escribir 1 día en los dos → *Diario* y el total se actualizan al escribir (1500 y 800; total 2300). Guardar volumetría.
- [ ] **Resumen de la pestaña 8.** En *Inventario de productos*, la tabla *Resumen de costos* muestra 1500 en *Ingeniero de fluidos* y 800 en *Ingeniero de control de sólidos*.
- [ ] **Pestaña 1.** El resumen de costos muestra 1500 en *Químicos / Personal DF* y 800 en *Ingeniero IFE / Control de sólidos*; en el desglose aparecen los dos servicios con "días".
- [ ] **Acumulado.** En el día siguiente cobrar 1 día de fluidos → diario 1500, acumulado 3000; control de sólidos diario 0, acumulado 800.
- [ ] **Tarifa corregida.** En un día, cambiar la tarifa aplicada de fluidos a 1200 y guardar → ese día cuesta 1200; los demás no cambian.
- [ ] **Cambio de contrato.** *Editar* fluidos y poner tarifa 2000 → los días ya cargados conservan 1500; un día nuevo propone 2000.
- [ ] **Quitar con días.** *Quitar* fluidos → mensaje de que se desactivó; el acumulado no baja; en días anteriores sigue apareciendo como "(inactivo)".
- [ ] **Quitar sin días.** Crear un servicio y quitarlo sin cobrarle días → desaparece.
- [ ] **Trailer.** Servicio categoría *Trailer*, 250 por día, 1 día → en la pestaña 1 suma en *Otros costos (Trailer)* y en el Excel diario en la fila *Otros (Trailer)*.
- [ ] **Recap.** En el reporte final del pozo, el costo total incluye los servicios.
- [ ] **Nombres.** Los nombres de los ingenieros siguen saliendo de los datos generales del pozo, no de los servicios.

**Notas de la prueba:**
