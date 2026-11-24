# 36 — Integridad en Catálogos Maestros, Configuración de Pérdidas y Componentes de Sarta

Verificación de la validación geométrica de juntas de componentes de sarta, protección contra listas vacías en la configuración de pérdidas (`Loss Setup`), código positivo en categorías y simetría de respuestas (`ok: True/False` y `success: True/False`) en los endpoints de Catálogos Maestros y Configuración del Pozo.

---

## Cómo funciona

1. **Geometría de Componentes de Sarta (`_validar_componente_sarta`):**
   - **Límites de conexión (Tool Joint):** Al igual que para el cuerpo del componente ($ID < OD$), para la junta de conexión se exige de manera estricta que su diámetro interno sea menor que su diámetro externo ($ID_{tj} < OD_{tj}$) cuando ambos están presentes y $OD_{tj} > 0$.
   - Si se intenta ingresar $ID_{tj} \ge OD_{tj}$, el backend rechaza la creación/edición con HTTP 400 y el error específico en el campo `tool_joint_id_in`.

2. **Configuración de Pérdidas (`api_categorias_perdida_guardar` y `CategoriaPerdidaItemForm`):**
   - **Protección contra lista vacía:** Se prohíbe enviar un arreglo vacío `categorias: []`, evitando que un usuario o un error de JavaScript borre todas las categorías de pérdida del pozo, lo cual rompería el registro volumétrico en la Pestaña 8 del reporte diario.
   - **Validación de código:** El código de la categoría debe ser estrictamente positivo ($> 0$), validado en `CategoriaPerdidaItemForm.clean_codigo`.

3. **Simetría y Normalización de Respuestas (`ok` y `success`):**
   - Los endpoints de configuración del pozo y catálogos maestros devuelven de forma simétrica tanto `"ok"` como `"success"`, previniendo inconsistencias en clientes frontend basados en `res.ok` o `res.success`:
     - `api_marketing_codes_guardar` (Pestaña 2 del pozo).
     - `api_categorias_perdida_guardar` (Loss Setup).
     - `api_equipment_properties_guardar` (Equipment Properties Setup).
     - `api_benchmark_definiciones_guardar` y `api_benchmark_targets_guardar` (Benchmark Setup).
     - `api_equipo_create`, `api_equipo_update`, `api_equipo_delete` (Catálogo Maestro de Equipos).
     - `api_malla_create`, `api_malla_update`, `api_malla_delete` (Catálogo Maestro de Mallas).
     - `api_propiedades_equipo_list`, `api_propiedad_equipo_create`, `api_propiedad_equipo_update`, `api_propiedad_equipo_delete` (Propiedades por Tipo de Equipo).
     - `api_parametros_benchmark_list`, `api_parametro_benchmark_create`, `api_parametro_benchmark_update`, `api_parametro_benchmark_delete` (Parámetros de Benchmark).
     - `api_componentes_sarta_list`, `api_componente_sarta_create`, `api_componente_sarta_update`, `api_componente_sarta_delete` (Componentes de Sarta).

---

## Pasos para verificar

### A. Geometría de Juntas en Componentes de Sarta
- [ ] 1. Ingresar a **Catálogos Maestros** (`/catalogos-maestros/`) y seleccionar la sección de **Componentes de Sarta** o abrir el modal de nuevo componente.
- [ ] 2. Crear un componente de tipo tubería de perforación (*Drill Pipe*) ingresando $OD = 5.000$ in, $ID = 4.276$ in.
- [ ] 3. En la geometría de junta de herramienta (*Tool Joint*), ingresar $OD_{tj} = 6.500$ in e intentar colocar $ID_{tj} = 6.625$ in o $6.500$ in ($ID_{tj} \ge OD_{tj}$).
- [ ] 4. Hacer clic en **Guardar**.
- [ ] 5. Comprobar que el sistema rechaza el guardado con un mensaje de validación indicando: *"El diámetro interno de la junta debe ser menor que su diámetro externo."*
- [ ] 6. Corregir $ID_{tj}$ a $3.250$ in y guardar exitosamente.

### B. Configuración de Pérdidas (Loss Setup)
- [ ] 7. Ingresar a la pantalla de configuración **Loss Setup** (`/pozos/<id>/loss-setup/`).
- [ ] 8. Intentar eliminar todas las filas de categorías y pulsar **Guardar**.
- [ ] 9. Verificar que el sistema rechaza la petición indicando que debe especificarse al menos una categoría de pérdida.
- [ ] 10. Intentar ingresar una fila con código `0` o `-1`; verificar que el formulario la rechaza indicando que el código debe ser un entero positivo mayor a cero.

### C. Normalización y Catálogos Maestros
- [ ] 11. En `/catalogos-maestros/`, crear y editar un Equipo, una Malla, una Propiedad de Equipo y un Parámetro de Benchmark.
- [ ] 12. Verificar en la consola de red del navegador que cada respuesta HTTP 200/201 devuelve tanto `"success": true` como `"ok": true`.
- [ ] 13. Intentar enviar campos vacíos o duplicados en cada catálogo y verificar que el error devuelve `"success": false` y `"ok": false`.

