# 03 — Precio por unidad o por barril

**Punto del doc 23:** 8 · **Migración:** `0029_productoactivopozo_cobro_por` · **Estado:** sin probar

## Cómo funciona

- Cada producto activo tiene **un precio** y un selector **Cobrar por: Por unidad | Por barril**.
- *Por unidad* (el valor por defecto, y el que tienen los productos que ya existían): `costo = cantidad × precio`.
- *Por barril*: el sistema calcula cuántos barriles ocupa una unidad del producto.
  - Unidad de volumen: conversión directa (1 BBL = 1 bbl; 42 GAL = 1 bbl).
  - Unidad de peso: con la GE, `tamaño en lb / (350 × GE)`.
  - Con eso, `costo = cantidad × precio por barril × barriles de una unidad`.
- Para cobrar por barril, la unidad tiene que ser de peso o de volumen. Por ejemplo, "SACO" sin peso se rechaza.
- En la pestaña 8, el precio se muestra como "30,00 /bbl" y, al pasar el mouse, el equivalente por unidad.

## Pasos para verificar

- [ ] **Por defecto.** Al activar un producto nuevo, *Cobrar por* = "Por unidad".
- [ ] **Salmuera por barril.** Activar SALMUERA 8.5 con unidad BBL, tamaño 1, precio 30 y *Por barril*. Cargar un ticket de entrada de 100 y agregar 50 → *Costo diario* = **1.500**.
- [ ] **Vista en la pestaña 8.** El precio de la salmuera se ve como "30,00 /bbl".
- [ ] **Peso por barril.** Producto en LBS, tamaño 100, GE 1,0, precio 350, *Por barril*: usar 1 saco → costo = **100** (100 lb ocupan 0,2857 bbl).
- [ ] **Unidad inválida.** Unidad "SACO" sin GE y *Por barril*, guardar → error "Para cobrar por barril la unidad tiene que ser de peso… o de volumen…".
- [ ] **Productos viejos.** Los productos que ya estaban activos antes de la 0029 aparecen en "Por unidad" y mantienen sus costos.

**Notas de la prueba:**
