# 11 — Cálculos de ingeniería

Referencia de las fórmulas del sistema que **no** son de hidráulica ([10](10_HIDRAULICA_API13D.md)), de control de sólidos ([07](07_PESTANA_6_CONTROL_SOLIDOS.md)) ni de volumetría ([09](09_PESTANA_8_VOLUMETRIA_INVENTARIO.md)). Todas trabajan en **unidades de campo**: ft, in, bbl, gpm, lb/gal y psi.

---

## Geometría y volúmenes del hoyo (pestaña 4)

Motor: `geometria_pozo.py`. Arma el pozo con `calcular_geometria_reporte()` en `views_daily_reports.py`.

### Fórmulas base (1029,4 = in² → bbl/ft)

```
Capacidad interna    (bbl/ft) = ID² / 1029.4
Capacidad anular     (bbl/ft) = (D_confinamiento² − OD²) / 1029.4
Desplazamiento acero (bbl/ft) = (OD² − ID²) / 1029.4
```

### Corrección por juntas (tool joints)

En drill pipe y heavy weight, la junta tiene un ID menor y un OD mayor que el cuerpo del tubo. ONE-TRAX pondera linealmente:
```
f = largo_junta_in / (largo_tramo_ft × 12)
capacidad_efectiva = capacidad_cuerpo × (1 − f) + capacidad_junta × f
```
Con 21" de junta en tramos de 31 ft, f = 0,056452. Así se reproducen exactamente los valores del ejemplo **Gusher #2** del manual.

### Perfil de confinamiento (`construir_perfil_confinamiento`)

De superficie hacia abajo, define qué diámetro contiene el fluido a cada profundidad:

1. **Riser** (si el pozo es offshore y lo usa): desde 0 hasta su longitud, con el ID del riser. Si no hay longitud, se usa Air Gap + Water Depth.
2. **Revestidores**: por su ID, desde superficie (o desde el tope del liner si `top_of_liner_ft > 0`) hasta su profundidad. Donde se solapan, manda el de menor diámetro.
3. **Hoyo abierto**: debajo del último revestidor, con el diámetro de la barrena corregido por washout (si falta, el tamaño de la barrena; si falta, el diámetro de hoyo del intervalo de costo).
4. **Hoyo piloto** (opcional): desde la profundidad actual hasta la del piloto, con su propio diámetro.

Fondo del hoyo = máx(profundidad actual, profundidad de la barrena, profundidad del piloto).

### Sarta (`construir_perfil_sarta`)

Los tramos se apilan **desde la mecha hacia arriba**: la base del tramo 1 queda en la profundidad de la barrena. El pozo se corta en cada frontera de confinamiento **y** en cada frontera de tramo. Cada sección entrega su volumen interno y anular. Debajo de la mecha se calcula como hoyo sin tubería ("Bajo la mecha").

### Totales

Volumen de sarta, anular, bajo la mecha, **total** (= sarta + anular + bajo mecha), desplazamiento de acero y:

```
Fondo arriba (emboladas) = volumen anular / bbl por embolada de UNA bomba (la primera activa)
Fondo arriba (minutos)   = volumen anular × 42 / caudal total de las bombas activas
```

Esta combinación, emboladas contadas contra una bomba y minutos con el caudal total, reproduce los valores del manual.

---

## Registro direccional: curvatura mínima

Función `calcular_survey_curvatura_minima()` en `views_daily_reports.py`. Se ejecuta al guardar las estaciones del Well Survey.

Entre dos estaciones (MD₁, I₁, A₁) → (MD₂, I₂, A₂):
```
cos β = cos(I₂ − I₁) − sen I₁ · sen I₂ · (1 − cos(A₂ − A₁))
RF    = (2/β) · tan(β/2)         (RF = 1 si β ≈ 0)
ΔTVD  = ΔMD/2 · (cos I₁ + cos I₂) · RF
ΔN    = ΔMD/2 · (sen I₁ cos A₁ + sen I₂ cos A₂) · RF
ΔE    = ΔMD/2 · (sen I₁ sen A₁ + sen I₂ sen A₂) · RF
DLS   = β(°) / ΔMD × 100          (°/100 ft)
```

"Sección vertical" = √(N² + E²), es decir, el **desplazamiento horizontal total** (*closure*). No se proyecta sobre un azimut de sección vertical.

