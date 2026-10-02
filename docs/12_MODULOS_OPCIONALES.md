# 12 — Módulos opcionales y evaluación de benchmark

Archivos: `models_opcionales.py` (migración 0021), `views_opcionales.py` y `reporte_opcionales.js/.css`.

> **Decisión del usuario: los módulos opcionales son 100 % opcionales.** Ningún otro cálculo depende de ellos: si no se usan, nada cambia. Según las notas del código, AOS al parecer no los usa hoy.

| Módulo | Dónde se abre | Guarda | API |
|---|---|---|---|
| Observaciones IFE | Pestaña 6 → Opcionales | Sí | `…/ife/` (GET y POST) |
| Análisis de sólidos por equipo | Pestaña 6 → Opcionales | Sí | `…/muestras/solidos/` |
| Retención en recortes | Pestaña 6 → Opcionales | Sí | `…/muestras/retencion/` |
| Eventos no programados | Pestañas 5 y 7 (ventana `#enModal`) — **botón oculto desde el 02-oct-2026** | Sí | `…/eventos/` |
| Evaluación de benchmark | Pestaña 8 | **No** (consulta) | `…/benchmark/` |

---

## 1. Observaciones IFE

Un registro por reporte (`ObservacionesIFE`, OneToOne) con los cuatro textos *IFE Remarks* de ONE-TRAX:

- Fluidos de perforación: resumen y plan siguiente
- Control de sólidos: resumen y plan siguiente

## 2. Análisis de sólidos por equipo (`AnalisisSolidosEquipo`)

Muestras tomadas **en un equipo** (por ejemplo, la descarga de una centrífuga), con el mismo balance de sólidos de la pestaña 3.

- Datos comunes (base abstracta `_MuestraEquipo`): equipo (**serie** + copia del nombre), hora de inicio y fin, orden de impresión, profundidad medida y perforada representada, comentarios.
- Tipo de lodo (WBM/OBM), tipo de muestra y los datos de laboratorio en un campo JSON `datos`.
- Cálculo: se crea un `ReporteDiarioMudCheck` **sin guardar** y se ejecuta `calcular_solids_analysis_wbm/obm`. En WBM se agregan HGS lb/bbl, GE promedio de sólidos y relación **inerte/reactivo** (sólidos perforados / bentonita).
- Aviso si agua + aceite + sólidos no suman 100 % (±0,5).

## 3. Retención en recortes (`RetencionRecortes`)

Prueba de retorta sobre recortes (*Cuttings Retention*). Entradas: peso del lodo, % y GE del fluido base, GE de sólidos, pesos de la celda (vacía, con húmedo, con seco), probeta vacía, agua (cc), probeta total y diámetro de la mecha.

```
húmedo (g)       = celda con húmedo − celda vacía
seco (g)         = celda con seco − celda vacía
fluido base (g)  = probeta total − probeta vacía − agua
factor de balance = (seco + agua + fluido base) / húmedo     → aviso si sale de 0,95–1,05
retención        = fluido base / húmedo (g/kg y %)  ·  fluido base / seco (g/kg y %)
lodo en recortes = [fluido base / GE_fb / (%fb/100)] / (seco / GE_sólidos)   (bbl lodo / bbl recortes)
```

**Verificado con el manual (pág. 114):** húmedo 30,7, seco 20,7, fluido base 5,2, 169,38 / 251,21 g/kg. El *lodo en recortes* (MOC) es una **reconstrucción**: en el ejemplo da ~1,5 % más que ONE-TRAX.

API genérica de muestras (clave `solidos` o `retencion`):
- `GET  …/muestras/<clave>/` · lista del reporte
- `POST …/muestras/<clave>/guardar/` · crea o actualiza
- `POST …/muestras/<clave>/<id>/eliminar/`

Solo se aceptan equipos de la lista de equipos activos del pozo.

## 4. Eventos no programados (`EventoNoProgramado`)

> **Oculto en pantalla desde el 02-oct-2026** a pedido de AOS ("que no confunda al ingeniero"): los botones `[data-en-abrir]` llevan `hidden`. El código, la API y el modelo siguen; los eventos ya cargados salen en el reporte final. Para reactivarlo, quitar `hidden` de los dos botones en `reporte_diario_detalle.html`.

Registro de problemas del pozo (*Unscheduled Events*).

| Campo | Nota |
|---|---|
| Categoría | Fluidos y perforación · Calidad de producto · Logística · Falla de equipo |
| Tipo de problema | **Obligatorio** (ej. pérdida de circulación, entrega tardía) |
| Tipo de fluido, descripción, causa sospechada, descripción de la pérdida | Texto |
| Tiempo perdido (h), volumen perdido (bbl), costo estimado | Números |

La ventana muestra **todos los eventos del pozo**, pero un evento **solo se edita o elimina desde el reporte en que se registró**. Mensaje: *"El evento no existe en este reporte (se edita desde el reporte en que se registró)."*

## 5. Evaluación de benchmark (pestaña 8, solo consulta)

Compara los **objetivos** de *Configuración de Benchmark* con los **valores reales** de los chequeos de lodo (pestaña 3), hasta la fecha del reporte.

**Columnas**: *Pozo completo* + una por cada **intervalo de revestimiento**. Los reportes se asignan a un intervalo por su **intervalo de costo** (pestaña 4). Cada columna muestra cuántos reportes tiene y su rango de profundidad.

**Qué campo del chequeo corresponde a cada parámetro**: se deduce por **palabras clave** en la descripción del parámetro (tabla `VINCULOS`):

| Palabras clave (en la descripción) | Campo del chequeo |
|---|---|
| hthp / hpht | Filtrado HPHT |
| api fluid, filtrado api, fluid loss, filtrado | Filtrado API |
| mud weight, peso del lodo, densidad | Densidad |
| funnel, embudo | Viscosidad de embudo |
| gel 10s / gel 10m | Geles |
| pv, plastic, plástica | PV |
| yp, yield, cedente | YP |
| mbt · sand/arena · solids/sólidos · chloride/cloruro · stability/estabilidad · ph | campo correspondiente |

Si la descripción no coincide con ninguna, el parámetro aparece sin valores reales. **Consejo**: nombrar los parámetros del catálogo con esas palabras.

**Filtro por tipo de fluido**: los parámetros WBM solo miran reportes WBM y WBM_CACL2. Los OBM, reportes OBM y SBM.

**Mín/máx**: se usan los objetivos MIN y MAX. Si solo hay un VALOR y la descripción termina en "min"/"mínimo" o "max"/"máximo" (ignorando paréntesis), el valor se toma como ese límite, como hace ONE-TRAX con parámetros separados.

**Resultado por celda**: objetivo (mín, máx o valor), **rango real** (mínimo y máximo medidos) y **% de mediciones dentro del objetivo**.
