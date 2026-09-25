# Manual de usuario — Reportes diarios de fluidos de perforación

Guía para los ingenieros de fluidos de AOS. Sigue el orden real de trabajo: crear el pozo, configurarlo una vez y luego llenar el reporte cada día.

> Deje abierta la ventana negra del servidor mientras use el sistema. Si una pantalla no refleja un cambio, recargue con `Ctrl + F5`.

---

## Parte 1 — Crear un pozo (una sola vez)

### 1.1 Asistente de nuevo pozo

Barra lateral → 🏗️ **Nuevo Pozo**. Son 4 pasos; cada **Guardar y Continuar** deja el avance guardado (si cierra la ventana, el pozo queda como borrador y se retoma desde la lista de pozos).

| Paso | Qué llenar | Cuidado |
|---|---|---|
| 1 Datos básicos | Nombre del pozo. Opcional: usar un pozo anterior como plantilla | El nombre no se puede repetir |
| 2 Unidades | Sistema de unidades | **No se puede cambiar después** |
| 3 Financiero | Moneda, decimales, % de impuesto, ecuaciones de sólidos (M-I o API), categorías de pérdida | La **moneda no se puede cambiar después**; el impuesto sí |
| 4 Confirmar | Revise el resumen y pulse **Crear Pozo** | |

### 1.2 Fecha de inicio (Spud Date)

La primera vez que abra el pozo aparece esta pantalla. Escriba la **primera fecha de datos** y el **tipo de fluido del primer chequeo** y pulse **Confirmar**.

> Aparece **una sola vez**. La fecha y el tipo de fluido no se pueden corregir después.

---

## Parte 2 — Configurar el pozo (antes del primer reporte)

Barra lateral → 💧 **Pozos** → elija el pozo. Se abre la **pantalla principal del pozo**. Complete estas tarjetas en este orden:

1. **Información General del Pozo** — operador, campo, taladro, ingenieros, **fecha de Spud** (la usa el reporte), temperatura de superficie y gradiente (para la hidráulica de 5ª edición). Si es costa afuera: Air Gap, profundidad de agua, temperatura del lecho marino y, si hay riser, su diámetro interno. Luego la pestaña **Códigos de Mercadeo**.
2. **Intervalos de Revestimiento (Costo)** — un intervalo por revestidor: diámetro interno (ID), profundidad de la zapata, diámetro de hoyo, tope de liner si es liner, días y longitud planeados. **Sin el ID y la zapata, los volúmenes del hoyo salen mal.**
3. **Información de Fosas** — cada fosa o tanque con número, nombre y capacidad (bbl).
4. **Configuración de Pérdidas** — revise las categorías (vienen 15 cargadas).
5. **Productos / Equipos / Mallas Activos** — elija del catálogo lo que se va a usar en este pozo:
   - **Productos**: precio, **unidad**, tamaño de unidad (por ejemplo, 55 para sacos de 55 lb con unidad `LB`), gravedad y **Código de Costo Diario** (1 Químicos, 2 Ingeniero de fluidos, 3 Ingeniero de control de sólidos, 4 Ingeniero IFE). Deje la unidad vacía solo para servicios (días de ingeniero).
   - **Equipos**: número de serie (obligatorio), descripción, precio de renta y de stand-by.
   - **Mallas**: precio y % de descuento.
6. **Configuración de Propiedades de Equipo** — qué datos se anotan cada día por tipo de equipo.
7. **Configuración de Benchmark** — parámetros a vigilar y valores objetivo (opcional).
8. **Configuración General** — impuesto, ¿usar hidráulica API 5ª edición?, **almacenes** y actividades de **distribución de tiempo**.

Los equipos, mallas, componentes de sarta, propiedades de equipo y parámetros de benchmark que no existan se crean antes en 🗂️ **Catálogos Maestros** (barra lateral). Los productos nuevos se crean en 📦 **Inventario**. En Catálogos Maestros, a los equipos que llevan mallas (zarandas) hay que ponerles el **número de posiciones de malla**.

---

## Parte 3 — El reporte diario

Pantalla principal del pozo → **Fluidos de Perforación y Equipos**. Se abre el historial de reportes.

