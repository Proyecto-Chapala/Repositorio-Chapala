# 21 — Análisis del material de la revisión del 27-sep-2026

Registro del análisis de **todas las imágenes y audios** que el usuario compartió el 27-sep para las últimas funciones antes de las pruebas finales. Sirve para entender **de dónde sale** cada decisión de [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) sin tener las imágenes a mano.

Material recibido:
1. Transcripciones de dos audios de la reunión con el ingeniero (`1era_parte.txt`, `2da_parte.txt`).
2. Lección N° 9 del curso ONE-TRAX en español, **"Diseño Side Track"** (8 diapositivas, pozo XOM.Nq.BdC.x-2, Exxon Mobil, Neuquén).
3. Hoja escrita **a lápiz** por el ingeniero con los cálculos de concentración.
4. Foto del reporte impreso **"REPORTE DiaRIO (Sistema Activo)"** de ONE-TRAX (reporte 97).
5. Foto del reporte impreso **"MUD VOLUME ACCOUNTING"** de ONE-TRAX (reporte 96).
6. Manual ONE-TRAX en inglés, **Tab #8** (págs. 125-130): Inventory/Hydraulics/Concentrations.
7. Manual ONE-TRAX en inglés, **Special Cases** (págs. 247-258): Side-Track, Pilot hole, Solids Analysis con CaCO₃.

---

## 1. Audios de la reunión (lo que pidió el ingeniero)

**Pedidos concretos:**
- **Concentraciones**: "lo que faltaría". Los tres eventos: lodo + agua, lodo + material, lodo + lodo (ver §3).
- **Side track**: tiene que ser parte del cálculo, no un comentario ("eso no puede colocarse como una observación, es parte del cálculo"). El pozo se abandona debajo del tapón, la profundidad vuelve a una menor y el volumen que quedó abajo se saca del sistema como perdido ("dejado en el hoyo"). Menciona también el **washout** (hoyo lavado).
- **Cuatro reportes** que se entregan: general, volumetría, concentraciones e inventario ("un paquete de tres: el reporte principal, el inventario y la presentación").
- **Reporte corto de propiedades del lodo** con un comentario, para entregar un avance al compañero antes del reporte de la noche ("un reportico independiente… simplemente el lodo").
- **Reporte final consolidado** al terminar el pozo/curso: recomendaciones, conclusiones, todos los eventos y prácticas. Acordaron que mejor en **PDF**.
- **Redondeo**: todo resultado de cálculo va redondeado (densidad 12,5 y no 12,4786; volumen 1325 y no 1394,37). **Los costos no se redondean** ("costo es costo, es billete").
- **Unidades**: el ingeniero trabaja en lb/bbl, pero el programa debe poder dar kg/m³.
- Productos: debe existir el dato de **libras totales** por unidad para poder calcular (en CHAPALA sale de unidad + tamaño del producto activo).

**Confirmaciones (ya estaba bien):**
- Fondo arriba y ciclo completo: ya se calculan en la geometría.
- Componentes de sarta con nombre editable: bien.
- Bombas: de 2 a 4 según el taladro, nombre editable, está bien.
- Día de 24 horas en la distribución de tiempo; si no cuadra se avisa.
- Plazo: listo antes de que empiece el curso a los ingenieros (semana siguiente).

---

## 2. Lección 9 — "Diseño Side Track" (8 diapositivas)

