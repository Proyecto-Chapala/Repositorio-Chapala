# 25 — Servicios del pozo (ingenieros, trailers…)

**Fecha:** 13-oct-2026 · **Migración:** `0035_servicios_del_pozo` · **Prueba en pantalla:** [pruebas/15](pruebas/15_SERVICIOS_DEL_POZO.md) · **Fuente:** `docs/fuentes/notas_cliente/2026-10-13_servicios_y_usado_otro_modulo.txt`

## 1. Qué pidió el usuario (análisis)

- **"Usado en otro módulo" es solo para productos químicos que se transfieren a otra línea.** Por ejemplo, cementación pide productos: se le pasan a precio de lista, salen del inventario y se cobran, pero **no** cuentan en las concentraciones ni en el lodo. Eso ya funcionaba así (punto 6 del [23](23_CORRECCIONES_REVISION_OCT.md)).
- **Los ingenieros y trailers no son productos.** Son la parte contable del contrato que se cobra por día: cada servicio tiene su categoría y su tarifa diaria. Ejemplo: "servicio de ingeniería = 1 coordinador + 2 ingenieros, tarifa X por día". Si se usó un día, se refleja su costo del día y el acumulado.
- Las tarifas son distintas por servicio (fluidos ≠ control de sólidos); cada uno lleva su categoría. También puede haber servicios de filtración y otros.
- **Los nombres de los ingenieros** siguen saliendo de los datos generales del pozo (Well Header). El servicio no lleva nombres.
- **Dónde:** en la pestaña 8, una pestaña **Servicios** al lado de *Inventario de productos*.
- Al cerrar el pozo, lo cobrado queda cerrado: cambiar la tarifa después no cambia los días ya cargados.
- **No** se pasan a la nueva sección los servicios que algún pozo ya tenga cargados como "producto sin unidad".

## 2. Cómo quedó

| Pieza | Dónde |
|---|---|
| `ServicioPozo` (pozo, descripción, categoría, tarifa diaria, activo) | `operaciones/models_servicios.py` |
| `ServicioDia` (reporte, servicio, días cobrados, **copia** de la tarifa y de la categoría) | `operaciones/models_servicios.py` |
| `costos_servicios(pozo, reporte)`: costo del día y acumulado por categoría y por servicio | `operaciones/models_servicios.py` |
| Categorías de servicio = todas las de costo menos químicos (`vol.CATEGORIAS_SERVICIO`) | `operaciones/volumetria.py` |
| Lectura (`servicios`, `categorias_servicio`) y guardado de los días (con *Guardar volumetría*) | `views_inventario._servicios_del_dia`, `_leer_servicios_del_dia`, `api_volumetria_guardar` |
| Alta, edición y baja de servicios | `api_servicio_guardar`, `api_servicio_eliminar` (`.../volumetria/servicio/...`) |
| Resumen de costos de la pestaña 1 y Excel diario | `views_inventario.resumen_costos` |
| Recap del pozo | `recap_pozo.datos_recap` |
| Pantalla | `reporte_diario_detalle.html` (`vaPanelServicios`), `reporte_inventario.js` (`vaRenderServicios`, `vaSrvGuardar`), `reporte_inventario.css` (`.va-srv-form`) |

Reglas:

- **Costo del día = días cobrados × tarifa aplicada.** La tarifa aplicada viene de la tarifa del contrato y se puede corregir para un día puntual.
- Cada día guarda su propia tarifa y categoría. Cambiar la tarifa del contrato solo afecta a los días que se carguen después.
- Un día con 0 días cobrados no guarda fila.
- **Quitar** un servicio que ya tiene días cobrados solo lo **desactiva** (su costo se conserva y sigue apareciendo en los días donde se cobró). Si no tiene días, se borra.
- Columna del resumen según la categoría (`vol.COLUMNA_RESUMEN`): ingeniero de fluidos (2) → *Químicos / Personal DF*; control de sólidos (3) e IFE (4) → *Ingeniero IFE / Control de sólidos*; trailer (5) → *Otros costos*.
- La tabla *Resumen de costos* de la pestaña *Inventario de productos* suma químicos + servicios por categoría.

## 3. Lo anterior que queda

El mecanismo viejo (producto activo **sin unidad** + días en "Usado otro módulo", [pruebas/05](pruebas/05_TRAILER.md)) sigue calculando igual, para no cambiar el costo de los pozos que ya lo usaron. Para lo nuevo se usa la pestaña **Servicios**; los textos de la pestaña 8 ya indican eso.

## 4. Pendiente

- Confirmar con AOS en qué columna del resumen va un servicio de **filtración** (hoy se le elige una de las categorías existentes, por ejemplo control de sólidos). Si hace falta una categoría nueva, se agrega en `vol.CATEGORIAS_COSTO` y `vol.COLUMNA_RESUMEN`.