### 3.1 Crear el reporte del día

1. **+ Nuevo Reporte**.
2. La fecha sugerida es el día siguiente al último reporte (o la fecha de Spud si es el primero). El tipo de lodo sugerido es el del último reporte.
3. Deje marcado **copiar datos del reporte anterior** para no volver a escribir profundidad, representantes y teléfonos.
4. Se abre el reporte con 8 pestañas. Arriba: flechas para ir al primer, anterior, siguiente y último reporte y el botón para **descargar el Excel**.

> **Primer reporte del pozo**: el sistema llena las bombas, la mecha, las boquillas y los 4 chequeos de lodo con **valores de ejemplo**. Reemplácelos por los reales (o bórrelos) ese mismo día; si no, se copian a los días siguientes.

### 3.2 Pestaña 1 — General

Profundidad, TVD, **profundidad de la mecha**, actividad, tipo de fluido y litología. Representantes y teléfonos. Pulse **Guardar**.

- **Configuración de Litología**: topes de formación del pozo.
- **Registro Direccional (Survey)**: estaciones MD, inclinación y azimut; el sistema calcula TVD, DLS y sección vertical.
- El cuadro **Balance Económico** muestra el costo del día y acumulado (se llena solo con las pestañas 6 y 8).

### 3.3 Pestaña 2 — Bombas y mecha

- Por bomba: camisa, carrera, eficiencia, **spm** y si está **en reporte**. El caudal se calcula solo.
- En "Marca y Modelo" puede elegir de la lista (al hacer clic se muestran todos los modelos) o escribir cualquier texto.
- Mecha: diámetro y **% de lavado** (el diámetro de hoyo con lavado se calcula al guardar).
- Boquillas: tamaño en 32avos y cantidad (el TFA se calcula).
- Parámetros de perforación, presión de bomba y datos de equipo de superficie.

### 3.4 Pestaña 3 — Propiedades del lodo

- Hasta 4 chequeos. Marque cuál es el **principal** (el que se imprime y usa la hidráulica).
- Escriba las lecturas del viscosímetro: **PV y YP se calculan solos** con R600 y R300.
- Con la retorta (agua, aceite, sólidos), cloruros, MBT y los datos de sal, el sistema calcula el **análisis de sólidos** (LGS, HGS, bentonita, sólidos perforados...). En lodo base aceite, un valor negativo indica que los datos de retorta no son coherentes: revise la medición.
- Propiedades extra: las etiquetas se configuran en el historial de reportes ("Etiquetas de Propiedades Extra").

### 3.5 Pestaña 4 — Geometría del pozo

1. Elija el **intervalo de costo** del día.
2. Arme la **sarta desde la mecha hacia arriba** (la primera fila es la mecha). Puede elegir componentes del catálogo; los diámetros se llenan solos y se pueden cambiar.
3. Si la sarta es la misma de ayer, use **heredar la sarta del reporte anterior** y ajuste la longitud de la tubería.
4. Guarde. Abajo aparecen los volúmenes (sarta, anular, bajo la mecha, total) y el tiempo de fondo arriba.

Si aparece "la sarta no llega a la mecha: faltan X ft", ajuste la longitud de la tubería de perforación.

### 3.6 Pestaña 5 — Comentarios

- **Especificación de lodo** (rango objetivo): se copia sola del día anterior.
- **Resumen del Día**: **una sola línea** (va al Recap del pozo). Arriba se ve el resumen de ayer como guía.
- **Observaciones y tratamiento** y **observaciones de operaciones** (hoja IADC).

### 3.7 Pestaña 6 — Control de sólidos

**Mallas** (en este orden):

1. **Ticket de recepción** con las mallas que llegaron (nuevas y usadas, cantidad según papel y cantidad real).
2. **Movimientos**: instalar malla nueva o usada en una posición de un equipo, pasar al almacén, desechar. Instalar una malla nueva carga su precio al costo del día.
3. Si se equivocó, **Deshacer último** (solo el último movimiento del pozo).

El sistema no deja instalar sin stock ni en una posición ocupada, y avisa qué día y qué malla causan el problema.

