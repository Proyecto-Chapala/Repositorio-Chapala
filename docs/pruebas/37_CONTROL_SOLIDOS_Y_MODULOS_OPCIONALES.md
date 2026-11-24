# 37 — Integridad en Control de Sólidos, Módulos Opcionales y Pérdidas del Reporte

Verificación de límites físicos en **Retención en Recortes** y **Análisis de Sólidos de Retorta por Equipo**, consistencia en **Eventos No Programados**, protección contra listas vacías en **Pérdidas del Reporte**, y simetría total de respuestas (`ok: True/False` y `success: True/False`) en la Pestaña 6 (Control de Sólidos) y Módulos Opcionales.

---

## Cómo funciona

1. **Límites Físicos en Retención de Recortes (`api_muestras_guardar`):**
   - **Consistencia de masas:**
     - La masa húmeda no puede ser negativa: $celda\_humedo \ge celda\_vacia$.
     - La masa seca no puede ser negativa: $celda\_seco \ge celda\_vacia$.
     - Al secar una muestra en la celda, el solvente/líquido se evapora, por lo que la masa seca no puede ser superior a la masa húmeda: $celda\_seco \le celda\_humedo$.
     - En la probeta graduada: la masa total del destilado no puede ser inferior a la probeta vacía más el agua recolectada: $probeta\_total \ge probeta\_vacia + agua\_cc$.
   - **Gravedades específicas y porcentajes:**
     - Las gravedades específicas de fluido base y sólidos deben ser estrictamente positivas ($sg\_fluido\_base > 0$, $sg\_solidos > 0$), evitando divisiones por cero.
     - El porcentaje de fluido base debe situarse entre $0\%$ y $100\%$, y el peso de lodo debe ser $> 0$.

2. **Límites Físicos en Análisis de Sólidos por Equipo (`solidos`):**
   - Los porcentajes de retorta ($water\_pct$, $oil\_pct$, $solids\_pct$) deben estar en el rango físico $[0, 100]\%$.
   - Las gravedades específicas ($drill\_solids\_sg$, $wt\_additive\_sg$, $oil\_sg$) y peso de lodo deben ser $> 0$.

3. **Eventos No Programados (`api_eventos_guardar`):**
   - Se exige que `tipo_problema` no esté vacío.
   - Las horas perdidas, el volumen perdido y el costo deben ser valores estrictamente no negativos ($\ge 0$).

4. **Pérdidas del Reporte (`api_perdidas_reporte_guardar`):**
   - Se prohíbe vaciar la lista de pérdidas asignadas al reporte diario (`codigos: []`), protegiendo la cuadrícula de distribución de pérdidas de la Pestaña 8.

5. **Simetría y Normalización de Respuestas (`ok` y `success`):**
   - Todas las respuestas JSON devuelven de forma uniforme `ok` y `success` tanto en éxito como en fallo:
     - Control de Sólidos (Pestaña 6): `api_control_solidos_detail`, `api_transaccion_malla_*`, `api_ticket_malla_*`, `api_tipo_ticket_malla_*`, `api_uso_equipos_*`.
     - Módulos Opcionales: `api_ife`, `api_muestras_*`, `api_eventos_*`, `api_benchmark_evaluacion`.
     - Inventario: `api_perdidas_reporte_detail` y `api_perdidas_reporte_guardar`.

---

## Pasos para verificar

### A. Límites Físicos en Retención de Recortes (Módulos Opcionales)
- [ ] 1. Abrir un reporte diario activo y desplegar el módulo opcional **Retención en Recortes**.
- [ ] 2. Crear una nueva muestra seleccionando una zaranda activa.
- [ ] 3. Ingresar celda vacía = `50` g y celda + húmedo = `40` g ($celda\_humedo < celda\_vacia$). Intentar guardar.
- [ ] 4. Verificar que el sistema rechaza el guardado indicando que el peso de celda + húmedo no puede ser menor que la celda vacía.
- [ ] 5. Ingresar celda + húmedo = `100` g y celda + seco = `105` g ($celda\_seco > celda\_humedo$). Intentar guardar.
- [ ] 6. Verificar que el sistema rechaza indicando que el peso de celda + seco no puede ser mayor que celda + húmedo.
- [ ] 7. Ingresar valores válidos coherentes (celda vacía = `50` g, húmedo = `100` g, seco = `90` g, probeta vacía = `30` g, agua = `5` cc, probeta total = `42` g, sg fluido = `0.84`, sg sólidos = `2.6`, % fluido base = `15.0`) y verificar que se guarda exitosamente con cálculo de factor de balance.

### B. Análisis de Sólidos y Eventos No Programados
- [ ] 8. En el módulo **Análisis de Sólidos**, ingresar agua = `110%` y verificar rechazo por porcentaje fuera de rango.
- [ ] 9. En el módulo **Eventos No Programados**, intentar registrar un evento con tipo de problema vacío o con horas perdidas negativas; verificar que es rechazado con mensaje explicativo.
- [ ] 10. Ingresar datos válidos de evento (tipo de problema: *"Pérdida de circulación"*, horas: `4.5`, volumen: `40` bbl, costo: `$2,500`) y verificar guardado exitoso.

### C. Normalización y Pérdidas del Reporte
- [ ] 11. En la Pestaña 8 (Inventario / Volumetría), abrir el configurador de pérdidas del reporte e intentar desmarcar todas las categorías para guardar una lista vacía.
- [ ] 12. Verificar rechazo con mensaje indicando que debe elegirse al menos una categoría para el reporte.
- [ ] 13. Abrir la consola de red del navegador y comprobar que todas las respuestas de la Pestaña 6 y de los módulos opcionales contienen `"ok": true` y `"success": true` simultáneamente.

