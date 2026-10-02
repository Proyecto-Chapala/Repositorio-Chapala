# 10 — Hidráulica (API RP 13D, 4ª y 5ª edición)

Archivos: `hidraulica.py` (motor puro), `views_hidraulica.py` (`api_hidraulica_detail`, `calcular_hidraulica_reporte`) y `reporte_hidraulica.js/.css`.

La pantalla es **solo de consulta**: no guarda nada. Cada vez que se abre, recalcula con lo último guardado en las pestañas 2, 3 y 4. Se puede cambiar entre la **4ª edición** y la **5ª edición** con los botones de la pantalla.

## 1. Datos de entrada

| Dato | De dónde sale | Si falta |
|---|---|---|
| Caudal Q (gpm) | Suma del caudal de las bombas activas (pestaña 2). Si da 0, el *caudal de bombas* de los datos de barrena | Lo avisa y no calcula |
| TFA (in²) | Boquillas (pestaña 2) | Lo avisa y no calcula |
| Tamaño de la mecha | Datos de barrena (pestaña 2) | HSI = 0 |
| Peso del lodo ρ (lb/gal) y reología | **Chequeo principal** de la pestaña 3: el marcado como principal que tenga R600/R300 o PV/YP; si no, el primero con datos | Lo avisa y no calcula |
| Secciones (diámetros y longitudes) | Motor de geometría de la pestaña 4 | Si no hay sarta, lo avisa |
| TVD a cada profundidad | 1) Interpolación entre las estaciones del **Well Survey**; 2) si no hay, proporción TVD/MD del reporte; 3) si no, pozo vertical | Se informa la fuente usada |
| Temperatura (solo 5ª) | Temperatura de superficie + gradiente °F/100 ft (Información General del Pozo) | No se muestra |
| Equipo de superficie | Pestaña 2: código 1-4 **o** presión y caudal de referencia | Pérdida de superficie = 0, con nota |

## 2. Reología

Si faltan lecturas, se completan con PV y YP: `R600 = 2PV + YP`, `R300 = PV + YP`.

### 4ª edición — ley de potencia
```
Tubería:  n = 3.32·log(R600/R300)        K = 5.11·R600 / 1022^n
Anular:   n = 0.657·log(R100/R3)         K = 5.11·R100 / 170.2^n
```
Si faltan R100 o R3, en el anular se usan los parámetros de la tubería, con aviso. K en dina·sⁿ/cm².

### 5ª edición — Herschel-Bulkley
```
τy = 1.066·(2·R3 − R6)                 (≥ 0; si faltan R6/R3 → τy = 0, con aviso)
n  = 3.32·log((2PV + YP − τy') / (PV + YP − τy'))       τy' = τy/1.066
k  = 1.066·(PV + YP − τy') / 511^n
```
Los mismos parámetros sirven para tubería y anular. k en lbf·sⁿ/100 ft². La reología **no se corrige por temperatura ni presión**, porque eso exige lecturas a varias temperaturas que el reporte no captura.

La pantalla dibuja un **reograma**: lecturas medidas contra la curva del modelo a 3, 6, 10, 30, 60, 100, 200, 300, 600 y 1000 rpm.

## 3. Pérdidas por fricción en sarta y anular

Unidades de campo: Q gpm, D in, V ft/min, ρ lb/gal, L ft, ΔP psi.

```
V = 24.48·Q / D²                               (anular: D² → D_hoyo² − OD²; D_h = D_hoyo − OD)
ΔP = 1.076e-5 · f · ρ · V² · L / D_h
```

**4ª edición.** Viscosidad efectiva:
- tubería `μ = 100·K·(96V/D)^(n−1)·((3n+1)/4n)^n`
- anular `μ = 100·K·(144V/D_h)^(n−1)·((2n+1)/3n)^n`

`Re = 15.467·V·D·ρ/μ`. Fricción de Fanning: laminar `16/Re` si `Re < 3470 − 1370n`; turbulento `a/Re^b` con `a = (log n + 3.93)/50` y `b = (1.75 − log n)/7` si `Re > 4270 − 1370n`; interpolación lineal en la transición.

**5ª edición.** Factor geométrico α (0 tubería, 1 anular), `G = ((3−α)n+1)/((4−α)n)·(1+α/2)`, `γw = 1.6·G·V/D_h`, `τw = ((4−α)/(3−α))^n·τy + k·γw^n`, `Re = ρV²/(19.36·τw)`. Fricción combinada laminar/transición/turbulenta:
`f = (f_lam¹² + (f_trans⁻⁸ + f_turb⁻⁸)^−1.5)^(1/12)`.

Por sección se informan: velocidades en sarta y anular, **velocidad crítica** (anular, a la que deja de ser laminar, obtenida por bisección), régimen de flujo, pérdidas, MD, TVD, **ECD** y, en la 5ª, temperatura anular y PV/YP usados.

```
ECD (lb/gal) = ρ + ΣΔP_anular(hasta esa profundidad) / (0.052 · TVD)
```

Las secciones **bajo la mecha** o sin tubería no generan pérdida.

## 4. Equipo de superficie

1. Si hay **presión y caudal de referencia** (pestaña 2): `ΔP_sup = P_ref · (Q / Q_ref)^1.86`.
2. Si no, con **código de caso 1-4**: longitud equivalente de tubería de 3,826" ID. Caso 1 = 2600 ft, 2 = 946 ft, 3 = 610 ft, 4 = 424 ft.
3. Si no hay ninguno de los dos: 0, con nota.

La pérdida de superficie se suma a la de la sarta.

## 5. Mecha

Coeficiente de descarga Cd = 0,95:
```
ΔP_mecha = ρ·Q² / (10858·TFA²)
HHP      = ΔP_mecha·Q / 1714
HSI      = HHP / (π/4·D_mecha²)
V_chorro = 0.3208·Q / TFA            (ft/s)
Impacto  = ρ·Q·V_chorro / 1932       (lbf)
```

**Verificado con el manual (pág. 130):** 803 gpm, 11,5 lb/gal, TFA 0,69 in² → **1435 psi, 672 HHP, HSI 5,7, 373 ft/s**.

## 6. Resultado

- Distribución de la presión de bomba: sarta (incluye superficie), anular y mecha, en psi y en %.
- **Total calculado** y **diferencia contra la presión de bomba real** de la pestaña 2.
- ECD al fondo.
- Avisos (lecturas faltantes, fuente de la TVD).

## 7. Limitaciones conocidas

- Las pérdidas en sarta y anular del ejemplo del manual **no se pudieron verificar**, porque el manual no trae los datos de las secciones. La mecha sí está verificada.
- No se descuentan las caídas de presión del **MWD** ni del **motor** (campos `dp_mwd` y `dp_motor` de la pestaña 2): se capturan, pero no entran al total. Para comparar con la presión real, hay que tenerlo en cuenta.
- El caudal suma **todas** las bombas activas, incluidas las marcadas como *bomba del riser*, cuyo caudal no pasa por la sarta. Revisar si aplica en pozos offshore con riser.
- **Edición por defecto inconsistente**: la pantalla abre siempre en la **5ª edición**, pero el **Excel** usa el ajuste del pozo *"Usar API 5ª edición"* (Configuración General), que por defecto está **desactivado** y da la **4ª**. Ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).
- Unidades: todo se calcula en unidades de campo (oilfield), aunque el pozo tenga otro sistema de unidades.
