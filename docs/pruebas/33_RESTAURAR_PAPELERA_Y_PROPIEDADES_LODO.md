# 33 — Restauración de Papelera, Cierre de Pozos e Integridad de Propiedades de Lodo

Verificación del blindaje en el ciclo de vida del pozo (restauración y cierre) y validación de límites físicos con atomicidad en Propiedades de Lodo (Pestaña 3).

---

## Cómo funciona

1. **Restaurar pozo desde la papelera (`api_pozo_restaurar`):**
   - Antes de limpiar `eliminado_en` y `eliminado_por`, la API verifica si ya existe un pozo activo o cerrado con el mismo nombre (`nombre__iexact=pozo.nombre`).
   - Si colisiona, responde con HTTP 400 y mensaje amigable en español, evitando excepciones no controladas `IntegrityError` (500) en la base de datos SQLite.

2. **Cierre de pozos (`api_pozo_cerrar`):**
   - Solo se permite cerrar pozos cuyo estado sea exactamente `ACTIVO`.
   - Si se intenta cerrar un pozo en `BORRADOR` (asistente de creación incompleto), la API rechaza la solicitud con HTTP 400 y mensaje explicativo.

3. **Propiedades de Lodo (`api_mud_properties_guardar`):**
   - **Validación preventiva en memoria:** Se revisan los valores antes de tocar la base de datos:
     - Densidades, viscosidades, lecturas reológicas ($R_{600}\dots R_{3}$), geles y filtrados $\ge 0$.
     - Porcentajes de retorta ($0.0\%$ a $100.0\%$).
     - Rango de $pH$ ($0.0$ a $14.0$).
     - Gravedades específicas de la configuración $> 0$.
   - **Transaccionalidad atómica:** El guardado de configuración, chequeos 1 a 4 y propiedades extra se ejecuta dentro de `with transaction.atomic():`. Si un valor falla en el chequeo 2, los cambios del chequeo 1 se revierten automáticamente (rollback).

---

## Pasos para verificar

### A. Intento de cierre de pozo en Borrador
- [ ] 1. Iniciar la creación de un nuevo pozo en `/pozos/crear/paso1/` y guardar solo el paso 1 (dejarlo en estado `BORRADOR`).
- [ ] 2. Intentar llamar al cierre de pozo mediante POST a `/api/pozos/<pk>/cerrar/`.
- [ ] 3. Comprobar que devuelve código 400 y el mensaje *"Solo se pueden cerrar pozos que se encuentren en estado ACTIVO."*.
- [ ] 4. Verificar en base de datos o en la lista que el pozo se mantiene en estado `BORRADOR`.

### B. Restauración de pozo con colisión de nombre
- [ ] 5. Enviar un pozo a la papelera (por ejemplo `POZO COLISION`).
- [ ] 6. Si en la base de datos existiera otro pozo activo con el mismo nombre, intentar restaurar desde `/pozos/papelera/`.
- [ ] 7. Verificar que el sistema muestra el error descriptivo en pantalla sin caerse ni generar error 500.

### C. Validación física en Propiedades de Lodo (Pestaña 3)
- [ ] 8. Abrir el Reporte Diario de un po activo y entrar a la pestaña **3- Mud Properties**.
- [ ] 9. Intentar ingresar una densidad negativa (ej. `-10.5` ppg) o una lectura $R_{600}$ negativa (ej. `-20`).
- [ ] 10. Al hacer clic en Guardar, verificar que aparece el toast de advertencia indicando que el valor no puede ser negativo y no se guardan datos corruptos.
- [ ] 11. Intentar ingresar un porcentaje de sólidos superior al 100% (ej. `120%`) o un $pH$ fuera de rango (ej. `16`).
- [ ] 12. Verificar que se rechaza indicando el rango correcto ($0-100\%$ o $0-14$).
- [ ] 13. Ingresar valores físicos reales (densidad 10.5 ppg, embudo 45 s, $R_{600}=50, R_{300}=30, pH=9.5$) y guardar.
- [ ] 14. Verificar toast exitoso verde y confirmación de cálculo automático de PV (`20.0`) e YP (`10.0`).

