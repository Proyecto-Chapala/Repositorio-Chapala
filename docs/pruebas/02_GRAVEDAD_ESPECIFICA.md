# 02 — Gravedad específica

**Punto del doc 23:** 7 · **Migración:** ninguna · **Estado:** sin probar

## Cómo funciona

- Un químico medido en peso aporta volumen al fluido: `volumen (bbl) = libras / (350 × GE)`. El resultado aparece en la volumetría como *Volumen de químicos agregados*.
- En *Productos activos*, un producto con unidad de peso (LBS, KG, TN…) **no se guarda** si le falta el *tamaño de unidad* o la *GE*. El error dice qué producto es y qué dato falta.
- Los productos en volumen (BBL, GAL, L) y los servicios (unidad vacía) no necesitan GE.
- La tabla de inventario de la pestaña 8 tiene la columna **GE**.

## Pasos para verificar

- [ ] **GE obligatoria.** En *Productos activos*, dejar BARITA (LBS) sin GE y guardar → error "BARITA-325: Falta la gravedad específica…".
- [ ] **Tamaño obligatorio.** Tamaño de unidad en 0 y guardar → error "Falta el tamaño de unidad".
- [ ] **Sin GE en volumen.** Un producto en BBL sin GE se guarda sin error.
- [ ] **Columna GE.** En la pestaña 8, la tabla de inventario muestra BARITA con GE 4,20.
- [ ] **Volumen agregado.** Con ticket de entrada cargado, *Agregar químicos* con 10 sacos de 100 lb de BARITA (GE 4,2) → *Volumen de químicos agregados* ≈ **0,68 bbl** (1.000 / 1.470).
- [ ] **Vista previa.** Antes de guardar el movimiento, la ventana de *Agregar químicos* muestra el mismo volumen.

**Notas de la prueba:**
