# 06 — Tarifas en dos monedas (USD y Bs)

**Punto del doc 23:** 9 · **Migración:** `0031_tarifas_dos_monedas` · **Estado:** sin probar

## Cómo funciona

- El contrato fija **una tarifa en cada moneda** para cada ítem (por ejemplo, salmuera: 30 USD o 1.200 Bs por barril). Las dos son **alternativas**: el pozo elige en cuál cobra y se usa solo esa. No hay tasa de cambio.
- **Configuración General** → *Segunda Moneda*: elegir la segunda moneda (por ejemplo VES) y **Cobrar en** (USD o VES).
- **Productos activos**: con segunda moneda aparecen columnas extra de precio en esa moneda:
  - Productos: *Precio (USD)* y *Precio (VES)*.
  - Equipos: renta y stand-by en cada moneda.
  - Mallas: precio en cada moneda (el descuento se aplica igual a las dos).
- Todos los costos (pestañas 6 y 8, resumen, pantalla detallada, Excel y recap) usan la tarifa de la moneda de cobro y muestran su código.
- Con reportes cargados, **"Cobrar en" queda bloqueado**, porque los costos viejos quedarían en otra moneda. Los nombres de las monedas sí se pueden corregir.
- Desapareció el reparto anterior por % y tasa (el recuadro "Cobro en dos monedas" de la pantalla de costos).
- *Cobro por barril* ([prueba 03](03_PRECIO_POR_BARRIL.md)) funciona igual con cualquiera de las dos tarifas.

## Pasos para verificar

Preparación: un pozo **nuevo, sin reportes**.

- [ ] **Configuración.** En *Configuración General*, la sección *Segunda Moneda* tiene dos selectores: *Segunda moneda* y *Cobrar en*. Ya no aparecen la tasa ni el porcentaje.
- [ ] **Sin segunda moneda.** Con *Segunda moneda* = Ninguna, *Cobrar en* solo ofrece la moneda principal y está deshabilitado.
- [ ] **Monedas iguales.** Elegir VES como segunda moneda y USD como principal → se guarda. Elegir USD en las dos → error "La segunda moneda debe ser distinta".
- [ ] **Columnas extra.** Con VES configurada, en *Productos activos* aparecen *Precio (USD)* y *Precio (VES)*. En equipos, renta y stand-by en cada moneda. En mallas, el precio en cada moneda.
- [ ] **Cargar tarifas.** Salmuera: 30 USD y 1.200 VES. Un equipo: renta 500 USD y 20.000 VES. Una malla: 100 USD y 4.000 VES con 10 % de descuento. Guardar.
- [ ] **Cobrar en VES.** *Cobrar en* = VES, guardar. Crear un reporte, cargar el ticket de la salmuera y agregar 50 bbl → costo **60.000**, con el símbolo VES en la tabla de costos.
- [ ] **Equipo y malla en VES.** En la pestaña 6, un día de renta del equipo → 20.000. Instalar una malla → 3.600 (4.000 − 10 %).
- [ ] **Símbolos.** El resumen de costos, la *Pantalla Detallada de Costos* (indicadores y desglose) y el Excel muestran **VES**, no "$".
- [ ] **Bloqueo.** Con el reporte ya creado, en *Configuración General* el selector *Cobrar en* aparece deshabilitado. Si se intenta cambiar → error "El pozo ya tiene reportes y cobra en VES…".
- [ ] **Corregir el nombre.** Con reportes, cambiar el nombre de la segunda moneda se guarda bien.
- [ ] **Pozos existentes.** Un pozo creado antes de la 0031 sigue cobrando en su moneda principal, con los mismos costos que antes.
- [ ] **Plantilla.** Crear un pozo nuevo usando como plantilla el pozo en VES → copia la segunda moneda, *Cobrar en* y todas las tarifas (también *Cobrar por* de la prueba 03).

**Notas de la prueba:**