> Observación: para la primera estación, cuando MD > 0, la TVD se calcula como `MD·cos I` y la sección como `MD·sen I`, pero ese desplazamiento **no se suma** a los acumulados N/E. Si la primera estación no está en superficie, la sección vertical de las siguientes queda subestimada. Recomendación: empezar siempre el survey con la estación MD = 0 (ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)).

---

## Bombas y boquillas

Modelo `ReporteDiarioBomba` (bomba **tríplex**):
```
Desplazamiento (bbl/emb) = 0.000243 × camisa(in)² × carrera(in) × eficiencia
Desplazamiento (gal/emb) = bbl/emb × 42
Caudal (gpm)             = gal/emb × SPM            (0 si la bomba no está "en el reporte")
```
El campo de vástago (*rod diameter*) de las bombas dúplex se guarda, pero **no** entra en la fórmula.

Boquillas (`ReporteDiarioBoquilla`):
```
Área (in²) = cantidad × π/4 × (tamaño/32)²
TFA = Σ áreas
```

---

## Reología de Bingham (pestaña 3)

```
PV = R600 − R300         (≥ 0)
YP = R300 − PV           (≥ 0)
```

---

## Balance de sólidos (pestaña 3)

Métodos de `ReporteDiarioMudCheck`. Se usa la densidad de retorta si existe; si no, la densidad del lodo. Las GE por defecto son HGS 4,20, LGS 2,60 y aceite 0,70 (WBM) u 0,80 (OBM).

### Base agua (`calcular_solids_analysis_wbm`)

1. **KCl** a partir de K⁺: `KCl mg/l = K⁺ × 1.9066` → `KCl lb/bbl = mg/l × 0.0003505 × %agua/100` → `% = lb/bbl / (3.5 × 1.984)`.
2. **NaCl** con los cloruros restantes (se descuentan los del KCl): `NaCl lb/bbl = Cl × 1.6485 × 0.0003505 × %agua/100` → `% = lb/bbl / (3.5 × 2.165)`.
3. **Sólidos suspendidos** = %sólidos − %NaCl − %KCl. Balance de masa:
   ```
   GE agua = 1 + (NaCl + KCl lb/bbl)/350
   masa total = (MW/8.33) × 100 ;  masa sólidos = total − agua·GEagua − aceite·GEaceite
   LGS = (GE_HGS·V_ss − masa_ss) / (GE_HGS − GE_LGS) ;  HGS = V_ss − LGS
   LGS lb/bbl = %LGS × 3.5 × GE_LGS
   ```
4. **Bentonita** (desde MBT): `lb/bbl = MBT × 5 × (1 − frac_bent)` (frac_bent por defecto 0,1111). **Sólidos perforados** = LGS − bentonita (− concentración de químicos en lb/bbl).

### Base aceite/sintético (`calcular_solids_analysis_obm`)

1. **Relación aceite/agua** = aceite/(aceite+agua) : agua/(aceite+agua).
2. **Salinidad**: `% sal en peso = Cl_salmuera × factor / 10000`, con factor 1,565 (CaCl2) o 1,6485 (NaCl). `sal lb/bbl = %p/(100−%p) × %agua × 3.5`.
3. **Sólidos ajustados** = %sólidos − volumen de sal (GE de la sal 2,15 CaCl2 o 2,165 NaCl).
4. **GE promedio de sólidos**, **LGS** y **HGS** por balance de masa, con salmuera = agua + sal. **Se permiten valores negativos** para detectar inconsistencias de laboratorio en la retorta.

> Observaciones:
> - La opción **ecuación de sólidos M-I / API** (del pozo y del reporte) se guarda, pero **no cambia el cálculo**: siempre se aplica la misma ecuación.
> - En base agua **no** se calcula `HGS lb/bbl` (solo el %).
>
> Ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).

---

## Otras constantes

| Constante | Valor | Dónde |
|---|---|---|
| Galones por barril | 42 | varios |
| lb/bbl de agua (GE 1) | 350 | `volumetria.py` |
| in² → bbl/ft | 1029,4 | `geometria_pozo.py`, `control_solidos.py` |
| Presión hidrostática | 0,052 psi/ft por lb/gal | ECD |
