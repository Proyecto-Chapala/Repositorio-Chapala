# 20 — Concentraciones, Side Track y Hoyo Piloto

Agregado el **27-sep-2026** a pedido del ingeniero de AOS (audios de revisión y lección 9 del curso ONE-TRAX "Diseño Side Track"). Cubre tres cosas: el reporte de **concentraciones**, el **side track** y el **hoyo piloto**. Migración nueva: **0022_sidetrack**.

---

## 1. Concentraciones de productos

### Qué es

La concentración de un producto es cuántas **libras hay por cada barril** de lodo:

```
concentración (lb/bbl) = libras totales del producto ÷ volumen de lodo (bbl)
1 lb/bbl = 2,85301 kg/m³
```

Se lleva **por compartimento**: el **sistema activo** (todas las fosas activas + el hoyo, porque se mezclan al circular) y **cada una de las demás fosas** por separado. El punto de partida de cada día es el cierre del día anterior.

### Los tres casos que explicó el ingeniero (y cómo los resuelve el sistema)

| Caso | Qué pasa | Ejemplo verificado |
|---|---|---|
| **Lodo + agua (o fluido base)** | Las libras no cambian y el volumen sube → la concentración **baja** (se diluye) | 500 bbl a 15 lb/bbl + 50 bbl de agua → 7500 / 550 = **13,64** |
| **Lodo + producto** | Suben las libras; el volumen sube un poco por el material (peso ÷ (GE × 350)) → la concentración **sube** | 500 bbl a 15 lb/bbl + 100 lb de bentonita → 7600 / 500,11 = **15,20** |
| **Lodo + lodo** (lodo entero o transferencia de otra fosa) | Se suman las libras de ambos y los volúmenes → queda un **promedio ponderado** | 500 bbl a 15 + 100 bbl a 20 → (7500 + 2000) / 600 = **15,83** |
| **Pérdida o devolución** | Se va lodo con todo lo que trae → la concentración **no cambia** | 500 bbl a 15 − 100 bbl → 15 |

> ⚠ La hoja escrita a lápiz del ingeniero tiene un error en el tercer ejemplo: 20 × 100 = **2000** lb (no 2500), por eso el resultado correcto es **15,83** lb/bbl y no 16,7.

**Por qué en ONE-TRAX a veces sube la concentración sin agregar nada**: porque entró lodo más cargado desde otra fosa. En el reporte 96 del pozo XOM.Nq.BdC.x-2 entraron 34 m³ desde la premezcla (1680 kg/m³) a la activa: es el caso "lodo + lodo".

Todo sale de los **movimientos de la volumetría** (pestaña 8). No hay nada que escribir a mano para las concentraciones: solo hay que registrar bien los movimientos y marcar *Calcular concentración* en los productos activos que se miden en peso.

### Dónde se ve

- **Pestaña 8 → Concentración** (consulta): selector de compartimento (sistema activo o cada fosa), botón de unidad **lb/bbl ↔ kg/m³**, volumen inicial/final y cambio, fluido base, agua, aumento de volumen por material y lodo entero del día; por producto: tamaño, **cantidad agregada**, concentración inicial, cambio y final, y total.
- **Excel → hoja "Concentraciones"** (formato del reporte "Sistema Activo" de ONE-TRAX): encabezado del pozo, volúmenes del día en bbl y m³, tabla por producto con inicial/cambio/final en **lb/bbl y kg/m³** y total. Un bloque por compartimento, cada uno en su página (primero el sistema activo).

### Técnico

- Motor: `volumetria.simular()` lleva `masa[compartimento][producto]` (lb). Nuevo en esta versión: por compartimento también `agregado` (unidades de producto agregadas hoy) y `entradas` (aceite, agua, volumen de químicos, lodo entero).
- API: `concentraciones[]` en `_estado_volumetria()` ahora incluye `unidad`, `tamano`, `empaque`, `agregado` por producto y `aceite`, `agua`, `vol_quimicos`, `lodo` por compartimento.
- Excel: `_hoja_concentraciones()` en `reporte_excel.py` (la hoja se crea por código, no está en la plantilla).

---

## 2. Side Track (desvío)

### Qué es

Mientras se perfora, algo sale mal (la tubería se pega, el hoyo se derrumba, no se puede pasar) y hay que **abandonar** el tramo de abajo: se pone un **tapón de cemento** y se vuelve a perforar **desviándose** desde un punto más arriba (el **kick-off**). La profundidad del pozo **baja** y el volumen que quedó debajo del tapón se **pierde**. No es un comentario: cambia la volumetría y el hoyo perforado.

### Por qué importa

Normalmente el **hoyo perforado del día** = profundidad de hoy − profundidad de ayer. El día del kick-off eso da negativo o sin sentido, porque ayer se estaba en el hoyo viejo. Del hoyo perforado salen los **recortes** del control de sólidos (pestaña 6) y varios indicadores con los que el operador evalúa el servicio (longitud perforada, volumen de hoyo perforado, eficiencia de equipos, dilución).

### Paso a paso en CHAPALA

**Día anterior (abandono / tapón)** — ejemplo: se venía a 3498 m y el tope del tapón quedó en 2900 m.
1. **Pestaña 1**: profundidad de la mecha = **tope del tapón** (2900). La **profundidad del pozo NO se cambia** (sigue 3498); si se cambia, se afecta la volumetría.
2. **Pestaña 4**: el volumen **bajo la mecha** es el hoyo que quedó debajo del tapón (en el ejemplo, 24,1 m³).
3. **Pestaña 8 → Volumetría**: en *Volumen no fluido → bajo la mecha* poner ese volumen. Luego **Pérdida** por el mismo volumen con la categoría **"Detrás del Revestimiento / En el Hoyo"** (código 7 del estándar; ONE-TRAX *Behind Csg/In Hole*; en el curso "Dejado en el hoyo").

