# 13 — Reporte de propiedades (reportito): comentario guardado y Excel

**Punto del doc 23:** 16 · **Migración:** `0032_comentario_propiedades` · **Estado:** sin probar · **Requiere:** prueba [12](12_PROPIEDADES_EXTRA.md)

## Cómo funciona

- **Decisión del usuario:** las propiedades se cargan **en la pestaña 3**, que ya tiene las 4 pruebas, el **punto de muestreo** (flow line, succión…) y la **hora** que elija el ingeniero (por ejemplo 10:00). El reportito no es una segunda pantalla de edición: muestra lo de la pestaña 3, así que no hay datos duplicados.
- Barra de arriba del reportito:
  - **Editar propiedades**: abre el reporte directamente en la pestaña 3 (`?pestana=3`).
  - **Guardar comentario**: el comentario para el Company Man **se guarda**. Antes se perdía al cerrar la página. Al volver a abrir el reportito, sigue ahí.
  - **Descargar Excel**: guarda el comentario y descarga el reportito en Excel, aparte del reporte general. Lleva logo AOS, datos del pozo, propiedades por chequeo (con "Muestra / hora" y las propiedades extra), especificación del lodo y comentario.
  - **Imprimir / Guardar PDF**: igual que antes. El comentario sale completo, y si está vacío no se imprime el recuadro.
- El comentario del reportito es independiente de los comentarios de la pestaña 5.

## Pasos para verificar

Preparación: correr `python manage.py migrate` (aplica la 0032). Un reporte con propiedades cargadas en la pestaña 3.

- [ ] **Muestra y hora.** En la pestaña 3, prueba #2: punto de muestreo "Succión", hora **10:00**, guardar. En el reportito, la fila "Muestra / hora" dice "Succión 10:00" en el chequeo #2.
- [ ] **Editar propiedades.** En el reportito, pulsar "Editar propiedades" → se abre el reporte **en la pestaña 3**.
- [ ] **Guardar comentario.** Escribir un comentario y pulsar "Guardar comentario" → "Comentario guardado.". Recargar la página → el comentario sigue.
- [ ] **Aviso sin guardar.** Modificar el comentario → la barra dice "Comentario sin guardar.".
- [ ] **Excel.** Pulsar "Descargar Excel" → se descarga `Propiedades_<n>_<pozo>_<fecha>.xlsx` con logo, datos del pozo, la tabla de propiedades (incluida "Muestra / hora" y las propiedades extra con valor), la especificación (si hay) y el comentario.
- [ ] **El Excel guarda el comentario.** Cambiar el comentario y descargar el Excel sin pulsar Guardar → el Excel trae el comentario nuevo y, al recargar, sigue guardado.
- [ ] **PDF.** "Imprimir / Guardar PDF" → el comentario sale completo, sin cortarse. Sin comentario, el recuadro no aparece.
- [ ] **Pestaña 5 intacta.** Los comentarios de la pestaña 5 no cambian al guardar el del reportito.

**Notas de la prueba:**
