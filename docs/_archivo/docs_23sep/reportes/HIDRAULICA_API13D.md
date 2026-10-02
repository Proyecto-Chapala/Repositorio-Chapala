# Hidráulica — API RP 13D, 4ª y 5ª edición

Cálculo de pérdidas de presión, velocidades, régimen de flujo, ECD y parámetros de la mecha. Es **solo consulta**: toma los datos que ya existen en el reporte y no guarda nada.

| | |
|---|---|
| Motor | `operaciones/hidraulica.py` (sin Django) |
| Vista | `views_hidraulica.api_hidraulica_detail` y `calcular_hidraulica_reporte` (también la usa el Excel) |
| API | `GET /api/pozos/<pk>/daily-report/<reporte_pk>/hidraulica/?edicion=4|5` |
| Pantalla | Pestaña 8 → 3 Hidráulica (`reporte_hidraulica.js`) |

## Datos de entrada

| Dato | De dónde sale |
|---|---|
| Caudal Q (gpm) | Suma del caudal de las bombas de la pestaña 2; si da 0, el "caudal de bomba" escrito en la mecha |
| TFA (in²) | Boquillas de la pestaña 2 |
| Diámetro de la mecha | Pestaña 2 |
| Peso del lodo ρ (lb/gal) | **Chequeo principal** de la pestaña 3 (si no hay principal con reología, el primero que tenga) |
| PV, YP y lecturas R600…R3 | Mismo chequeo |
| Secciones del pozo y la sarta | Motor de geometría (pestaña 4). Se ignoran las secciones sin tubería y las de bajo la mecha |
| TVD de cada profundidad | 1) Estaciones del Registro Direccional (interpolación lineal; extrapola con la última pendiente). 2) Si no hay estaciones: proporción TVD/MD de la pestaña 1. 3) Si tampoco: pozo vertical |
| Temperatura (solo 5ª) | Temperatura de superficie y gradiente de Información General del Pozo |
| Equipo de superficie | Código, presión y caudal de referencia de la pestaña 2 |
| Presión de bomba real | Pestaña 2 (para comparar con la calculada) |

Si falta algo, la respuesta trae la lista `faltan` y no calcula.

Unidades de campo: Q gal/min, D in, V ft/min, ρ lb/gal, L ft, ΔP psi.

---

## Reología

Lecturas faltantes: si no hay R600 o R300 pero sí PV y YP, se reconstruyen: `R600 = 2·PV + YP`, `R300 = PV + YP`.

### 4ª edición — ley de potencia

```
Tubería:  n = 3.32 · log(R600 / R300)        K = 5.11 · R600 / 1022ⁿ
Anular:   n = 0.657 · log(R100 / R3)         K = 5.11 · R100 / 170.2ⁿ
```

Si faltan R100 o R3, el anular usa los parámetros de la tubería (y avisa). K en dina·sⁿ/cm².

### 5ª edición — Herschel-Bulkley

```
τy = 1.066 · (2·R3 − R6)                        (0 si faltan R6 y R3; se avisa)
n  = 3.32 · log((2·PV + YP − τy') / (PV + YP − τy'))      con τy' = τy / 1.066
k  = 1.066 · (PV + YP − τy') / 511ⁿ
```

Los mismos parámetros para tubería y anular. k en lbf·sⁿ/100 ft². τy se limita a menos del 99 % de (PV + YP).

La reología **no se corrige por temperatura ni presión**: eso exige lecturas del viscosímetro a varias temperaturas, que el reporte no captura. La temperatura anular se informa pero no modifica el cálculo.

La pantalla muestra el **reograma**: las lecturas que predice el modelo a 3, 6, 10, 30, 60, 100, 200, 300, 600 y 1000 rpm, junto con las medidas.

---

## Flujo en cada sección

```
Velocidad             V = 24.48 · Q / D²                        tubería: D = ID
                                                                anular: D² = Dhoyo² − OD², Dh = Dhoyo − OD
Pérdida por fricción  ΔP = 1.076·10⁻⁵ · f · ρ · V² · L / Dh
```

### 4ª edición