**Día del kick-off** — ejemplo: kick-off a 8515 ft, al cierre del día se llegó a 9200 ft.
1. **Pestaña 1**: profundidad = la nueva del side track (9200).
2. **Pestaña 4 → Contexto del Pozo → Side Track**: marcar **"Hoy arranca un side track"** y escribir la **profundidad de kick-off** (8515). Guardar. La tarjeta **Hoyo Perforado** muestra "685 ft desde el kick-off".
3. **Gestionar intervalos del pozo**: crear el intervalo nuevo de tipo **"Side Track (desvío)"** (el "S" de ONE-TRAX) para llevar sus costos, y elegirlo como intervalo de costo del día.

**Día siguiente**: nada especial. La casilla se marca **solo** el día del kick-off; al día siguiente el avance vuelve a ser hoy − ayer.

Validaciones: el kick-off debe ser menor que la profundidad del día y no puede ser más profundo que el hoyo del día anterior. Solo hay un side track por día (igual que ONE-TRAX).

### Verificación con el manual ONE-TRAX (Special Cases: Side-Track)

| Día | Cálculo | CHAPALA | ONE-TRAX |
|---|---|---|---|
| Kick-off (19/01) | (9200 − 8515) ft × 9,69²/1029,4 | 62,5 bbl | 62 |
| Siguiente (20/01) | (10442 − 9200) ft × 9,69²/1029,4 | 113,3 bbl | 113 |
| Lección 9 (abandono) | 598 m bajo el tapón con hoyo de 8,915" | 24,08 m³ | 24,1 |

### Técnico

- Campo nuevo `ReporteDiario.kickoff_sidetrack_ft` (0 = no hay side track ese día).
- Tipo nuevo `SIDETRACK` en `IntervaloRevestimiento.TIPO_CHOICES`. No tiene revestidor, así que no entra al perfil de confinamiento (igual que hoyo abierto).
- Cálculo en `control_solidos.hoyo_perforado()` (función pura), usada por `views_control_solidos._contexto_hoyo()` → pestaña 6, tarjeta "Hoyo Perforado" de la pestaña 4 (`hoyo_perforado` en la API de geometría) y el avance del Excel.
- La geometría (perfil) no cambió: el fondo es la profundidad del día, así que el hoyo abandonado deja de contarse solo cuando la profundidad del día baja.
- El sistema **no bloquea** que la profundidad baje de un día a otro.

---

## 3. Hoyo piloto (ampliación)

### Qué es

Primero se perfora un hoyo **pequeño** (ej. 8½") y después se **amplía** con una mecha más grande (ej. 12¼"). Mientras se amplía, solo se corta el **anillo** entre las dos mechas, y parte del hoyo tiene el diámetro chico.

### Paso a paso

- **Mientras se perfora el piloto**: nada especial; es un hoyo normal. Hoyo piloto = 0.
- **Desde que empieza la ampliación**:
  - Pestaña 1: profundidad y mecha = la de la **mecha grande** (ej. 1358 m).
  - Pestaña 2: tamaño de mecha = la grande (12¼").
  - Pestaña 4 → **Hoyo Piloto**: diámetro (8½") y profundidad (1710 m) del piloto.

### Cálculo del hoyo perforado

- Dentro del tramo que ya tenía piloto: `(D² − d²) / 1029,4 × longitud` (solo el anillo).
- Fuera del piloto: `D² / 1029,4 × longitud`.
- **Primer día de ampliación** (ayer no había piloto cargado): se cuenta desde la **zapata del último revestidor**, porque la profundidad de ayer era la del piloto.

Verificación con el manual (Special Cases: Pilot hole): revestidor 13⅜" a 920,11 m, piloto 8½" a 1710 m, ampliando a 12¼" hasta 1358 m → **438 m y 108,6 bbl** (ONE-TRAX: 438 m y 109 bbl). El volumen bajo la mecha (81 bbl) es el piloto entre 1358 y 1710 m, que la geometría ya calculaba.

---

## 4. Análisis de sólidos con carbonato de calcio (CaCO₃)

Recomendaciones del manual para el ingeniero (no requieren programación):
- **Base agua**: poner la GE de la **barita** como material densificante y estimar las lb/bbl de CaCO₃ en el campo **"Concentración química"** del análisis de sólidos (pestaña 3). Si no, el carbonato se reporta como sólido perforado.
- **Base aceite**: no hay MBT ni concentración química; solo salen %HGS y %LGS. El %LGS "alto" incluye el carbonato.
- Si **no hay sólidos de alta gravedad**, ajustar el % de sólidos de la retorta para que el HGS quede cerca de 0 sin negativos (en OBM, el ajuste se suma o resta al % de aceite).
- Retorta: usar la de 50 cc, verificar recuperación del 100 % con fluido base puro, verificar volúmenes de copa y probeta con pipeta de 50 cc, y volver a pesar la muestra si se enfrió mucho.

---

## 5. Redondeo en el Excel

En la hoja **Contabilidad de Volumen**, el balance, el lodo en el hoyo y las pérdidas se imprimen **sin decimales** (en campo el volumen se reporta entero). Los volúmenes por fosa llevan 1 decimal (como el Mud Volume Accounting de ONE-TRAX) y los costos no se redondean más allá de centavos.