| Diap. | Contenido | Lectura |
|---|---|---|
| 1 | Portada "ONE-TRAX · Diseño Side Track · Lección N° 9" | — |
| 2 | **Procedimiento**: (1) fijar Bit Depth en el tope del tapón de cemento; (2) en Well Geometry → Daily Casing, configurar el escenario con la profundidad del tope; (3) en Volume Accounting poner en **Volume Not Fluids** el volumen debajo del tapón; (4) hacer las transacciones Transfer/Loss por todo el volumen perdido ("Left in Hole", lodo dejado entre tapón y tapón); (5) en Casing Interval Summary crear el intervalo del side track; (6) pasar al siguiente día y seguir perforando | Es el procedimiento de 3 días que se implementó (ver [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) §2) |
| 3 | Pestaña 1-General del 08/10/2013: Depth 3498 m, TVD 3498, **Bit Depth 2900 (amarillo)** = "profundidad del tapón de cemento" | La profundidad del pozo **no** se cambia; solo la mecha va al tope del tapón |
| 4 | Well Geometry: Daily Intervals con filas 1 F 13,375" a 505; 2 F 9,625" a 2694; **3 O a 2900** (amarillo); **4 O a 3498**. Hole Volume Summary: Drill String 25, Annulus 75,4, **Below Bit 24,1**, Total 124,5. Hole Size 8,5; Washout 8,915 | Below Bit = volumen bajo el tapón. **Verificado**: 598 m × (8,915" → 0,040273 m²) = **24,08 m³** ✔ (usa el diámetro con washout) |
| 5 | Casing Interval Summary: intervalos 1 F, 2 F, **3 O a 3498** (queda como hoyo abierto con la profundidad real del fondo) y **4 S** (Side Track, nuevo). Interval (Cost) Number = 4 | Tipo **"S"** → en CHAPALA tipo de intervalo **"Side Track (desvío)"** |
| 6 | Volume Accounting: **Volume Not Fluids** = 24,1 en Below Bit → Fluid Volume 100,4; Total Loss Break Down: "2 Dejado en Hoyo" = 24,1; botón Transfer/Loss resaltado | Volumen no fluido + pérdida. En el estándar de CHAPALA la categoría es la **código 7 "Detrás del Revestimiento / En el Hoyo"** |
| 7 | Día siguiente (09/10/2013): Depth = TVD = **Bit Depth = 2920** | La profundidad del pozo **baja** respecto al día anterior (3498 → 2920) |
| 8 | Comparación de los dos días: 08/10 con 4 filas (hasta 3498) y 09/10 con 3 filas (hoyo abierto a 2920); dibujo del pozo antes y después | El hoyo viejo desaparece del perfil cuando baja la profundidad |

---

## 3. Hoja a lápiz del ingeniero — concentraciones

Tres casos, todos con bentonita:

| Caso | Escrito por el ingeniero | Revisión |
|---|---|---|
| **Vol. conc. + agua** | 500 bbl con 15 lb/bbl + 50 bbl de agua → 15 × 500 = 7500 lb; vol. total 550; 7500 / 550 = **13,64 lb/bbl** | ✔ correcto |
| **Vol. conc. + lb de material** | 500 bbl a 15 lb/bbl + 100 lb de bentonita → 7500 + 100 = 7600 lb; 7600 / 500 = **15,2 LPB** | ✔ correcto. En el audio aclara que el volumen "aumentó un poco" por el material; CHAPALA lo suma (100 lb / (2,6 × 350) = 0,11 bbl → 15,20) |
| **Vol. conc. 1 + vol. conc. 2** | 500 bbl a 15 LPB + 100 bbl a 20 LPB → 15 × 500 = 7500; **20 × 100 = 2500** (error); total 10000 lb / 600 bbl = **16,7** | ✘ **Error aritmético**: 20 × 100 = **2000**; total 9500 lb / 600 = **15,83 lb/bbl**. Hay que avisarle al ingeniero |

Regla general que se programó: **concentración = libras totales ÷ volumen**; las pérdidas de lodo entero no cambian la concentración (se va lodo con todo lo que trae).

---

## 4. Foto "REPORTE DiaRIO (Sistema Activo)" — reporte 97

- Encabezado: Operator Exxon Mobil, Well XOM.Nq.BdC.x-2, Location Neuquén (Argentina), M-I Well No. 175733, **Report No. 97**, Spud 04/08/2013, **Date 08/11/2013**, Depth 4570 m, Mud Weight 1300 kg/m³.
- Bloque de volúmenes: Aceite Agregado (m³), **Incr Vol – Matl Den** (m³) (aumento de volumen por la densidad del material), Vol. Inicial Fluidos **105,6**, 18 (sin rótulo visible), Cambio en Volumen **−87,6**.
- Tabla: PRODUCT · Size · AMOUNT ADDED (Qty Unit) · ESTIMATED CONC (kg/m³) **Initial / Change / Final**. 15 productos, todos con cantidad agregada 0,00. Ej.: M-I BAR (Big Bag, 1 MT BG) 696,54 → +130,89 → 827,43; Quicklime 20,72 → 24,58; Megamul 14,52 → 17,06; VG-69 6,86 → 8,12; etc.
- **Total: 976,47** = suma de las concentraciones finales (verificado: 976,48 por redondeo).

**Observación analizada:** todas las concentraciones suben ~18,8 % sin agregar producto. Primero pareció contradecir la regla del ingeniero, pero el manual (Tab #8, pág. 128) aclara que la concentración es **por fosa** y depende de las transacciones de la volumetría: ese período entró lodo más cargado desde la premezcla (en el reporte 96 se ven **34 m³ de Premix → Activo**, premezcla a 1680 kg/m³ contra 1350 del activo). Es el caso **lodo + lodo**, no un error.

**Cómo quedó en CHAPALA:** hoja "Concentraciones" del Excel y pantalla de la pestaña 8 con el mismo esquema (cantidad agregada, inicial, cambio, final, total), en lb/bbl y kg/m³, y volúmenes del día (fluido base, agua, aumento por material, lodo entero, inicial, final, cambio).

---

## 5. Foto "MUD VOLUME ACCOUNTING" — reporte 96 (07/11/2013)

- **Tanques** (TANK · CAPACITY m³ · WEIGHT kg/m³ · VOLUME m³ · REMARKS · CLASS): Active 1 (124 · 1350 · 105,6 · Megadril · Active), Píldora (18 · 1350 · 18,3 · Reserve), Premix 1/2/3 (19-20 · 1680 · 8,3/8,5/8,6 · Premix), Reserve 1 (26 · 1680 · 24,4), Reserve 2 (16 · 14,5 · Salmuera), Química (12 · 7,5 · Reserve).
- **Sum Pit Volumes**: Active 105,6 · Reserve 64,7 · Premix 25,4.
- **Mud in Hole**: Annulus 115 · Pipe 48 · Below Bit — · Total 163; Volume Not Mud 115/48 → 163 (todo el hoyo marcado como "no lodo" ese día).
- **Volume Balance** (Active / Reserve / Premix / Total): Start 105/47/60/211 · Oil Added 15 · Total Volume Built 15 · From Active To 18 (a reserva) · From Premix To 34 (al activo) · Daily Loss 30 · **Final 106/65/25/196**.
- **Loss Breakdown**: Decanter 30 (Verti-G, Secadora, Dejado en el hoyo, Mud Cleaner, Permeability, Contaminado, Maniobra en 0) · Total Loss 30.

**Verificación del balance:** Activo 105 + 15 − 18 + 34 − 30 = **106** ✔ · Reserva 47 + 18 = **65** ✔ · Premix 60 − 34 = 26 ≈ 25 (redondeo de 25,4) ✔ · Total 211 + 15 − 30 = **196** ✔ · Reserva por tanque 18,3 + 24,4 + 14,5 + 7,5 = **64,7** ✔. Premix 8,3 + 8,5 + 8,6 = **25,4** ✔.

**Conclusiones:** el balance y el lodo en el hoyo se imprimen **sin decimales** (confirma el pedido de redondeo); los tanques con 1 decimal. La hoja "Contabilidad de Volumen" de CHAPALA ya tenía esta estructura; se ajustó el redondeo.

---

## 6. Manual ONE-TRAX — Tab #8 (págs. 125-130)

| Pág. | Pantalla | Qué se aprendió |
|---|---|---|
| 125 | Tab 8 "Inv/Hyd/Conc": Inventory/Fluids Volume Accounting (entrada de datos) · Hydraulics, Cuttings Retention, **Product Concentration**, Evaluation of Benchmark (solo **muestran** datos) · Daily Loss Print Selection (configuración) | Concentración es de consulta, no se captura |
| 126 | Daily Loss Print Selection: hasta **20 categorías**, máximo **10 en el reporte** (Add / Delete / Add All) | Ya construido ("Pérdidas del reporte") |
| 127 | Benchmark Evaluations: Target Values (del Setup) vs Actual Values (calculados) por Whole Well e intervalos | Ya construido |
| 128 | **Product Concentration** (8/21/2005): Product Name · Start Conc. · End Conc. (lb/bbl); **Pit Name** (desplegable, ej. Active #1) con su Fluid Volume (570); Report Type **Active / Pits**; "estos valores dependen de las transacciones de Volume Accounting" | La concentración es **por fosa**; se imprime del sistema activo o de las fosas → así quedó la hoja de Excel (un bloque por compartimento) |
| 129-130 | Hydraulic Results API 5ª ed. (AnnT, AnnPV, AnnYP; DS 1462, Ann 79, Bit 1435, Total 2976 psi) y la salida gráfica | Ya construido (mecha verificada: 1435 psi) |

---

## 7. Manual ONE-TRAX — Special Cases (págs. 247-258)

### Side-Track (págs. 247-252)
- Normalmente el **hoyo perforado** = profundidad de hoy − de ayer; **no funciona el primer día de un side track**. Solo **un side track por día**.
- Es importante porque el operador evalúa el servicio con longitud perforada, volumen de hoyo perforado, SCE y dilución.
- **Paso 1** (día anterior al kick-off): poner la profundidad de abandono (*plug back*) en el último intervalo de Daily/Casing Volume; **no cambiar la profundidad de la pestaña 1**. Ej.: plug back 20.171 ft, mecha a 4000, Below Bit 1475, Total 1775.
- **Paso 2** (día del kick-off): agregar un intervalo tipo **"S"** con profundidad = TD del día, y la **profundidad de kick-off** en el intervalo de arriba. Ej.: kick-off 8515 ft, TD 9200 ft; **Drilled Hole = 62**.
- **Paso 3** (día siguiente): borrar el intervalo "S"; queda el hoyo abierto con la TD del día. Ej.: TD 10.442 ft; **Drilled Hole = 113**.
- **Verificado**: (9200 − 8515) × 9,69²/1029,4 = **62,5** ✔ · (10442 − 9200) × 9,69²/1029,4 = **113,3** ✔.
- **Implementación en CHAPALA** (más simple que ONE-TRAX): casilla "Hoy arranca un side track" + profundidad de kick-off en la pestaña 4, solo ese día; el hoyo perforado se cuenta desde el kick-off. El perfil del pozo no necesita el intervalo "S" diario porque se arma con la profundidad del día.

### Pilot hole (págs. 253-255)
- Mientras se perfora el piloto no hay nada especial. Al **ampliar** con una mecha mayor, los recortes y el volumen que circula son una fracción → se usa la caja **Pilot Hole** (tamaño y profundidad) de la pestaña 4.
- Ejemplo: revestidor 13⅜" a 920,11 m; piloto 8½" a 1710 m.
  - *Antes de ampliar* (29/07/2006, reporte 22): Depth 1710, Bit Depth 796, Bit 12¼"; Pilot Hole 0 → **no se carga piloto**. Below Bit 439, Total 850.
  - *Primer día ampliando* (30/07/2006, reporte 23): Depth = Bit Depth = **1358**; Pilot Hole 8,5 / 1710. Resultados: Below Bit **81**, **Drilled Hole 109**, **Drilled Depth 438 m**.
- **Deducción** (no está escrita en el manual): 438 = 1358 − 920,11 → el primer día cuenta **desde la zapata**; el volumen es solo el **anillo**: (12,25² − 8,5²)/1029,4 × 1437 ft = **108,6 bbl** ✔; Below Bit = piloto de 1358 a 1710 m = 81,1 ✔.

### Solids Analysis con CaCO₃ (págs. 256-258)
- WBM: GE de la barita como densificante; estimar lb/bbl de CaCO₃ y ponerlo como **Chemical Concentration** (si no, cuenta como sólido perforado). %LGS incluye aditivos, no es lo mismo que %DS.
- OBM: sin MBT ni concentración química; solo %HGS y %LGS; el %LGS "alto" incluye el carbonato.
- Sin sólidos de alta gravedad: ajustar el % de sólidos de la retorta para que HGS quede ~0 sin negativos (en OBM el ajuste va al % de aceite).
- Retorta: usar la de 50 cc; comprobar 100 % de recuperación con fluido base puro (si no, revisar temperatura final); verificar volúmenes de copa y probeta con pipeta de 50 cc; volver a pesar si la muestra se enfrió mucho.
- **No requiere programación** (el campo "Concentración química" ya existe); quedó en el manual de usuario.

---

## 8. Resumen: de cada fuente a lo construido

| Fuente | Resultado en CHAPALA |
|---|---|
| Audios + hoja a lápiz + foto Sistema Activo + manual pág. 128 | Concentraciones por compartimento, pantalla con lb/bbl ↔ kg/m³ y hoja Excel "Concentraciones" |
| Foto Mud Volume Accounting + audio (redondeo) | Hoja "Contabilidad de Volumen" sin decimales en balance/hoyo/pérdidas; redondeo en pantallas |
| Lección 9 + manual págs. 247-252 | Side track (kick-off del día, tipo de intervalo, hoyo perforado), migración 0022_sidetrack |
| Manual págs. 253-255 | Hoyo perforado al ampliar piloto |
| Manual págs. 256-258 | Nota en el manual de usuario (pestaña 3) |
| Audio (reportico) | Reporte corto de propiedades del lodo (pestaña 3 → PDF) |
| Audio (reporte final) | Reporte final del pozo en Excel o PDF, migración 0023_recap_pozo |

**Pendiente de confirmar con el ingeniero:** el error del caso 3 de su hoja (15,83 y no 16,7) y si el comentario del reporte corto de propiedades debe quedar guardado.