**Equipos**: por cada equipo, horas, lodo en recortes, % de recortes, tipo de pérdida (y caudal y densidades si es centrífuga); cantidad usada y código de cobro; horas de parada y observaciones. El sistema calcula lo descargado y el lodo perdido.

### 3.8 Pestaña 7 — Distribución de tiempo

Reparta las horas del día entre las actividades. Las 4 primeras siempre aparecen; agregue otras de la lista. Si el total no coincide con las horas del período se marca en **rojo**, pero puede guardar igual. Cambie las **horas del período** solo el primer día, el último o si cambia la hora de corte.

### 3.9 Pestaña 8 — Inventario / Hidráulica / Concentraciones

**Orden recomendado cada día:**

1. **Ticket de productos** con lo que llegó a la locación (y los de devolución), como registro. No cambia la existencia.
2. **Movimientos** del día:
   - ⚗ **Agregar químicos**: fosa, fluido base, agua y cantidades de productos.
   - 🛢 **Agregar lodo entero**: fosa, volumen, peso, producto de lodo y sus concentraciones.
   - ⇆ **Transferencia / pérdida**: entre fosas, devolución (a dónde) o pérdida (tipo).
3. **Volúmenes de fosas**: tipo de cada fosa y **volumen real medido** al cierre, peso y temperatura. Indique cuánto volumen del hoyo no es fluido del sistema, si aplica.
4. Revise el **Balance de volumen**: el "no contabilizado" debería quedar cerca de 0. **No cambie el volumen real para cuadrar**: si no cuadra, falta registrar algún movimiento o pérdida.
5. **Inventario de productos**: revise existencias; use "usado en otro módulo", "ajuste" o "en pedido" si hace falta.

La existencia que se ve es la de la pantalla **Inventario** (una sola para todos los pozos). Al agregar químicos o lodo, se descuenta de ahí; si se deshace el movimiento o se borra el reporte, vuelve. Si un producto aparece en 0, cargue su cantidad en Inventario.

Consultas:

- **Concentración de productos** (lb/bbl) en el sistema activo y en cada fosa.
- **Hidráulica**: elija 4ª o 5ª edición. Muestra pérdidas de presión, velocidades, régimen de flujo, ECD, HHP, HSI y la diferencia con la presión de bomba real. Si falta algún dato, dice cuál y en qué pestaña.
- **Evaluación de benchmark**: objetivos contra valores medidos.

⚙ **Pérdidas del reporte**: elija las (máximo) 10 categorías de pérdida que salen impresas. Se hace una vez por pozo.

### 3.10 Descargar el Excel

Botón **Excel** en la barra superior del reporte. Genera el libro con el formato ONE-TRAX en español: reporte de lodo (según el tipo de lodo), propiedades extra, contabilidad de volumen, inventario químico (tres hojas: DF, por nombre y completo), equipos e inventario de mallas. Las hojas sin datos (inventario, equipos o mallas) no se incluyen.

---

## Errores frecuentes y qué hacer

| Mensaje o síntoma | Qué hacer |
|---|---|
| "Registra primero el ticket de recepción" (mallas) | Registre en la pestaña 6 el ticket de las mallas que llegaron, en ese día o antes |
| "Inventario de X: hay N y se necesitan M" | No alcanza la existencia: actualice la cantidad en la pantalla Inventario |
| "La posición X del equipo Y ya tiene..." | Retire primero la malla que está (pasar al almacén o desechar) |
| "... no tiene tipo asignado (o es 'Vacía')" | En Volúmenes de fosas, ponga el tipo de la fosa ese día |
| "El último movimiento del pozo (#N) es del reporte del ..." | Vaya a ese reporte para deshacerlo |
| Un producto en 0 en la pestaña 8 | Su cantidad en la pantalla Inventario es 0, o no tiene unidad en Productos Activos (se trata como servicio) |
| Volúmenes del hoyo en 0 | Falta la profundidad de la mecha (pestaña 1), la sarta (pestaña 4) o los intervalos de revestimiento |
| La hidráulica dice que faltan datos | Complete lo que indica: caudal y boquillas (2), chequeo principal con reología y peso (3), sarta (4) |
| "Ya existe un reporte para esa fecha" | Solo puede haber un reporte por día y pozo |
