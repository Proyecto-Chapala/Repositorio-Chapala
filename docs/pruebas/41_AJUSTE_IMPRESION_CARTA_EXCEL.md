# 41 — Ajuste predeterminado de impresión en hoja tamaño Carta (Letter) para reportes de Excel

## Cómo funciona

1. **Ajuste automático a hoja tamaño Carta (Letter):**
   - Todos los reportes generados en Excel por el sistema (`Reporte Diario`, `Reportito de Propiedades` y `Reporte Final Recap`) tienen configurado el tamaño de papel predeterminado como **Carta** (`paperSize = 1`, Letter 8.5" × 11").
   - Se activa la propiedad `fitToPage = True` y se retira cualquier escala fija (`scale = None`), permitiendo que el visor de Excel ajuste automáticamente el zoom de impresión.

2. **Ajuste de ancho y alto (1 página de ancho sin división horizontal):**
   - **Ancho (`fitToWidth = 1`):** Garantiza que todas las columnas de la tabla entren exactamente en una sola página de ancho, eliminando el problema clásico de Excel donde las últimas columnas (como las columnas I, J o M) se desbordan o se cortan hacia una segunda hoja horizontal en blanco.
   - **Alto (`fitToHeight`):**
     - **Hojas de página única (`fitToHeight = 1`):** Hojas de lodo (`Lodo Base Agua`, `Lodo CALDRIL`, `Lodo Base Aceite`, `Lodo Base Sintetica`), `Prop Extra`, `Contabilidad de Volumen`, `Equipos` e `Inventario de Mallas`. Se imprimen completas en exactamente 1 página.
     - **Hojas tabulares o dinámicas (`fitToHeight = 0`):** `Concentraciones`, `Inv Quimico (completo)`, `Reportito de Propiedades` y `Recap del Pozo`. Tienen flujo vertical libre respetando los saltos de página correspondientes por sección o por bloque de 50 productos.

3. **Márgenes optimizados y cuadrícula:**
   - Márgenes estrechos y simétricos (0.3" a 0.4") para maximizar el área de datos y asegurar que el texto sea legible y de aspecto agradable.
   - Cuadrícula (`showGridLines = True`) activada en todas las hojas.

---

## Pasos para verificar

1. **Verificar ajuste de impresión en el Reporte Diario:**
   - [ ] Abrir cualquier reporte diario y pulsar **Descargar Reporte Excel**.
   - [ ] Abrir el archivo `.xlsx` en Microsoft Excel.
   - [ ] Ir a **Archivo → Imprimir** (o presionar `Ctrl + P`).
   - [ ] Verificar en la vista previa de impresión que el papel seleccionado sea **Carta (Letter)**.
   - [ ] Comprobar que la hoja `Lodo Base Agua` (o `Lodo Base Aceite`) quepa completa en **1 sola página**, mostrando todas las columnas (desde la columna A hasta la J) sin columnas cortadas.
   - [ ] Comprobar que la hoja `Inv Quimico (completo)` quepa perfectamente en 1 página de ancho.

2. **Verificar ajuste de impresión en el Reportito de Propiedades:**
   - [ ] Descargar el reportito de propiedades desde el botón **Reporte Excel**.
   - [ ] Presionar `Ctrl + P` y comprobar que la vista previa encaja en tamaño Carta vertical sin cortar columnas de chequeos.

3. **Verificar ajuste de impresión en el Recap del Pozo:**
   - [ ] Entrar al Recap del pozo y exportar a Excel.
   - [ ] Presionar `Ctrl + P` y comprobar que se visualiza en tamaño Carta horizontal (Landscape) ajustado al ancho de página con cuadrícula visible.

