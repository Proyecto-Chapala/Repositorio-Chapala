# Módulos opcionales

Módulos de ONE-TRAX que se construyeron completos pero que **AOS al parecer no usa**. Nada de lo demás depende de ellos: si quedan vacíos no afectan ningún cálculo, costo ni el Excel.

| Módulo | Dónde se abre | Modelo |
|---|---|---|
| Observaciones IFE | Pestaña 6 | `ObservacionesIFE` (1:1 con el reporte) |
| Análisis de sólidos por equipo | Pestaña 6 | `AnalisisSolidosEquipo` |
| Retención en recortes | Pestaña 6 (consulta también desde la 8) | `RetencionRecortes` |
| Eventos no programados | Pestañas 5 y 7 | `EventoNoProgramado` |
| Evaluación de benchmark | Pestaña 8 (solo consulta, no guarda nada) | — |

| | |
|---|---|
| Vistas | `operaciones/views_opcionales.py` |
| Modelos | `operaciones/models_opcionales.py` (migración `0021`) |
| JS / CSS | `reporte_opcionales.js`, `reporte_opcionales.css` |

Los equipos se guardan por **número de serie + copia del nombre**, porque la lista de equipos activos del pozo se guarda recreando filas. Solo se pueden elegir equipos activos del pozo (o el que ya tenía la muestra).

---

## Observaciones IFE

Cuatro textos libres de la pantalla principal de *Solids Equipment* ("IFE Remarks"):

| Campo | Contenido |
|---|---|
| `fluidos_resumen` | Fluidos de perforación — resumen |
| `fluidos_plan` | Fluidos de perforación — plan siguiente |
| `solidos_resumen` | Control de sólidos — resumen |
| `solidos_plan` | Control de sólidos — plan siguiente |

`GET` o `POST /api/pozos/<pk>/daily-report/<reporte_pk>/ife/`.

---

## Muestras por equipo (datos comunes)

El análisis de sólidos y la retención comparten estos campos:

| Campo | Regla |
|---|---|
| Equipo (número de serie) | De los equipos activos del pozo |
| Hora de inicio y fin | `HH:MM` |
| Orden de impresión | 1 a 99 |
| Profundidad medida (ft) | ≥ 0 |
| Profundidad perforada representada (ft) | ≥ 0 |
| Comentarios | Hasta 255 caracteres |

Los datos específicos de la prueba se guardan en un campo JSON `datos`. Los resultados **no se guardan**: se calculan al consultar.

## Análisis de sólidos por equipo

Corre **el mismo balance de sólidos de la pestaña 3** sobre una muestra tomada en un equipo (por ejemplo, la descarga de una centrífuga). Tipo de muestra en texto libre.

| Tipo de lodo | Entradas | Resultados |
|---|---|---|
| Base agua | peso, agua %, aceite %, sólidos %, K⁺ de KCl, SG sólidos perforados, SG aditivo, SG aceite, fracción de bentonita, concentración de químicos, MBT, cloruros | NaCl, KCl, LGS, bentonita, sólidos perforados, HGS (% y lb/bbl), SG promedio de sólidos, relación **inerte / reactivo** (sólidos perforados ÷ bentonita) |
| Base aceite | peso, agua %, aceite %, sólidos %, SG aceite, SG aditivo, SG sólidos perforados, cloruros, sal (CaCl2 o NaCl) | Sal % peso y lb/bbl, sólidos corregidos, OWR, LGS, HGS, SG promedio de sólidos |

Aviso si agua + aceite + sólidos no suman 100 % (tolerancia 0.5).

`GET /muestras/solidos/`, `POST /muestras/solidos/guardar/`, `POST /muestras/solidos/<id>/eliminar/`.

## Retención en recortes (Cuttings Retention)

Prueba de retorta sobre recortes para medir cuánto fluido base se pierde pegado a ellos.

Entradas: peso del lodo, % de fluido base en el lodo, SG del fluido base, SG de los sólidos, celda vacía, celda con recorte húmedo, celda con recorte seco, probeta vacía, agua recuperada (cc), probeta con fluido total. Además, diámetro de la mecha.

Cálculo (verificado con el manual, pág. 114):

