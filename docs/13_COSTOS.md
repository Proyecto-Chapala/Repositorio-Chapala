# 13 — Costos

Todos los costos del reporte diario se calculan en **un solo lugar**: `views_inventario.resumen_costos(pozo, reporte)`. Lo usan la pestaña 1 (tarjeta de balance económico), el modal *Cost Overview* y el Excel.

Ningún costo se guarda: se recalculan en cada consulta a partir de los hechos registrados (movimientos, tickets, transacciones y uso de equipos).

## Columnas (como en ONE-TRAX)

| Columna | Qué suma | Origen |
|---|---|---|
| **Químicos / Personal DF** (`df_chem`) | Productos y servicios con categoría de costo **1 (Químicos)** y **2 (Ingeniero de fluidos)** | Pestaña 8 |
| **Ingeniero IFE / Control de sólidos** (`ife_sc`) | Categorías **3 (Ing. control de sólidos)** y **4 (Ing. IFE)** | Pestaña 8 |
| **Total perforación** | `df_chem + ife_sc` | |
| **Equipos / Mallas** (`df_equip`) | Renta de equipos + mallas nuevas instaladas | Pestaña 6 |
| **Otros** (`other_cost`) | DWM/CF: **siempre 0**, porque no hay módulo todavía | — |
| **Total** | Total perforación + Equipos/Mallas + Otros | |

Cada columna se da **del día** y **acumulada** del pozo hasta la fecha del reporte.

## De dónde sale cada costo

### Productos (pestaña 8)

| Hecho | Costo |
|---|---|
| *Agregar químicos* | cantidad × precio del producto **en ese momento** (copiado en el movimiento) |
| *Agregar lodo reciclado* | unidades consumidas del producto "lodo reciclado" × su precio |
| *Usado en otro módulo* (inventario manual) | cantidad × precio del día (ej. días de ingeniero) |
| Servicios (productos con unidad vacía) | Solo costo, sin existencias |

La **categoría** de cada costo es el *código de costo diario* del producto activo, editable por día en el inventario. Se reparte así: 1 = Químicos, 2 = Ingeniero de fluidos, 3 = Ingeniero de control de sólidos, 4 = Ingeniero IFE. **Pendiente**: confirmar con AOS el significado de los códigos 1-4.

### Equipos (pestaña 6)

`costo = cantidad usada × tarifa`. La tarifa es la **de renta** (`COMPLETO`), la **standby** (`STANDBY`) o 0 (`SIN_COBRO`), tomada de *Equipos activos* **el día que se registra** y congelada mientras no cambie el código de cobro.

### Mallas (pestaña 6)

Cada **malla nueva instalada** cuesta su **precio neto** = `precio × (100 − descuento%) / 100`, redondeado a centavos y congelado en la transacción. Recibir mallas o instalar usadas no cuesta.

## Impuesto

`Pozo.tasa_impuesto` (%) solo se usa en el **Excel**, en las hojas de inventario, como impuesto sobre el costo químico del día. No se suma a los totales del reporte.

## Detalle (Cost Overview)

`GET …/cost-overview/` devuelve los totales y la lista de ítems con categoría, descripción, cantidad, unidad, costo unitario y costo total. Por ejemplo: *"Renta Centrífuga (CF-01)"*, *"Mallas nuevas instaladas: 170 Mesh"*, cada producto químico.

## Si algo no cuadra

Si la línea de tiempo de la volumetría o de las mallas tiene un error (por ejemplo, tras borrar un reporte con tickets), `resumen_costos` **omite** esa parte en silencio (costo 0) para no romper la pantalla. Si los costos se ven en 0 de repente, hay que abrir la pestaña 6 u 8 de ese reporte: allí sí aparece el mensaje de error.

## Cobro en dos monedas (02-oct-2026)

Si el pozo tiene **segunda moneda** (Configuración General), la *Pantalla Detallada de Costos* del reporte muestra un recuadro con el reparto del total del día y del acumulado:

```
a cobrar en la moneda del pozo  = total × (1 − %/100)
a cobrar en la segunda moneda   = total × %/100 × tasa
total expresado en la segunda   = total × tasa
```

Los costos se siguen calculando y guardando en la moneda del pozo; no hay conversión de precios. Función `cobro_dos_monedas()` en `views_daily_reports.py`. El Excel diario todavía no muestra este reparto.
