# 35 — Integridad en Tanques (Pits), Volumetría y Listas Activas

Verificación de los límites físicos y simetría de respuestas en la configuración de **Tanques y Fosas** (`Pits and Tanks Information`), **Tipos de Fosa** (`Pit Type Setup`), **Dejar Fluido en el Hoyo** (Pestaña 8 - Volumetría) y **Listas Activas del Pozo** (Productos, Equipos y Mallas de Zaranda).

---

## Cómo funciona

1. **Configuración de Tanques / Fosas (`api_fosas_guardar` y `FosaForm`):**
   - **Límites físicos:** La capacidad de cualquier tanque debe ser estrictamente no negativa ($\ge 0$ bbl) y el número de fosa debe ser un entero positivo mayor a cero ($> 0$).
   - Se rechazan valores de capacidad negativos o números nulos/negativos con HTTP 400 y mensaje explicativo.

2. **Tipos de Fosa (`api_tipos_fosa_guardar` y `TipoFosaForm`):**
   - Se prohíbe enviar una lista vacía de tipos de fosa (`tipos_fosa: []`), evitando dejar el pozo sin tipos estándar de tanque.
   - Los códigos deben ser no negativos ($\ge 0$).
   - Respuestas normalizadas simétricamente con `ok: True/False` y `success: True/False`.

3. **Volumetría — Dejar Fluido en el Hoyo (`api_volumetria_dejar_en_hoyo`):**
   - Cuando se registra fluido abandonado o cementado en el hoyo (ej. antes de un side track), si la petición no incluye `perdida_codigo`, el backend asigna automáticamente la categoría de pérdida estándar por defecto `"Detrás del Revestimiento / En el Hoyo"` (`CATEGORIA_PERDIDA_EN_HOYO = 7`).
   - Las respuestas de éxito y error de la API volumétrica (`_respuesta` y `_error`) devuelven de manera consistente `{"ok": bool, "success": bool}`.

4. **Listas Activas del Pozo (Productos, Equipos y Mallas):**
   - En `ProductoActivoPozoForm`, `EquipoActivoPozoForm` y `MallaActivaPozoForm` se validan tarifas, precios unitarios y rentas no negativas ($\ge 0$).
   - En mallas activas se restringe el porcentaje de descuento a valores entre $0\%$ y $100\%$.
   - Respuestas JSON normalizadas con `{"ok": bool, "success": bool}` en `api_productos_activos_guardar`, `api_equipos_activos_guardar` y `api_mallas_activas_guardar`.

---

## Pasos para verificar

### A. Límites Físicos en Tanques y Tipos de Fosa
- [ ] 1. Ingresar a Información del Pozo y abrir la pantalla **Pit Information** (`/pozos/<id>/pits/`).
- [ ] 2. En la grilla de tanques, intentar configurar un tanque con capacidad negativa (ej. `-200` bbl) o con número `0`.
- [ ] 3. Hacer clic en **Guardar Fosas**.
- [ ] 4. Verificar que el sistema rechaza la operación con toast/alerta de error indicando que la capacidad no puede ser negativa y el número debe ser mayor a cero.
- [ ] 5. Ingresar capacidades positivas normales (ej. Tanque 1: 500 bbl, Tanque 2: 400 bbl) y guardar exitosamente.
- [ ] 6. En la sección de Tipos de Fosa, intentar borrar todas las filas y guardar; verificar que se rechaza la solicitud exigiendo al menos un tipo de fosa.

### B. Listas Activas (Productos, Equipos y Mallas)
- [ ] 7. Ir a **Active Items** (`/pozos/<id>/active-items/`).
- [ ] 8. En la pestaña de Productos Activos, intentar fijar un precio unitario negativo (ej. `-15.00`).
- [ ] 9. Guardar y comprobar que el sistema rechaza el guardado con mensaje descriptivo.
- [ ] 10. En la pestaña de Equipos Activos, ingresar precio de renta negativo y verificar rechazo.
- [ ] 11. En la pestaña de Mallas Activas, intentar ingresar un descuento de `150%` o precio negativo; verificar que es rechazado.

### C. Dejar Fluido en el Hoyo (Pestaña 8)
- [ ] 12. Abrir un reporte diario activo y entrar a la pestaña **8- Volumetría / Inventario**.
- [ ] 13. Abrir la opción de dejar fluido en el hoyo (tapón/abandono) indicando volumen y tanque activo origen, omitiendo la selección explícita del tipo de pérdida.
- [ ] 14. Guardar y verificar que el movimiento se registra automáticamente bajo la categoría 7 (*"Detrás del Revestimiento / En el Hoyo"*), reflejándose tanto en el volumen no ocupado por fluido del hoyo como en la pérdida del sistema activo.

