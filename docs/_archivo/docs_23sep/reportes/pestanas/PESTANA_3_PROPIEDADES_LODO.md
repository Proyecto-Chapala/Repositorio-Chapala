# Pestaña 3 — Propiedades del lodo (Mud Properties)

Hasta **4 chequeos de lodo** por día, configuración del análisis de sólidos y propiedades extra.

| | |
|---|---|
| Vistas | `views_daily_reports.api_mud_properties_detail`, `api_mud_properties_guardar`, `obtener_o_crear_mud_checks` |
| Modelos | `ReporteDiarioMudConfig` (1:1), `ReporteDiarioMudCheck` (1 a 4), `PropiedadExtraFluido`, `ReporteDiarioMudExtraValue` |
| Cálculos | Métodos de `ReporteDiarioMudCheck` en `models_daily_reports.py` |

## Primera apertura del día

Se crean la configuración y los 4 chequeos. Si hay reporte anterior, cada chequeo copia los valores del chequeo del mismo número del día anterior.

En el **primer reporte del pozo** los chequeos se crean con **datos de ejemplo** de ONE-TRAX: el chequeo 1 (principal) trae un lodo completo de 10.5 lb/gal (R600 50, R300 38, PV 12, YP 26, cloruros 12 000, MBT 15...) y los chequeos 2 a 4 traen peso 10.5, embudo 45 y horas 15:00, 21:00 y 03:00.

> Hay que **reemplazar o borrar** esos valores el primer día. Si no, pasan a los días siguientes (se heredan), la hidráulica calcula con el lodo de ejemplo y la evaluación de benchmark cuenta los chequeos 2 a 4 como mediciones reales.

## Configuración

| Campo | Default | Uso |
|---|---|---|
| Ecuación de sólidos | M-I | M-I o API |
| Lodo densificado | Sí | |
| SG aceite base | 0.84 | Default del campo `oil_sg` de los chequeos |
| SG material densificante | 4.20 | Default de `wt_additive_sg` (barita) |
| SG sólidos perforados | 2.60 | Default de `drill_solids_sg` |
| Sal de la fase interna (OBM) | CaCl2 | CaCl2 o NaCl |

El **tipo de lodo del reporte** (WBM, WBM CaCl2, OBM, SBM) decide qué análisis de sólidos se ejecuta: OBM y SBM usan el de base aceite; los demás, el de base agua.

## Chequeo de lodo

El **chequeo principal** (`is_primary`) es el que se imprime y el que usa la hidráulica. Se marca uno; el servidor desmarca los demás.

| Grupo | Campos |
|---|---|
| Muestra | Origen (In, Pit...), hora, temperatura de línea de flujo, profundidad, TVD |
| Densidad | Peso del lodo (lb/gal), temperatura, viscosidad de embudo (s/qt) |
| Reología | Temperatura de reología (120 °F por defecto), lecturas R600, R300, R200, R100, R6, R3; PV, YP; geles 10 s, 10 min, 30 min |
| Filtrado | API y HPHT (cc/30 min), revoque API y HPHT (1/32") |
| Retorta | Sólidos, aceite, agua y arena (% vol) |
| Entradas del análisis | Peso de lodo para retorta, temperatura, K⁺ de KCl (mg/L), SG aditivo, SG aceite, fracción de bentonita (0.1111), concentración de químicos (lb/bbl), SG sólidos perforados |
| Química | pH y temperatura, Pm, Pf, Mf, cloruros, dureza Ca⁺⁺, MBT, estabilidad eléctrica, cal en exceso |

### PV y YP

Si vienen R600 y R300, el servidor **siempre** recalcula (modelo plástico de Bingham):

```
PV = R600 − R300
YP = R300 − PV            (= 2·R300 − R600)
```

Si faltan las lecturas, se aceptan PV y YP escritos a mano.

### Análisis de sólidos base agua (WBM)

`calcular_solids_analysis_wbm()`:

```
KCl (lb/bbl) = K⁺ × 1.9066 × 0.0003505 × (agua% / 100)       KCl %vol = KCl lb/bbl ÷ (3.5 × 1.984)
Cl⁻ de NaCl  = cloruros totales − cloruros aportados por el KCl
NaCl (lb/bbl) = Cl⁻NaCl × 1.6485 × 0.0003505 × (agua% / 100)  NaCl %vol = NaCl lb/bbl ÷ (3.5 × 2.165)
Sólidos suspendidos = sólidos% − NaCl% − KCl%
SG del agua = 1 + (NaCl + KCl lb/bbl) / 350
masa total   = (peso del lodo / 8.33) × 100
masa líquido = agua% × SG agua + aceite% × SG aceite
masa sólidos = masa total − masa líquido
LGS% = (SG_HGS × Vss − masa sólidos) / (SG_HGS − SG_LGS)       HGS% = Vss − LGS%
LGS lb/bbl = LGS% × 3.5 × SG_LGS
Bentonita lb/bbl = MBT × 5 × (1 − fracción bentonita)          Bentonita % = lb/bbl ÷ (3.5 × SG_LGS)
Sólidos perforados lb/bbl = LGS lb/bbl − bentonita − concentración de químicos
Sólidos perforados % = LGS% − bentonita%
```

Los valores negativos se llevan a 0 en WBM.

### Análisis de sólidos base aceite (OBM / SBM)

`calcular_solids_analysis_obm()`:

```
Relación aceite/agua = aceite% / (aceite% + agua%) : agua% / (aceite% + agua%)
Sal % peso (si no se escribe) = (cloruros / (agua%/100)) × factor / 10000
      factor = 1.565 para CaCl2, 1.6485 para NaCl
Sal lb/bbl = (sal% / (100 − sal%)) × agua% × 3.5
Volumen de sal = sal lb/bbl ÷ (3.5 × SG sal)      SG sal: CaCl2 2.15, NaCl 2.165
Sólidos corregidos % = sólidos% − volumen de sal
masa salmuera = agua% + sal lb/bbl / 3.5
SG promedio de sólidos = masa sólidos / sólidos corregidos
LGS / HGS: igual que en WBM, sobre los sólidos corregidos
```

En OBM **se permiten valores negativos**: indican que los datos de retorta son físicamente inconsistentes (error de laboratorio), en lugar de ocultarlo.

### Sobrescritura manual

Después del cálculo, si el usuario envió valores para los resultados (NaCl, KCl, LGS, bentonita, sólidos perforados, HGS, sólidos corregidos, OWR, SG promedio), se guardan los del usuario.

## Propiedades extra (Extra Report Labels)

Etiquetas adicionales **por pozo** y por tipo de fluido (WBM u OBM), hasta 60 cada uno. Se configuran desde el hub de reportes ("Etiquetas de Propiedades Extra"), donde también se pueden cargar plantillas predefinidas (por ejemplo Statoil) o guardar las propias como plantilla.

Cada chequeo guarda su valor para cada etiqueta (`ReporteDiarioMudExtraValue`). `orden_impresion` decide si y en qué orden salen en el Excel (0 = no se imprime).

## Qué usa esta pestaña después

| Dato | Lo usa |
|---|---|
| Peso del lodo, PV, YP y lecturas del chequeo principal | Hidráulica (pestaña 8) |
| Todos los valores de todos los chequeos | Evaluación de benchmark (pestaña 8) |
| Especificación de lodo | Se captura en la pestaña 5, no aquí |
| Cálculo de sólidos | Se reutiliza en el análisis de sólidos por equipo (módulo opcional) |
