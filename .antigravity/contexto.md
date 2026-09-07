# Contexto del proyecto — Sistema de reportes de fluidos de perforación (estilo ONE-TRAX)

## 1. Qué es el proyecto

Sistema propio que replica/estandariza la lógica del software **ONE-TRAX** (M-I SWACO), usado para generar reportes diarios de un pozo petrolero. Varias secciones conectadas entre sí van llenando un mismo reporte. El sistema debe ser **modular y configurable**: no todas las propiedades ni todos los campos aplican siempre; se activan según el tipo de sistema de fluido.

**Stack definido:** Python + Django + PostgreSQL. JavaScript se usará (aunque no era la primera opción) específicamente para la parte de **geometría del pozo**, porque el gráfico debe redibujarse en vivo según los datos ingresados.

**Estrategia de desarrollo acordada:** ir primero por lo fácil/estructural (datos generales, catálogos, propiedades, volumen, cierres) y dejar la geometría interactiva (la parte más compleja, con JS) para el final.

## 2. Archivos de referencia ya revisados

- `Mud_Report_16_PERLA-1X.xlsx` — plantilla real de ONE-TRAX (pozo Perla-1X, operador Cardon IV). Hojas clave: `Synthetic-Based Mud` (reporte de propiedades), `Vol. Info` (balance de volumen), `Equipment` (equipos y costos), `Chem. Inv (DF)` (inventario químico acumulativo). **Es la referencia de campos y fórmulas.**
- `3__INVENTARIO_FISICO_PRODUCTOS_QUIMICOS...xlsx` — inventario físico de productos sólidos y líquidos (columnas: cantidad inicial, entrada, existente, salida, stock final).
- `Standardizing_ONE_TRAX_Wellsite.pptx` — presentación general del sistema ONE-TRAX: Well Information, Marketing Codes, Well Casing Intervals, Well Survey, activación de productos/equipos/mallas, Benchmarks.
- `Standardizing_ONE-TRAX_Side_Track.pptx` — procedimiento de Side Track: fijar Bit Depth en el tope del tapón de cemento, asignar "Volume Not Fluids" al volumen que queda debajo, registrar una transacción de pérdida "Left in Hole", crear el nuevo intervalo de casing, y continuar al día siguiente. **Esta es la base de la lógica de cierre de intervalos.**

## 3. Estructura del reporte (orden de pestañas/secciones)

1. **Datos generales** (encabezado principal): fecha, número de reporte, pozo, operador, ubicación, peso de lodo, etc. Alimenta el encabezado de todo el reporte.
2. **Propiedades** del sistema de fluido (agua, aceite o sintético) — sección **selectiva**, no todas las propiedades aplican a todos los sistemas.
3. **Volumen y geometría del pozo** — la parte más compleja: el gráfico del pozo debe adaptarse en vivo a medida que se ingresan los datos.
4. Balance de volumen / ventana de pérdidas.
5. Ensamblaje de fondo (bottom hole assembly) — relacionado con la ventana de Side Track.
6. Productos/materiales (con costo, código, gravedad específica, libraje).
7. Equipos (código, costo diario, horas usadas).
8. Comentarios.

## 4. Lógica de la matriz de propiedades (selectiva y configurable)

- Existe un catálogo maestro de propiedades posibles (densidad, pH, viscosidad, etc.).
- Cada **tipo de sistema** (agua / aceite / sintético) activa solo un subconjunto de esas propiedades — no todas están siempre presentes.
- Se arma una **matriz** con las propiedades activas para ese sistema; de ahí sale el listado que puede llenarse en el reporte de ese día.
- **Cierre a las 12:00 a.m.**: al cerrar, deben aparecer las propiedades que se necesitaban con su resultado ya cargado; de ahí se genera el reporte del día.

## 5. Lógica de costos

- Los precios **no son fijos**, varían según lo que se use en cada momento.
- El costo debe salir de una **fórmula**, no ingresarse manualmente:
  ```
  costo = cantidad usada × precio unitario
  ```
- El reporte es **acumulativo por día**: dentro del mismo reporte del día se van sumando los usos de la mañana, tarde, etc. (visto en la hoja `Chem. Inv (DF)`: columnas Daily Used / Cum Used / Daily Cost / Cum. Cost).
- Al final del reporte se muestra un costo acumulado (diario + histórico).

## 6. Lógica de inventario (ya construida parcialmente por el usuario)

- El inventario es **acumulativo dentro del mismo día**: si en la mañana se usa un producto y en la tarde se usa otro (o el mismo), ambos aparecen sumados en el mismo reporte del día.
- Estructura actual de la interfaz del usuario:
  - **Sección "Inventario"**: existencia inicial + recepción de productos (el stock del día).
  - **Sección "Uso de Material"**: transacciones individuales de consumo. El reporte va sumando estas transacciones a lo largo del día.
- Relación con el mud report real: `Start Amt` = `Final Stock` del día anterior; `Daily Used` = suma de todas las transacciones de uso de ese día; `Final Stock` = `Start Amt − Daily Used + Daily Rec'd`.

## 7. Fórmulas confirmadas

### 7.1 Volumen generado por material (a partir de libraje y gravedad específica)

```
libraje_final = libraje_unitario × cantidad
volumen (bbl) = libraje_final / (gravedad_específica × 350)
```

