# Pestaña 5 — Comentarios

Especificación de propiedades del lodo y los tres bloques de texto del día.

| | |
|---|---|
| Vistas | `views_daily_reports.obtener_o_crear_comentarios`, `api_comentarios_detail`, `api_comentarios_guardar` |
| Modelo | `ReporteDiarioComentarios` (1:1 con el reporte) |
| API | `GET/POST /api/pozos/<pk>/daily-report/<reporte_pk>/comentarios/[guardar/]` |

## Especificación de propiedades del lodo

Tres textos cortos (máx. 50 caracteres): **peso del lodo**, **viscosidad** y **filtrado**. Ejemplo: `11.5-12.0`.

Es el **rango objetivo acordado con el operador**, no la medición del día (esa está en los chequeos de la pestaña 3). Como casi nunca cambia, **se hereda del reporte anterior** al abrir la pestaña por primera vez.

## Bloques de texto

| Bloque | Campo | Destino | Reglas |
|---|---|---|---|
| Resumen del día (Mud Recap Remarks) | `mud_recap_remarks` | Una fila del **Well Recap** del pozo | **Una sola línea**: al guardar, los saltos de línea y espacios repetidos se colapsan en un espacio |
| Observaciones y tratamiento | `remarks_and_treatment` | Reporte diario | Actividad y servicio de fluidos del día |
| Observaciones de operaciones | `remarks` | Reporte diario | Operaciones del taladro, normalmente de la hoja IADC |

Los textos **no se heredan**: cada día empieza vacío. Para ayudar a redactar, la pantalla muestra el resumen del día anterior ("Ayer").

`tiene_contenido` indica si ya se escribió algo en cualquiera de los tres bloques.

## Eventos no programados

Desde esta pestaña (y desde la 7) se abre el módulo opcional de eventos no programados. Ver [../MODULOS_OPCIONALES.md](../MODULOS_OPCIONALES.md).
