# Manual de usuario — Smart Mud

**All Oil Services, C.A. (AOS)** · Sistema de reportes de fluidos de perforación y equipos

Este manual explica, paso a paso, cómo usar el sistema: desde crear un pozo hasta llenar y descargar el reporte diario y el reporte final del pozo. Si una palabra no es clara, búscala en el [glosario](17_GLOSARIO.md). Para dudas comunes, mira las [preguntas frecuentes](18_PREGUNTAS_FRECUENTES.md).

---

## Contenido

1. [Abrir el sistema](#1-abrir-el-sistema)
2. [Conocer la pantalla](#2-conocer-la-pantalla)
3. [Preparar los catálogos (una sola vez)](#3-preparar-los-catálogos-una-sola-vez)
4. [Crear un pozo nuevo](#4-crear-un-pozo-nuevo)
5. [Configurar el pozo](#5-configurar-el-pozo)
6. [El reporte diario](#6-el-reporte-diario) (incluye [casos especiales: side track y hoyo piloto](#66-casos-especiales-side-track-y-hoyo-piloto))
7. [Rutina diaria recomendada](#7-rutina-diaria-recomendada)
8. [Reportes que se entregan](#8-reportes-que-se-entregan) (Excel diario, reporte de propiedades, reporte final del pozo)
9. [Inventario del almacén](#9-inventario-del-almacén)
10. [Consejos y errores comunes](#10-consejos-y-errores-comunes)

---

## 1. Abrir el sistema

**Versión instalada (`SmartMud.exe`)** — la que usan los ingenieros:
1. Doble clic en **`SmartMud.exe`**. Se abre el navegador con el sistema. **No aparece ninguna ventana negra.**
2. El sistema queda funcionando con un **ícono de gota** junto al reloj de Windows (si no se ve, pulsa la flechita ^ al lado del reloj). Doble clic en la gota vuelve a abrir el navegador.
3. Para **salir**: clic derecho en la gota → **Salir**.
4. La primera vez pide la **clave de activación** (la entrega el programador).

> Si algo falla aparece un cuadro con el error. Envía al programador el archivo `datos\smartmud.log`, junto a `SmartMud.exe`.

**Versión de desarrollo** (en la PC del programador): doble clic en `Iniciar Sistema.bat`; ahí sí se usa la ventana negra del servidor. Ver [instalación](01_INSTALACION_Y_EJECUCION.md).

## 2. Conocer la pantalla

A la izquierda está la **barra lateral**. El botón de arriba la contrae y expande, y el sistema recuerda tu preferencia.

| Opción | Para qué |
|---|---|
| 💧 **Pozos** | Lista de pozos. Desde aquí entras a cada pozo |
| 📦 **Inventario** | Productos químicos del **almacén** |
| 🏗️ **Nuevo Pozo** | Crear un pozo |
| 🗂️ **Catálogos Maestros** | Equipos, mallas, componentes de sarta, propiedades y parámetros de benchmark, compartidos por todos los pozos |

Los mensajes de confirmación o de error aparecen como avisos flotantes en una esquina. **Léelos**: dicen exactamente qué falta o qué está mal.

**Números redondeados.** Como se reporta en campo, los **volúmenes** calculados se muestran **sin decimales** (1325 bbl, no 1324,87), la **densidad** con 1 decimal y los **costos** con sus centavos. Las diferencias que hay que vigilar (el *No contabilizado*) y los volúmenes de cada tanque llevan 1 decimal para no esconder diferencias pequeñas. En las tarjetas de volumen de la pestaña 4, pasa el ratón sobre el número para ver el valor exacto.

## 3. Preparar los catálogos (una sola vez)

Antes del primer pozo, carga los **Catálogos Maestros** (menú → *Catálogos Maestros*). Cada pestaña tiene la lista a la izquierda y el formulario a la derecha.

1. **Equipos**: código, nombre, tipo (zaranda, centrífuga, limpiador de lodo…) y **posiciones de malla** (cuántas mallas lleva: 0 a 12; con 0 no lleva mallas).
2. **Mallas de zaranda**: código, descripción y mesh.
3. **Componentes de sarta**: mechas, drill collars, heavy weight, drill pipe… con su OD, ID y, en tuberías, los datos de la **junta** (OD, ID y largo). El largo del tramo es 31 ft por defecto.
4. **Propiedades de equipo**: propiedades que se pueden registrar por tipo de equipo (por ejemplo, velocidad del tazón de la centrífuga).
5. **Parámetros de benchmark**: por ejemplo "Mud Weight (WBM)" o "PV (OBM)". Usa palabras como *peso del lodo, PV, YP, filtrado, MBT, cloruros, pH*: así el sistema los compara solo contra los chequeos de lodo.

Para crear: **+ Nuevo**, llena el formulario y **Guardar**. Para editar: haz clic en la fila. Para borrar: selecciona la fila y pulsa **Eliminar** (no se puede si ya se usa en algún pozo).

Los **productos químicos** se cargan en **Inventario** (sección 9).

## 4. Crear un pozo nuevo

Menú → **Nuevo Pozo**. Son 4 pasos. Todo se guarda solo a medida que avanzas: si cierras a medias, el pozo queda en **borrador** y puedes continuarlo después desde la lista de pozos.

**Paso 1 — Datos básicos.** Escribe el **nombre del pozo** (no puede repetirse). Si quieres, elige un **pozo anterior como plantilla**: se copian sus unidades, moneda, categorías de pérdida, tanques y productos, equipos y mallas activos (no sus reportes).

**Paso 2 — Unidades.** Elige el sistema de unidades. *Standard Oilfield* es el habitual. Con *Personalizado* eliges la unidad de cada propiedad.

> Por ahora el sistema calcula y muestra todo en unidades de campo (ft, in, bbl, gpm, lb/gal, psi), sea cual sea el sistema elegido. Las concentraciones se pueden ver también en kg/m³.

**Paso 3 — Financiero.** **Moneda** (se elige de la lista: dólar, bolívar, euro, pesos, real…), decimales, **% de impuesto**, ecuaciones de sólidos (**API**) y el juego de **categorías de pérdida** (*Estándar*, Statoil… o *Personalizado*).

**Paso 4 — Confirmar.** Revisa el resumen y confirma. **Después de confirmar, las unidades ya no se pueden cambiar.**

### Pantalla "Fecha inicial" (solo la primera vez)

Al abrir el pozo por primera vez aparece esta pantalla:
- **Fecha de primera captura**: obligatoria.
- **Tipo de fluido inicial**: base agua, base agua CaCl2, base aceite, base sintética o completación. Obligatorio.
- ¿Con tratamiento y disposición? · N° de control LOGIT (opcional).

> ⚠ **Revisa bien antes de confirmar**: la fecha y el tipo de fluido **no se pueden cambiar después**.

## 5. Configurar el pozo

Entra al pozo (menú → **Pozos** → el pozo). Verás la **pantalla principal** con tarjetas, ya en el orden en que conviene llenarlas:

### 5.1 📋 Información General del Pozo
Operador, campo, ubicación, contratista, taladro, ingenieros, fechas, profundidad total, **temperatura de superficie y gradiente** (los usa la hidráulica) y comentarios. En la segunda pestaña van los **códigos de mercadeo**.
- **Offshore**: si lo marcas, debes llenar *Air Gap*, *Water Depth* y *Sea Floor Temp*.
- **Riser**: solo offshore. Es obligatorio su **diámetro interno**. Si no pones la longitud, se usa *Air Gap + Water Depth*.
- Los **ingenieros** que pongas aquí salen como representantes en el primer reporte diario y en el reporte final.

### 5.2 🧾 Configuración General
- **Moneda** del pozo (lista de monedas comunes). Cambiarla solo cambia el símbolo; no convierte montos.
- **Cobro en una segunda moneda (opcional)**: para contratos que se cobran parte en una moneda y parte en otra (ej. dólares y bolívares). Elige la segunda moneda, la **tasa de cambio** (unidades de la segunda moneda por 1 de la del pozo) y el **% cobrado** en ella. Los costos se siguen cargando en la moneda del pozo; la pantalla de costos del reporte muestra cuánto cobrar en cada una (día y acumulado).
- Impuesto, **usar API 5ª edición en hidráulica** (recomendado) y ecuaciones de sólidos (API).
- **Códigos de almacén**: crea al menos uno (por ejemplo, "ALM-01 – Almacén Principal"). Se usan en los tickets.
- **Distribución de tiempo**: ya vienen 20 actividades. Puedes agregar más.

### 5.3 🛢️ Intervalos de Revestimiento (Costo)
Una fila por revestidor: tipo, **OD e ID**, diámetro de hoyo, **profundidad**, tope del liner (si es liner), días y costos planeados. **Sin intervalos, los volúmenes del hoyo no se pueden calcular bien.**
- Cada intervalo está **Abierto** (se está perforando) o **Cerrado**. **No se puede crear el siguiente mientras el anterior siga abierto.**
- Cuando se baja el revestidor: abre el intervalo, completa sus datos (al menos tipo y profundidad), **Guardar** y luego **Cerrar intervalo**. Recién ahí se habilita **+ Nuevo**.
- Si se cerró por error, **Reabrir intervalo** (solo el último).

Si el pozo tiene un desvío, se crea un intervalo de tipo **Side Track (desvío)** (ver 6.6). Las **observaciones y recomendaciones** y los **comentarios para el recap** de cada intervalo salen en el reporte final del pozo.

### 5.4 🪣 Información de Tanques
- **Tanques**: número, nombre y capacidad (bbl) de cada tanque (ej. Tanque activo, Reserva 1, Reserva 2, Retorno, Mezcla).
- **Tipos de tanque**: ya vienen los 7 estándar (Vacía, **Activa**, **Reserva**, **Premix**, Espaciador, Píldora, Rompedor). Puedes agregar otros.

### 5.5 🧰 Productos / Equipos / Mallas Activos
Aquí eliges **qué se usa en este pozo** y **a qué precio**. **Doble clic** sobre una fila del catálogo la pasa a la lista activa (o usa el botón +).
- **Productos**: elige el producto del inventario y define su **unidad** (por ejemplo LB, KG, GAL, BBL), su **tamaño** (por ejemplo 100 si es un saco de 100 lb), su **precio**, su gravedad específica, si se le **calcula concentración** y su **código de costo** (1 Químicos, 2 Ingeniero de fluidos, 3 Ingeniero de control de sólidos, 4 Ingeniero IFE).
  > Si dejas la **unidad vacía**, el producto se trata como un **servicio** (por ejemplo, días de ingeniero): suma costo, pero no lleva existencias.
  > Para que un producto salga en el reporte de **concentraciones** debe medirse en **peso** (LB, KG, TN…), tener su **tamaño** y tener marcado *calcular concentración*: así el sistema sabe cuántas libras tiene cada saco.
- **Equipos**: elige el equipo, pon su **número de serie** (obligatorio) y las tarifas de **renta** y **standby**.
- **Mallas**: elige la malla, su **precio** y el **% de descuento**.

Pulsa **Guardar** en cada pestaña.

### 5.6 📉 Configuración de Pérdidas
Vienen las categorías estándar (zarandas, centrífuga, evaporación, perdido en formación, **detrás del revestimiento / en el hoyo**…). Edita si hace falta.

### 5.7 ⚙️ Propiedades de Equipo (opcional)
Marca qué propiedades quieres registrar por tipo de equipo.

### 5.8 📊 Benchmark (opcional)
Elige los parámetros a vigilar y pon sus objetivos (valor, mínimo o máximo) para todo el pozo o por intervalo.

### 5.9 🗑️ Eliminar un pozo
Si un pozo se empezó mal: pantalla principal del pozo → **Eliminar pozo** (arriba a la derecha) → escribe el **nombre exacto** del pozo → **Eliminar definitivamente**. Se borra todo (configuración, intervalos, tanques y reportes) y **no se puede deshacer**. Lo que consumieron sus reportes vuelve al inventario general.

## 6. El reporte diario

Pantalla principal del pozo → tarjeta **💧 Fluidos de Perforación y Equipos**.

### 6.1 El hub (historial)
Esta página **solo sirve para crear el reporte del día y abrir los anteriores**: no se edita ni se borra nada aquí. Muestra todos los reportes del pozo con fecha, profundidad, actividad y tipo de lodo.

Las **etiquetas de propiedades extra** del lodo (una sola vez por pozo) están **bloqueadas**: para cambiarlas pulsa **Modificar etiquetas**, edita y **Guardar Etiquetas** (se vuelven a bloquear).

### 6.2 Crear el reporte del día
1. **+ Nuevo Reporte**.
2. **Fecha**: usa **Hoy** o elige otra fecha. Solo un reporte por día.
3. **Tipo de fluido** del día.
4. **¿Copiar datos del día anterior?** → **Sí** (recomendado): trae profundidades, actividad, representantes y teléfonos.
5. **OK (Crear Reporte)**.

Las bombas, la barrena, los chequeos de lodo, los comentarios y el tiempo también se traen del día anterior la primera vez que abres cada pestaña. Solo tienes que **actualizar lo que cambió**.

### 6.3 Las 8 pestañas

Cada pestaña tiene su botón **Guardar**. **Guarda antes de cambiar de pestaña.** Las excepciones son la pestaña 6 (mallas) y los movimientos de la 8, que se guardan al instante.

#### Pestaña 1 — General
- Actividad, **profundidad (MD)**, **TVD**, **profundidad de la barrena**, tipo de fluido y litología.
- Botones de **Litología / topes de formación** y **Registro direccional (survey)**. Son del pozo, no del día. En el survey carga MD, inclinación y azimut; el sistema calcula TVD y DLS. **Empieza el survey con una estación en MD 0.**
- Representantes y teléfonos.
- **Balance económico**: costos del día y acumulados. El botón de detalle muestra de dónde sale cada costo.

#### Pestaña 2 — Bombas / Barrenas
- **Bombas**: modelo (bórralo y haz clic para ver toda la lista de sugerencias), camisa, carrera, eficiencia y **SPM**. Marca **"en el reporte"** las que están trabajando. El caudal se calcula solo.
- **Boquillas**: tamaño en 32avos y cantidad. El **TFA** se calcula solo.
- **Barrena**: tamaño, **washout**, datos de perforación (RPM, WOB, ROP), **presión de bomba** y datos del equipo de superficie (código 1-4 o presión de referencia).

#### Pestaña 3 — Propiedades del lodo
- Hasta **4 chequeos** por día. El **#1 es el principal** (el último del día): es el que usan la hidráulica y el Excel.
- Llena densidad, embudo, **lecturas R600 a R3** (PV y YP se calculan), geles, filtrados, **retorta** (sólidos, aceite, agua), química (pH, cloruros, MBT…) y las propiedades extra.
- El **análisis de sólidos** (LGS, HGS, bentonita, sólidos perforados) se calcula solo.
  > Si el lodo lleva **carbonato de calcio (CaCO₃)** en base agua, escribe sus lb/bbl estimadas en **Concentración química**; si no, se reporta como sólido perforado. En base aceite, el %LGS "alto" incluye el carbonato.
- Botón **Reporte de Propiedades**: un reporte corto **solo del lodo** para entregar un avance al compañero antes del reporte completo (ver 8.2).

#### Pestaña 4 — Geometría del pozo
- **Sarta**: se carga **desde la mecha hacia arriba** (fila 1 = mecha). Elige cada componente del catálogo y pon su **longitud**. Con **"Heredar del día anterior"** copias la sarta de ayer.
- **Contexto del pozo**:
  - **Intervalo de costo** del día (el revestidor que se está perforando).
  - **Hoyo piloto**, si se está ampliando un hoyo más pequeño (ver 6.6).
  - **Side track**, solo el día en que arranca un desvío (ver 6.6).
- **Volúmenes del hoyo**: se calculan solos (sarta, anular, bajo la mecha, total, desplazamiento, fondo arriba en emboladas y minutos) y el **hoyo perforado** del día (bbl y ft), que se actualiza al guardar. Las tarjetas muestran enteros; el valor exacto está en el tooltip y en el desglose por sección.

#### Pestaña 5 — Comentarios
- **Especificación del lodo**: el **rango objetivo** acordado (ej. "11.5-12.0"), no el valor medido.
- **Resumen del día** (sale en el recap diario del reporte final), **observaciones y tratamiento**, y **observaciones del día**.


#### Pestaña 6 — Control de sólidos
**a) Inventario de mallas.** Aquí se registran los **tickets**:
1. **Nuevo ticket** → tipo (por ejemplo, *Recepción desde almacén*), número, almacén y personas.
2. Por cada malla: cantidades **nuevas** y **usadas**, "según ticket" y **"real"** (lo que llegó de verdad; es lo que cuenta).

**b) Transacciones de mallas.** Por cada equipo y posición:
- **Instalar nueva** (descuenta del stock de nuevas y **suma el costo** de la malla), **Instalar usada**, **Pasar al almacén**, **Desechar del equipo**, **Desechar del almacén**.
- **Deshacer**: solo la última transacción del pozo, y solo desde su reporte.

> Si no hay mallas en stock, el sistema **no deja instalar**. Registra primero el ticket de recepción.

**c) Detalle y uso de equipos.** Por cada equipo: horas, **MOC**, % de recortes (zarandas, limpiador, secador) o caudal y densidades (centrífuga), **tipo de pérdida**, cobro (**completo**, **standby** o **sin cobro**), horas de parada y observaciones. Se calcula el volumen descargado y el lodo perdido a partir del **hoyo perforado** del día. **Guarda** al terminar.

**d) Opcionales**: Observaciones IFE, análisis de sólidos por equipo y retención en recortes. Solo si los necesitas.

#### Pestaña 7 — Distribución de tiempo
- **Horas del período** (normalmente 24).
- Pon las horas de cada actividad según la hoja IADC. Las 4 principales (alistamiento, perforación, viajes, tiempo no productivo) siempre aparecen. Agrega otras desde la lista.
- Si el total no da las horas del período, sale **en rojo**, pero se puede guardar.

#### Pestaña 8 — Inventario / Hidráulica / Concentraciones

**a) Volumetría e inventario.** Es la pestaña más importante del cierre del día:

1. **Inventario**: es el **mismo** de la pantalla *Inventario* (almacén). Lo que se usa aquí se descuenta de allá; si un producto sale en 0, carga la existencia en *Inventario*. Los *Tickets de productos* son **solo registro** (quién pidió, quién recibió, diferencias con el papel).
2. **Registra los movimientos del día**, en orden:
   - **Agregar químicos**: tanque, productos y cantidades, fluido base y agua.
   - **Agregar lodo reciclado**: tanque, volumen, producto "lodo reciclado", su origen y, si se conocen, las **concentraciones** del lodo que llega (lb/bbl).
   - **Transferencia**: de un tanque a otro.
   - **Devolución**: fluido que sale del pozo (indica a dónde).
   - **Pérdida**: tanque, volumen y **tipo de pérdida**.
3. **Al cierre, mide los tanques** y escribe el **volumen real** de cada una (y su tipo si cambió). Si hay volumen del hoyo que no es fluido (cemento, tapón), indícalo en **Volumen no fluido**. **Guarda.**
4. Revisa el **"No contabilizado"** de cada grupo (activo, reserva, premezcla): **debe quedar en 0**. Si no, falta registrar alguna pérdida o movimiento. **No cambies el volumen real para cuadrar.**
5. En el inventario, si hace falta, llena **usado en otro módulo** (por ejemplo, días de ingeniero), **ajuste**, **en pedido** o **no imprimir**, y **guarda**.

**b) Concentraciones.** Consulta. Muestra cuántas libras de cada producto hay por barril de lodo, en el **sistema activo** (tanques activos + hoyo) o en **cada tanque** (elige en la lista). Con los botones **lb/bbl** y **kg/m³** cambias la unidad.
- Arriba: volumen inicial y final, **cambio en volumen**, fluido base y agua agregados, aumento de volumen por material y lodo reciclado recibido.
- Por producto: tamaño, **cantidad agregada** hoy, concentración **inicial**, **cambio** y **final**, y el total.
- Cómo se mueven los números (no hay que hacer nada a mano, salen de los movimientos):
  - **Agregas agua o fluido base** → las concentraciones **bajan** (se diluye). Ej.: 500 bbl a 15 lb/bbl + 50 bbl de agua → 13,64.
  - **Agregas un producto** → la de ese producto **sube**. Ej.: + 100 lb de bentonita → 15,20.
  - **Mezclas lodo con lodo** (lodo reciclado o transferencia) → queda el **promedio**. Ej.: 500 bbl a 15 + 100 bbl a 20 → 15,83.
  - **Pierdes lodo** → la concentración **no cambia**.

**c) Hidráulica.** Consulta: elige **4ª** o **5ª edición**. Muestra pérdidas de presión, ECD, velocidades, régimen de flujo, datos de la mecha (HHP, HSI, velocidad de chorro) y la diferencia contra la presión real de la bomba. Si faltan datos, te dice cuáles y en qué pestaña.

**d) Evaluación de benchmark.** Consulta: compara los objetivos con los chequeos de lodo reales y da el % de mediciones dentro del objetivo.

**⚙ Pérdidas del reporte**: elige qué 10 categorías de pérdida se imprimen (es del pozo, se configura una vez).

### 6.4 Eventos no programados
**Ocultos desde el 02-oct-2026** a pedido de AOS (para no confundir al ingeniero). El módulo sigue en el código y los eventos ya cargados salen en el reporte final.

### 6.5 Moverse entre reportes
- La flecha **←** vuelve al hub.
- Los reportes **ya no se borran desde el hub** (página bloqueada). Si un pozo se empezó mal, se elimina el pozo completo (5.9).

### 6.6 Casos especiales: side track y hoyo piloto

#### Side track (desvío)
Pasa cuando algo sale mal perforando (la tubería se pega, el hoyo se derrumba) y hay que **abandonar** el tramo de abajo con un **tapón de cemento** para perforar de nuevo **desviándose** desde más arriba (el **kick-off**). No se anota como comentario: cambia la volumetría y el hoyo perforado. Se hace en tres días:

**1. Día del abandono (antes del kick-off)** — ej.: se venía a 3498 m y el tapón quedó con su tope en 2900 m.
- **Pestaña 1**: la **profundidad de la barrena** = tope del tapón (2900). **No cambies la profundidad del pozo** (sigue 3498).
- **Pestaña 4**: el volumen **bajo la mecha** es el lodo que quedó debajo del tapón (ej. 24,1 m³).
- **Pestaña 8**: en **Volumen no fluido → bajo la mecha** escribe ese volumen y **guarda**. Después registra una **Pérdida** por ese mismo volumen con el tipo **"Detrás del Revestimiento / En el Hoyo"** (código 7; en el curso se le llama "Dejado en el hoyo").

**2. Día del kick-off** — ej.: se desvió desde 8515 ft y al cierre del día se llegó a 9200 ft.
- **Pestaña 1**: la profundidad es la nueva del side track (9200).
- **Pestaña 4 → Contexto del pozo → Side Track**: marca **"Hoy arranca un side track"**, escribe la **profundidad de kick-off** (8515) y **guarda**. La tarjeta *Hoyo Perforado* dirá "685 ft desde el kick-off".
- **Gestionar intervalos del pozo**: crea el intervalo nuevo de tipo **Side Track (desvío)** y elígelo como **intervalo de costo** del día.

**3. Día siguiente**: nada especial. La casilla de side track se marca **solo** el día del kick-off.

> Solo se puede registrar un side track por día. El sistema no bloquea que la profundidad del pozo sea menor que la del día anterior.

#### Hoyo piloto (ampliación)
Pasa cuando se perforó primero un hoyo **pequeño** (ej. 8½") y luego se **amplía** con una mecha más grande (ej. 12¼").
- **Mientras se perfora el piloto**: es un hoyo normal. Deja *Hoyo piloto* en 0.
- **Desde que empieza la ampliación**:
  - Pestaña 1: profundidad y barrena = la de la **mecha grande** (ej. 1358 m).
  - Pestaña 2: tamaño de barrena = la grande (12¼").
  - Pestaña 4 → **Hoyo Piloto**: diámetro (8½") y profundidad (1710 m) del piloto.
- El sistema calcula solo el volumen bajo la mecha (el piloto que falta ampliar) y el **hoyo perforado**: dentro del piloto solo cuenta el anillo que corta la mecha grande, y el primer día de ampliación cuenta desde la zapata del último revestidor.

## 7. Rutina diaria recomendada

```
1. Hub → + Nuevo Reporte (Hoy, tipo de fluido, copiar datos: Sí)
2. Pestaña 1: profundidad, TVD, barrena, actividad → Guardar
3. Pestaña 2: SPM de bombas, boquillas y datos de barrena si cambiaron → Guardar
4. Pestaña 3: chequeos de lodo del día → Guardar
             (a media jornada, si hace falta: Reporte de Propiedades → PDF al compañero)
5. Pestaña 4: ajustar la sarta si cambió y el intervalo de costo → Guardar
             (si hoy arranca un side track: marcar la casilla y la profundidad de kick-off)
6. Pestaña 6: tickets de mallas recibidas → transacciones de mallas → uso de equipos → Guardar
7. Pestaña 8: (tickets de productos, solo registro) → movimientos → volumen real de tanques → Guardar
             → revisar "No contabilizado" = 0 → revisar concentraciones
8. Pestaña 7: horas por actividad → Guardar
9. Pestaña 5: resumen y observaciones → Guardar
10. Pestaña 1: revisar el balance económico → descargar el Excel
```

Al terminar el pozo: **Reporte Final del Pozo** (sección 8.3).

## 8. Reportes que se entregan

### 8.1 Reporte diario en Excel
Dentro del reporte, el botón de **Excel** descarga `Reporte_<N°>_<Pozo>_<fecha>.xlsx` con el formato del Mud Report en español y el logo de AOS arriba a la izquierda. Trae el **reporte general** (hoja de lodo según el tipo de fluido y propiedades extra), la **contabilidad de volumen** (balance y hoyo en números enteros, como se reporta en campo), las **concentraciones** (sistema activo y cada tanque, en lb/bbl y kg/m³), el **inventario químico** (tres hojas), equipos e inventario de mallas.

> Es normal ver en pantalla páginas con encabezado y sin datos debajo de las hojas de inventario, y tres hojas de inventario parecidas (por código, por nombre y completa). **Al imprimir, solo salen las páginas con datos.**

### 8.2 Reporte de propiedades del lodo (avance)
Para entregar las propiedades antes del reporte completo (por ejemplo, al compañero del turno).
1. Pestaña 3 → llena y **guarda** los chequeos.
2. Botón **Reporte de Propiedades**: se abre una página aparte con el encabezado del pozo, los chequeos del día (solo las propiedades con datos) y la especificación del lodo.
3. Escribe el **comentario** en el recuadro (tratamiento, tendencia, recomendación).
4. **Imprimir / Guardar PDF** → en el diálogo elige *Guardar como PDF*.

> El comentario de este reporte no se guarda en el sistema: se escribe e imprime en el momento.

### 8.3 Reporte final del pozo (recap)
Pantalla principal del pozo → tarjeta **📑 Reporte Final del Pozo**. Reúne todo el pozo en un solo reporte, en **Excel o PDF**, a elección.

**Paso 1 — Conclusiones y recomendaciones.** Escribe el **resumen del pozo**, las **conclusiones**, las **recomendaciones** y, si quieres, las **lecciones aprendidas**. Pulsa **Guardar textos**: quedan guardados en el pozo y puedes corregirlos cuando quieras. Las observaciones de cada intervalo se toman de *Intervalos de Revestimiento*.

**Paso 2 — Generar el reporte.**
- **Hasta la fecha** (opcional): para sacar un recap parcial; vacío = todo el pozo.
- **Secciones**: marca las que quieres (vienen todas marcadas):

| Sección | Qué trae |
|---|---|
| Datos del pozo y resumen | Operador, taladro, ingenieros, días, profundidad final, hoyo perforado, densidad mín./máx., pérdidas, costo total y costo por pie, side tracks, eventos |
| Conclusiones y recomendaciones | Los textos del paso 1 |
| Resumen por intervalo | Días, fechas, profundidad, pies perforados, densidad máxima, pérdidas, costo real y planeado, observaciones |
| Recap día por día | Por reporte: profundidad, avance, densidad, PV/YP, filtrado, volumen activo, pérdidas, costo del día y acumulado, actividad y **resumen del día** (pestaña 5) |
| Volúmenes y pérdidas | Fluido base, agua, químicos, lodo recibido, devuelto y perdido; pérdidas por categoría con su % |
| Productos consumidos | Cantidad usada y costo de cada producto en todo el pozo |
| Distribución de tiempo | Horas y % por actividad |
| Eventos no programados | Todos los eventos del pozo |
| Costos | Por concepto y por intervalo (real contra planeado) |

- **Descargar Excel**: un libro con una hoja por sección.
- **Ver / Guardar PDF**: se abre la página lista para imprimir; en el diálogo elige *Guardar como PDF* (mejor en **horizontal**).

> Con muchos reportes puede tardar unos segundos, porque se recalcula todo el pozo. Si algún día tiene la volumetría con error, el reporte lo avisa arriba y ese día sale con volúmenes y costos de químicos en 0.

## 9. Inventario del almacén

Menú → **Inventario**. Es el stock del **almacén** de AOS y el catálogo de productos del sistema.

- Filtra por **Todos**, **Sólidos** o **Líquidos**, y busca por código, descripción o unidad.
- Haz clic en una fila para ver o editar. Para crear, usa el formulario: código, descripción, unidad, costo, libraje, cantidad, gravedad específica y categoría.
- El **estado** se calcula solo: **Bajo** (0 a 20), **Medio** (21 a 50), **Alto** (más de 50).
- Solo se puede **eliminar** un producto con **cantidad 0** que no se haya usado en ningún pozo.

> Es **el mismo inventario** que usa el reporte diario de todos los pozos: lo que se agrega en la pestaña 8 se descuenta de aquí, y borrar un pozo lo devuelve. Las compras y llegadas se cargan aquí, editando la cantidad.

## 10. Consejos y errores comunes

| Mensaje o situación | Qué hacer |
|---|---|
| "Inventario de …: hay N … y se necesitan M. Actualiza la existencia en la pantalla Inventario." | Carga la existencia real del producto en *Inventario* |
| "No hay mallas nuevas de … en stock" | Ticket de recepción de mallas en la pestaña 6 |
| "La posición X del equipo Y ya tiene …" | Primero retira la malla (Pasar al almacén o Desechar) |
| "…no tiene tipo asignado (o es 'Vacía')" | En la volumetría, asigna un tipo a ese tanque y guarda |
| "El intervalo N sigue abierto…" | Cierra el intervalo anterior (5.3) antes de crear el siguiente |
| "Ya existe un reporte para …" | Solo uno por día: ábrelo desde el hub |
| "La profundidad de kick-off … debe ser menor que la profundidad del día" | Revisa la profundidad de la pestaña 1 (debe ser la nueva del side track) |
| La hidráulica dice "faltan…" | Completa y guarda la pestaña indicada (2, 3 o 4) |
| Volúmenes del hoyo en 0 | Revisa intervalos de revestimiento, profundidad de la barrena, tamaño de la barrena y sarta |
| Un producto no aparece en concentraciones | En *Productos activos*: unidad de peso, tamaño y *calcular concentración* marcado |
| El reporte de propiedades sale vacío | Guarda primero la pestaña 3 |
| El reporte final dice "La volumetría no cuadra en…" | Abre la pestaña 8 de esos días y corrige el error de inventario o de tanques |
| La pantalla no se actualiza | `Ctrl + F5` |
| Costos del día en 0 de repente | Abre las pestañas 6 y 8: probablemente hay un error de inventario que mostrar |

**Buenas prácticas**
- Registra las **mallas recibidas** (pestaña 6) y carga en *Inventario* los **productos que llegan** el mismo día en que llega el material.
- Si algo está mal en un reporte, corrígelo con un movimiento o un ajuste (los reportes no se borran desde el hub).
- Usa **Deshacer** solo para el último movimiento.
- Mide y escribe el **volumen real** de todos los tanques cada día.
- Escribe cada día el **resumen del día** (pestaña 5): es lo que arma el recap del reporte final.
- Mantén los catálogos maestros ordenados y con nombres claros.
