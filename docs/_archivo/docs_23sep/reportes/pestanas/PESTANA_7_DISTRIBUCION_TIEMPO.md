# Pestaña 7 — Distribución de tiempo (Time Distribution)

Horas del período del reporte repartidas por actividad del taladro.

| | |
|---|---|
| Vistas | `views_daily_reports._catalogo_tiempo_pozo`, `obtener_o_crear_tiempo`, `_estado_tiempo`, `api_tiempo_detail`, `api_tiempo_guardar` |
| Modelos | `ReporteDiarioTiempo` (1:1), `ReporteDiarioActividadTiempo` |
| Catálogo | `TipoDistribucionTiempo` del pozo (Configuración General → Distribución de Tiempo) |
| JS / CSS | `reporte_tiempo.js`, `reporte_tiempo.css` |

## Horas del período

24 por defecto. Se cambia solo en días especiales:

- primer día del pozo (se empezó a perforar a mitad del período),
- último día (se liberó el taladro),
- cambio de la hora de corte del operador.

Rango: más de 0 y hasta **48 h** (más que eso casi seguro es un error de captura).

## Actividades

- Las actividades **1 a 4** (Alistamiento / Servicio, Perforación, Maniobras, Tiempo No Productivo) aparecen **siempre**, en ese orden.
- Las demás se agregan desde el catálogo del pozo. Solo se ofrecen las de tipo **DF** y **DF/CF** (fluidos de perforación).
- Si el pozo no tiene catálogo (pozos viejos), se siembra el estándar de 20 actividades.

Catálogo estándar: 1 Alistamiento / Servicio del Taladro, 2 Perforación, 3 Maniobras (Viajes), 4 Tiempo No Productivo (DF/CF); 5 Instalación de BOP, 6 Prueba de BOP, 7 Cementación, 8 Acondicionamiento de Hoyo, 9 Acondicionamiento de Lodo, 10 Toma de Núcleos, 11 Registro Direccional, 12 Trabajo Direccional, 13 Pesca, 14 Pérdida de Circulación, 15 Rimado, 16 Reparación del Taladro, 17 Bajada de Revestimiento, 18 Pruebas, 19 Espera de Fraguado de Cemento, 20 Espera por Clima (DF).

## Reglas al guardar

- Horas ≥ 0 y ≤ 48 por fila; se acepta coma decimal (`5,5`).
- No se puede repetir una actividad.
- Una actividad debe existir en el catálogo del pozo; las que ya estaban guardadas se aceptan aunque luego se hayan quitado del catálogo (el histórico no se pierde).
- Las filas opcionales con 0 horas no se guardan; las fijas se muestran igual.
- Se guarda por **número de actividad + copia de la descripción**, no con llave foránea, porque el catálogo del pozo se guarda recreando sus filas.

## Total contra período

```
cuadra = |Σ horas − horas del período| < 0.01
```

Si **no cuadra**, la pantalla lo marca en rojo **pero deja guardar**. Es una decisión del usuario: en campo hay días que no cuadran y el ingeniero decide.

## Eventos no programados

Botón al módulo opcional de eventos. Ver [../MODULOS_OPCIONALES.md](../MODULOS_OPCIONALES.md).