```
Viscosidad efectiva tubería  μ = 100·K · (96·V / D)^(n−1) · ((3n + 1) / 4n)ⁿ
Viscosidad efectiva anular   μ = 100·K · (144·V / Dh)^(n−1) · ((2n + 1) / 3n)ⁿ
Reynolds                     Re = 15.467 · V · Dh · ρ / μ
Límites                      Re laminar = 3470 − 1370·n     Re turbulento = 4270 − 1370·n
Fanning                      laminar f = 16 / Re
                             turbulento f = a / Re^b,  a = (log n + 3.93) / 50,  b = (1.75 − log n) / 7
                             transición: interpolación lineal entre los dos límites
```

### 5ª edición

```
α = 0 tubería, 1 anular
G = ((3 − α)·n + 1) / ((4 − α)·n) · (1 + α/2)
γw = 1.6 · G · V / Dh
τw = ((4 − α)/(3 − α))ⁿ · τy + k · γwⁿ
Re = ρ · V² / (19.36 · τw)
f laminar = 16/Re      f transición = 16·Re / Re_laminar²      f turbulento = a / Re^b
f = (f_lam¹² + (f_tr⁻⁸ + f_tu⁻⁸)^(−1.5))^(1/12)
```

### Velocidad crítica

Velocidad anular a la que el flujo deja de ser laminar. Se busca por bisección (60 iteraciones entre 0 y 20 000 ft/min) el punto donde Re = Re laminar.

---

## Mecha

Coeficiente de descarga 0.95 (incluido en la constante 10858):

```
ΔP mecha           = ρ · Q² / (10858 · TFA²)
HHP                = ΔP · Q / 1714
HSI                = HHP / (π/4 · Dmecha²)
Velocidad de chorro = 0.3208 · Q / TFA          (ft/s)
Fuerza de impacto  = ρ · Q · Vj / 1932          (lbf)
```

### Verificación contra el manual (pág. 130)

| Dato | Manual | Sistema |
|---|---|---|
| Entrada | 803 gpm, 11.5 lb/gal, TFA 0.69 in², mecha 12¼" | Igual |
| Pérdida en la mecha | 1435 psi | 1434 psi (diferencia de redondeo) |
| HHP | 672 | 672 |
| HSI | 5.7 | 5.7 |
| Velocidad de chorro | 373 ft/s | 373 ft/s |

---

## Equipo de superficie

Dos formas, en este orden:

1. **Presión de referencia**: si en la pestaña 2 hay presión **y** caudal de referencia, se escala al caudal actual (tiene prioridad sobre el código):
   ```
   ΔP superficie = P_ref · (Q / Q_ref)^1.86
   ```
2. **Caso estándar**: longitud equivalente de tubería de 3.826" de ID, calculada con la reología del día:

| Código (pestaña 2) | Caso API | Longitud equivalente |
|---|---|---|
| 1 | Manual | Se usa la presión escrita en la pestaña 2 tal cual |
| 2 | Caso 1 | 2600 ft |
| 3 | Caso 2 | 946 ft |
| 4 | Caso 3 | 610 ft |
| 5 | Caso 4 | 424 ft |

Si no hay datos (código 1 sin presión), la pérdida de superficie es 0 y se avisa.

Hasta el 25/09/2026 esta tabla estaba corrida un caso respecto a la pantalla (el código 1 calculaba como caso API 1). Los reportes con código 1 y sin presión ahora muestran 0 psi de superficie en lugar de ~2600 ft equivalentes.

---

## ECD

Se acumula la pérdida anular desde la superficie hacia abajo. En la base de cada sección:

```
ECD = ρ + ΔP_anular_acumulada / (0.052 · TVD)
```

**ECD en el fondo** = el de la última sección.

## Resultados

| Grupo | Contenido |
|---|---|
| Por sección | Descripción, longitud, diámetros, velocidad y régimen en la sarta, velocidad anular, velocidad crítica, régimen anular, pérdidas en sarta y anular, MD, TVD, ECD, temperatura anular (5ª), PV/YP usadas (5ª) |
| Totales | Sarta (secciones + superficie), superficie, anular, mecha, **total**, porcentaje de cada parte y **diferencia contra la presión de bomba real** |
| Mecha | Pérdida, HHP, HSI, velocidad de chorro, fuerza de impacto, % del total |
| Avisos | Lecturas faltantes, fuente de la TVD, disponibilidad de temperatura |
