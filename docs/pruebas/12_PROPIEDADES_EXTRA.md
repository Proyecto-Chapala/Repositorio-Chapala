# 12 — Propiedades extra que se guardan y aparecen

**Punto del doc 23:** 15 · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- **Causas del error del cliente** (cargó "% Carbonato = 20" en la última prueba y "no aparecía por ningún lado"):
  1. La grilla de propiedades de la pestaña 3 **nunca** mostraba las propiedades extra. Solo se veían dentro de su ventana.
  2. El reporte de propiedades solo imprimía las extra **1 a 8** con **orden de impresión > 0**. Una propiedad nueva suele quedar con orden 0 o con un número mayor que 8.
- **Regla única ahora** (la usan la grilla, el reporte de propiedades y el Excel): se muestran las propiedades extra **del tipo de fluido del reporte** (base agua o aceite/sintético), **con etiqueta**, que tienen **orden de impresión** o **algún valor cargado ese día**. Primero van las que tienen orden (1, 2, …) y después las que solo tienen valor, por número.
- **Pestaña 3:** al final de la grilla aparece la sección **"Propiedades Extra"**, con una fila por propiedad, su etiqueta, su unidad y una celda por chequeo (#1 a #4). Las celdas se editan y se guardan con el resto de la pestaña.
- **Ventana "Propiedades Extra del Reporte":** sigue mostrando todas las del tipo de fluido. Al guardar, los valores pasan a la grilla y, si una propiedad recibe su primer valor, su fila se agrega sola.
- **Excel:** las 1 a 8 que corresponden van en la hoja del lodo y las 9 a 60 en la hoja de propiedades extra, con la misma regla. Las propiedades con valor ya no se pierden por no tener orden.

## Pasos para verificar

Preparación: en la configuración de etiquetas extra del pozo, crear "% Carbonato" (unidad %) con **orden de impresión 0** y un número mayor que 8, por ejemplo 12. Crear otra, "Sulfuros", con orden 1.

- [ ] **Con orden, sin valor.** En la pestaña 3, al final de la grilla, aparece "Propiedades Extra" con la fila **Sulfuros** (vacía). "% Carbonato" todavía no aparece, porque no tiene orden ni valor.
- [ ] **El caso del cliente.** Abrir la ventana de propiedades extra, escribir **20** en "% Carbonato", columna **#4**, y guardar → en la grilla aparece la fila **% Carbonato** con 20 en la columna #4, sin recargar.
- [ ] **Editar en la grilla.** Cambiar el valor a 25 directo en la grilla y guardar la pestaña → al reabrir la ventana se ve 25.
- [ ] **Persistencia.** Recargar la página → la fila sigue con su valor.
- [ ] **Reporte de propiedades.** Abrir el reporte de propiedades del día → aparece "% Carbonato" con su valor en el chequeo #4.
- [ ] **Excel.** Descargar el Excel → "% Carbonato" aparece en la hoja de propiedades extra (es la n.° 12).
- [ ] **Tipo de fluido.** En un reporte de base aceite, la grilla muestra solo las propiedades extra de aceite/sintético.
- [ ] **Sin etiqueta.** Las propiedades sin etiqueta no aparecen en ningún lado.

**Notas de la prueba:**