```
húmedo (g)       = celda con húmedo − celda vacía
seco (g)         = celda con seco − celda vacía
fluido base (g)  = probeta total − probeta vacía − agua
factor de balance = (seco + agua + fluido base) / húmedo
g/kg y % en peso de fluido base sobre recorte húmedo y sobre recorte seco
lodo en recortes (bbl/bbl) = [fluido base / SG fluido base / (% fluido base / 100)] ÷ [seco / SG sólidos]
```

Aviso si el factor de balance sale fuera de 0.95-1.05 ("la prueba no cierra").

El "lodo en recortes" es una **reconstrucción propia**: en el ejemplo del manual da aproximadamente 1.5 % más que ONE-TRAX.

`GET /muestras/retencion/`, `POST /muestras/retencion/guardar/`, `POST /muestras/retencion/<id>/eliminar/`.

---

## Eventos no programados (Unscheduled Events)

Registro de problemas del pozo. Se registran en un reporte, pero la lista muestra **los de todo el pozo** (cada uno con su fecha); un evento solo se edita o borra desde el reporte en que se registró.

| Campo | Regla |
|---|---|
| Categoría | Fluidos y perforación, Calidad de producto, Logística, Falla de equipo |
| Tipo de problema | **Obligatorio** (por ejemplo: pérdida de circulación, entrega tardía) |
| Tipo de fluido | Se sugiere el fluido del reporte |
| Descripción, causa sospechada, descripción de la pérdida | Texto libre |
| Tiempo perdido (h) | 0 a 10 000 |
| Volumen perdido (bbl) | ≥ 0 |
| Costo estimado | ≥ 0 |

Los eventos **no** alimentan la volumetría ni el resumen de costos.

`GET /eventos/`, `POST /eventos/guardar/`, `POST /eventos/<id>/eliminar/`.

---

## Evaluación de benchmark

Compara los **objetivos** del *Benchmark Setup* del pozo con los **valores medidos** en los chequeos de lodo (pestaña 3), para el pozo completo y para cada intervalo. No guarda nada.

### Columnas

- **Pozo completo**: todos los reportes hasta la fecha del reporte abierto.
- **Un intervalo por cada intervalo de revestimiento**: los reportes cuyo intervalo de costo (pestaña 4) es ese intervalo.

Cada columna informa cuántos reportes cubre y la profundidad mínima y máxima.

### Cómo se vincula un parámetro con un dato del chequeo

Por **palabras clave en la descripción del parámetro** (español o inglés):

| Palabras | Campo del chequeo |
|---|---|
| hthp, hpht | Filtrado HPHT |
| api fluid, filtrado api, fluid loss, filtrado | Filtrado API |
| mud weight, peso del lodo, densidad | Peso del lodo |
| funnel, embudo | Viscosidad de embudo |
| gel 10s / 10 seg | Gel 10 s |
| gel 10m / 10 min | Gel 10 min |
| pv, plastic, plástica | PV |
| yp, yield, cedente | YP |
| mbt | MBT |
| sand, arena | Arena % |
| solids, sólidos | Sólidos % |
| chloride, cloruro | Cloruros |
| stability, estabilidad | Estabilidad eléctrica |
| ph | pH |

Si la descripción no contiene ninguna, el parámetro sale "no vinculado" (se muestra el objetivo sin comparar).

El **tipo de fluido** del parámetro filtra los reportes: WBM solo cuenta reportes WBM o WBM CaCl2; OBM solo OBM o SBM.

### Objetivo

- Tipo MIN_MAX: mínimo y máximo.
- Valor único: si la descripción termina en "min" / "mínimo" o "max" / "máximo" (parámetros separados, como en ONE-TRAX), el valor se toma como ese límite.

### Resultado por celda

Objetivo (mínimo, máximo o valor), mínimo y máximo reales, cantidad de mediciones y **% de mediciones dentro del rango**.

> Todos los chequeos con valor cuentan, incluidos los chequeos 2 a 4. Si se dejaron los valores de ejemplo del primer reporte, distorsionan el resultado (ver [pestanas/PESTANA_3_PROPIEDADES_LODO.md](pestanas/PESTANA_3_PROPIEDADES_LODO.md)).
