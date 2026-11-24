# 40 — Productos usados en reporte de lodo, hoja única de inventario y rediseño visual en Excel

## Cómo funciona

1. **Productos usados en hoja de Lodo (filas 19 a 33):**
   - En la sección **PRODUCTOS USADOS Últ. 24 h** de la hoja del lodo (`Lodo Base Agua`, `Lodo CALDRIL`, `Lodo Base Aceite` o `Lodo Base Sintetica`), se calcula la cantidad consumida considerando tanto lo asentado en la tabla de inventario (`usado_fluido`) como lo dosificado en los tanques de lodo (`agregado_balance`).
   - Las filas sin productos (entre la fila 19 y la 33) y las filas sin equipos (filas 36 a 46) se limpian dejándolas en blanco (`None`), eliminando los residuos de ceros (`0 | 0 | 0`) heredados de la plantilla ONE-TRAX.

2. **Hoja única de inventario químico:**
   - Se mantiene la hoja única de inventario del pozo: **`Inv Quimico (completo)`**, consolidando todos los productos activos y con movimiento en la locación.
   - Las hojas redundantes o vacías (`Inv Quimico (DF)` e `Inv Quimico (por nombre)`) se eliminan del libro para evitar hojas repetidas.

3. **Rediseño visual elegante:**
   - **Colores en pestañas de Excel:** Las hojas generadas tienen un código cromático profesional:
     - Hoja de Lodo principal: Azul Marino Corporativo (`#1E3A8A`)
     - Propiedades extra: Azul Cobalto (`#2563EB`)
     - Contabilidad de Volumen: Verde Aguamarina / Teal (`#0D9488`)
     - Concentraciones: Celeste Hidráulico (`#0284C7`)
     - Inv Químico (completo): Verde Esmeralda (`#059669`)
     - Equipos: Púrpura (`#7C3AED`)
     - Inventario de Mallas: Índigo (`#4F46E5`)
   - **Cuadrícula activa:** Se asegura `showGridLines = True` en todas las hojas para una visualización cómoda y estructurada.

---

## Pasos para verificar

1. **Verificar productos usados en la hoja del lodo:**
   - [ ] Abrir o crear un reporte diario y registrar consumo de químicos (por ejemplo, 10 sacos de Barita en *Usado en Fluidos* o dosificados en un tanque en *Volumetría*).
   - [ ] Descargar el reporte en Excel (`Descargar Reporte Excel`).
   - [ ] Abrir el archivo `.xlsx` y ubicarse en la primera pestaña (`Lodo Base Agua`).
   - [ ] Verificar que en las filas 19 a 33 aparezca la descripción del producto, el empaque y la cantidad exacta consumida (ej. `10.00`).
   - [ ] Comprobar que las filas restantes de la tabla estén limpias sin ceros residuales.

2. **Verificar la hoja única de inventario químico:**
   - [ ] En el mismo libro descargado, observar las pestañas del documento.
   - [ ] Comprobar que existe una única pestaña de inventario químico: **`Inv Quimico (completo)`**.
   - [ ] Confirmar que **no** aparecen las pestañas vacías `Inv Quimico (DF)` ni `Inv Quimico (por nombre)`.

3. **Verificar estética y cuadrículas:**
   - [ ] Constatar que las pestañas inferiores del libro de Excel muestren sus colores corporativos respectivos.
   - [ ] Verificar que las líneas de división (gridlines) estén activas y visibles en todas las hojas.