El 350 es lb/bbl de agua dulce (8.34 lb/gal × 42 gal/bbl). Si el material se saca, el volumen se resta; si se recibe, se suma. De ahí sale el balance de volumen del día.

### 7.2 Capacidad interna de tubería (bbl)

```
capacidad (bbl) = (ID_tubería² / 1029.4) × longitud
```

### 7.3 Volumen anular (espacio entre hoyo/revestidor y tubería)

```
volumen_anular (bbl) = ((ID_hoyo_o_revestidor)² − (OD_tubería)²) / 1029.4 × longitud
```

**Ejemplo validado en el prototipo:** OD tubería = 5", ID tubería = 4.276", OD hoyo = 7", longitud = 2900 ft →

- Capacidad interna ≈ 51.5 bbl
- Volumen anular (hoyo 7" vs tubería 5") ≈ 67.6 bbl

Unidades de trabajo: **inglesas** (ft, in, bbl, lb).

### 7.4 Categorías estándar de pérdida (catálogo fijo por pozo)

Superficie, tanque, hoyo, shakers, evaporación, centrífuga, formación, dejado en hoyo (Left in Hole), descargado, limpieza de pit. Deben estar estandarizadas para que el balance de volumen siempre cuadre (visto en la hoja `Vol. Info`, sección "Loss Breakdown").

## 8. Cierre volumétrico por intervalo (**tema pendiente de definir en detalle, feedback recibido**)

Un experto revisó la lógica y agregó este punto crítico, aún por formalizar:

> "Se tiene que ver los cierres volumétricos. Cada intervalo se va cerrando, una vez que termines lo cerraste, y así sucesivamente con varios intervalos. Cada intervalo al llegar a su fin se cierra para que arranque el siguiente. Ejemplo: tiene profundidad, lo que se metió de hierro (un revestidor por ejemplo), diámetro externo e interno — eso está en el manual."

**Interpretación acordada (a validar/expandir en la próxima sesión):**

1. Cada intervalo (sección de hoyo entre revestidores, o entre inicio y un side track) es una unidad de control volumétrico independiente con su propio balance.
2. Al terminar un intervalo:
   - Se fija la profundidad final (bit depth / tope de cemento).
   - Se registra la tubería instalada: tipo (revestidor/liner), longitud, diámetro externo, diámetro interno.
   - Se fuerza el **cierre volumétrico**: el volumen que queda atrapado por debajo de esa profundidad ("Volume Not Fluids") se registra como pérdida ("Left in Hole") para que el balance cuadre en cero.
   - El intervalo queda **congelado** (no editable), similar al macro "Save Final Report" del mud report original.
3. El siguiente intervalo **arranca con el volumen final del anterior como su volumen inicial** (Start Volume), y continúa acumulando reportes diarios normalmente.

**Propuesta de modelo de datos (Django) esbozada, pendiente de definir campos completos:**

- `Intervalo`: pozo (FK), número, profundidad inicial, profundidad final, diámetro hoyo/revestidor, estado (`abierto`/`cerrado`), fecha apertura, fecha cierre.
- `TuberiaInstalada`: FK a intervalo, tipo, longitud, OD, ID.
- `CierreVolumetrico`: FK uno-a-uno a intervalo, volumen final por tanque, volumen no fluido, transacción de pérdida generada automáticamente, usuario, timestamp.
- `ReporteDiario`: FK a intervalo (no directamente al pozo) — no debe poder crearse/editarse si el intervalo está cerrado.
- Regla de negocio: una vez `Intervalo.estado = 'cerrado'`, ningún reporte diario de ese intervalo debe ser editable.

## 9. Geometría del pozo (parte compleja, pendiente para el final)

- El gráfico del pozo debe representarse con eje vertical = profundidad (escalado), eje horizontal = diámetro (simétrico respecto a un eje central).
- Cada elemento (casing, tubería, hoyo abierto) es un rectángulo entre su profundidad tope/base, con ancho proporcional a su diámetro.
- Al cambiar cualquier campo (profundidad de asentamiento, diámetro, longitud), el dibujo debe reescalarse recalculando proporciones — no es un dibujo fijo.
- Se construyó un **prototipo interactivo** (HTML/SVG/JS) que demuestra esta lógica: sliders para profundidad total, profundidad de zapata de revestidor, diámetro de hoyo abierto, ID de revestidor, OD e ID de tubería; el esquema se redibuja y calcula en vivo: capacidad de tubería, volumen anular en hoyo abierto, volumen anular en sección revestida, y volumen total.
- Pendiente: extender el modelo a **múltiples intervalos de revestidor apilados** (no solo uno), integrándolo con la lógica de cierre de intervalos de la sección 8.

## 10. Próximos pasos acordados (no completados aún)

1. Definir el modelo de datos completo (entidades, campos, relaciones) para: pozo, reporte diario, intervalo (con su cierre volumétrico), propiedades (matriz selectiva), productos/materiales, equipos, volúmenes/pérdidas.
2. Formalizar la lógica de cierre volumétrico por intervalo (sección 8) con el detalle exacto que confirme el usuario contra el manual mencionado.
3. Diseñar a detalle la ventana de matriz de propiedades selectivas.
4. Al final: implementar la geometría interactiva del pozo en JS dentro de Django (posiblemente vía un canvas/SVG embebido en el template, con endpoints o cálculo en el propio JS).
