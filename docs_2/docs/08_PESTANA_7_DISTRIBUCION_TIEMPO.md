# 08 — Pestaña 7: Distribución de tiempo

Archivos: `models_daily_reports.py` (`ReporteDiarioTiempo`, `ReporteDiarioActividadTiempo`, migración 0016), `views_daily_reports.py` (`api_tiempo_detail`, `api_tiempo_guardar`) y `reporte_tiempo.js/.css`.

## Propósito

Registrar **cuántas horas dedicó el taladro a cada actividad** durante el período del reporte, según la hoja IADC del día. Equivale a *Time Distribution* de ONE-TRAX.

## Pantalla

1. **Período del reporte**: horas que cubre el reporte. Por defecto **24**, editable. Es distinto de 24 el primer día del pozo, el último, o cuando cambia la hora de corte.
2. **Actividades del taladro**:
   - Las **4 actividades principales siempre aparecen**, aunque tengan 0 h: 1 Alistamiento/Servicio del taladro, 2 Perforación, 3 Maniobras (viajes) y 4 Tiempo no productivo.
   - Las demás se **agregan desde el catálogo del pozo** (*Configuración General → Distribución de tiempo*). Solo se ofrecen las de tipo **DF** y **DF/CF**.
3. **Total**: se compara con las horas del período. **Si no coincide, se marca en rojo, pero se deja guardar** (decisión del usuario). Tolerancia: 0,01 h.
4. Botón **Eventos no programados**: abre la ventana compartida con la pestaña 5 (ver [12](12_MODULOS_OPCIONALES.md)).

## Reglas de guardado (`api_tiempo_guardar`)

| Regla | Mensaje |
|---|---|
| Horas del período > 0 | *"Horas del período: debe ser mayor que cero."* |
| Horas por fila entre 0 y **48** (se acepta coma decimal) | *"…las horas no pueden ser negativas."* / límite de 48 h, porque más que eso es casi seguro un error de captura |
| Actividad no repetida | *"La actividad '…' está repetida."* |
| Actividad existente en el catálogo del pozo | *"Fila N: la actividad X no existe en la configuración del pozo."* |

Las actividades se guardan por **número** con **copia de la descripción** (`tipo_numero`, `descripcion`), porque el catálogo del pozo se guarda borrando y recreando filas. Si luego se renombra una actividad en el catálogo, los reportes viejos conservan el nombre con que se registraron.

Si un pozo antiguo no tiene catálogo, se siembra el estándar de 20 actividades la primera vez que se abre la pestaña.

## Catálogo estándar (sembrado al crear el pozo)

| # | Actividad | Tipo |
|---|---|---|
| 1 | Alistamiento / Servicio del Taladro | DF/CF |
| 2 | Perforación | DF/CF |
| 3 | Maniobras (Viajes) | DF/CF |
| 4 | Tiempo No Productivo | DF/CF |
| 5 | Instalación de BOP | DF |
| 6 | Prueba de BOP | DF |
| 7 | Cementación | DF |
| 8 | Acondicionamiento de Hoyo | DF |
| 9 | Acondicionamiento de Lodo | DF |
| 10 | Toma de Núcleos | DF |
| 11 | Registro Direccional | DF |
| 12 | Trabajo Direccional | DF |
| 13 | Pesca | DF |
| 14 | Pérdida de Circulación | DF |
| 15 | Rimado | DF |
| 16 | Reparación del Taladro | DF |
| 17 | Bajada de Revestimiento | DF |
| 18 | Pruebas | DF |
| 19 | Espera de Fraguado de Cemento | DF |
| 20 | Espera por Clima | DF |

## Relación con otras pestañas

- Las **horas del período** se usan en la pestaña 6 como referencia para el uso de equipos.
- El reporte Excel imprime las **primeras 10 actividades** de la distribución de tiempo.
