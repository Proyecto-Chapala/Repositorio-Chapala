# 34 — Integridad de Geometría de Sarta y Propiedades Extra

Verificación de la consistencia física y transaccionalidad atómica en la Pestaña 4 (**Well Geometry / Geometría del Pozo**) y en la configuración de **Propiedades Extra de Fluidos**.

---

## Cómo funciona

1. **Geometría del Pozo y Tramos de Sarta (`api_well_geometry_guardar`):**
   - **Límites físicos:** Longitudes de tramo, diámetros externos ($OD$), diámetros internos ($ID$), juntas ($OD_{tj}$, $ID_{tj}$, longitud) y dimensiones de hoyo piloto no pueden ser negativos ($\ge 0$).
   - **Consistencia geométrica de tubería:** En cualquier componente tubular con espesor de pared, el diámetro interno no puede igualar ni superar al diámetro externo ($ID < OD$, e $ID_{tj} < OD_{tj}$). Esto previene desplazamientos de acero nulos o negativos en los cálculos de capacidad y volumen anular de [`geometria_pozo.py`](../../operaciones/geometria_pozo.py).
   - **Transaccionalidad atómica indivisible:** La actualización de campos del reporte diario (intervalo de costo, hoyo piloto y desvío de side track) y la sustitución completa de tramos de sarta (`TramoSarta.objects.bulk_create`) se ejecutan dentro de `with transaction.atomic():`. Si cualquier tramo falla la validación o ocurre una desconexión, ningún campo del reporte es alterado en base de datos.

2. **Propiedades Extra de Fluidos (`api_propiedades_extra_guardar`):**
   - Validación previa en memoria de los ítems recibidos (número de propiedad entero positivo $\ge 1$).
   - Toda la matriz de actualización, creación y eliminación de registros en `PropiedadExtraFluido` corre dentro de una transacción atómica protegida.

3. **Estandarización de Respuestas:**
   - Tanto `api_well_geometry_guardar`, `api_propiedades_extra_guardar`, `api_comentarios_guardar` como `api_reporte_propiedades_comentario` responden de forma simétrica con `ok: True/False` y `success: True/False`.

---

## Pasos para verificar

### A. Validación física en Geometría del Pozo (Pestaña 4)
- [ ] 1. Ingresar a un reporte diario activo y dirigirse a la pestaña **4- Well Geometry**.
- [ ] 2. En la tabla de sarta de perforación (*Drill String*), agregar una fila e intentar ingresar un diámetro interior mayor que el exterior (ej. $OD = 4.5"$, $ID = 5.0"$).
- [ ] 3. Hacer clic en **Guardar Geometría**.
- [ ] 4. Verificar que el sistema muestra un toast de error indicando que el diámetro interior debe ser menor que el exterior, y la sarta no se corrompe.
- [ ] 5. Intentar ingresar una longitud negativa (ej. `-500` ft).
- [ ] 6. Verificar que la API rechaza la solicitud indicando que la longitud no puede ser negativa.
- [ ] 7. Ingresar datos reales coherentes (ej. Drill Pipe 5", longitud 3000 ft, OD 5.0", ID 4.276", TJ OD 6.5", TJ ID 3.75").
- [ ] 8. Guardar y verificar toast verde exitoso y cálculo inmediato de volúmenes de sarta y espacio anular.

### B. Transaccionalidad Atómica y Rollback
- [ ] 9. En un reporte con hoyo piloto existente (ej. 8.5"), intentar cambiar el tamaño a 12.25" mientras se introduce una sarta con error geométrico.
- [ ] 10. Comprobar que tras el error 400, el tamaño de hoyo piloto no se modificó parcialmente en base de datos.

### C. Propiedades Extra de Fluidos
- [ ] 11. En Información del Pozo o modal de Propiedades Extra, configurar una propiedad personalizada para lodo base agua (ej. *"Salinidad KCl"*, unidad *"mg/L"*).
- [ ] 12. Guardar y verificar que se persiste correctamente en base de datos.
- [ ] 13. Limpiar la etiqueta y unidad de la propiedad y guardar; verificar que se elimina de la base de datos de manera limpia sin dejar registros vacíos.

