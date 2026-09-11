# Módulo Extra: Casos Borde, Excepciones y Reglas Ocultas (Extra Context)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / Edge Cases & System Quirks

Este documento recopila reglas de negocio condicionales, comportamientos específicos de la interfaz de usuario (UI) y excepciones contables que no pertenecen a un solo módulo, pero que son críticas para la estabilidad del sistema[cite: 1].

## 1. Convenciones de Interfaz de Usuario (UI/UX)
El frontend debe respetar un código de colores estricto para guiar al usuario y bloquear errores de integridad de datos.
*   **Celdas con Borde Rojo:** Indican un campo de entrada obligatorio vacío o una celda con datos erróneos (ej. valores fuera de los parámetros definidos en `Daily Properties Specifications` o resultados negativos inválidos).
*   **Celdas con Fondo Amarillo:** Son campos de estricta lectura (Display Only). Contienen datos calculados por el sistema y nunca deben aceptar entrada manual desde el teclado.

## 2. Excepciones en la Contabilidad de Volumen (`Volume Accounting`)
*   **Ocultamiento del Volumen Calculado:** En la sección `Pit Section`, el campo `Calc End Volume` (Volumen Final Calculado) **no se muestra** para ninguna fosa que tenga asignado el tipo `Active`[cite: 1].
*   **Prevención de Volúmenes Fantasma (El Checkbox `All Volume`):** En los modales de `Transfer` y `Return`, si el usuario marca la casilla `All Volume`, el sistema debe capturar el volumen calculado exacto de la base de datos para vaciar el tanque a $0.00$ y evitar que queden residuos decimales microscópicos (ej. $0.0001\text{ bbl}$)[cite: 1].
*   **El Factor `Volume Not Fluids`:** Si durante un desplazamiento hay agua de mar o aire en el anular, este volumen debe ingresarse obligatoriamente en `Volume Not Fluids`[cite: 1]. Si no se resta del `Total Hole Volume`, el sistema asumirá erróneamente que esos barriles son de lodo activo y desajustará el cuadre contable (`Not Accounted` será distinto de cero)[cite: 1].

## 3. Disociación Financiera vs. Operativa
*   **El Quirk de la Filtración (`Filtration`):** Existe una separación estricta en el manejo de los equipos de filtración[cite: 1]. Los cargos monetarios (facturación de tarifa plena o stand-by) se ingresan única y exclusivamente en la tabla `Equipment Utilization` de la pestaña `Equipment`[cite: 1]. Sin embargo, los datos técnicos de uso (NTU, horas, ciclos) van obligatoriamente en la pestaña `Filtration`[cite: 1].
*   **El Quirk del Back Load (`Return`):** Despachar lodo de regreso a la base mediante un `Return` saca el volumen físico de los tanques, pero **no genera una transacción contable automática (nota de crédito)**[cite: 1]. Para que el costo se ajuste financieramente a favor del cliente, el ingeniero debe asentar el crédito manualmente usando la columna `Used Other` en la pestaña de Inventario[cite: 1].

## 4. Bloqueos de Base de Datos y Hard Stops
*   **Variables Globales Inmutables:** Los campos `Is Offshore?` y `Unit Set` quedan bloqueados permanentemente una vez que se crea el primer reporte diario del proyecto.
*   **Restricción de Borrado de Intervalos:** El `Interval "0"` no puede ser eliminado bajo ninguna circunstancia. Además, ningún intervalo puede ser borrado si ya tiene días o costos asociados.
*   **Restricción de Borrado de Fosas:** Una fosa (`Pit`) no puede ser eliminada del catálogo si ya ha sido utilizada en la tabla diaria (`The Record Is In Use By Table [DayPit]`).
*   **Validación Intranet (LDAP):** El botón `Validate SLB User Names` requiere obligatoriamente una conexión a la intranet corporativa (Schlumberger) para verificar la existencia del ID; de lo contrario, fallará la validación para el cierre del proyecto.

## 5. Excepciones en Catálogos y Requisitos de Reporte
*   **Regla Oculta de Plan Data:** La importación de la data de planificación (`Plan Data Tab`) se vuelve **obligatoria** para el cierre del proyecto bajo dos condiciones precisas: si el proyecto duró 15 días o más, o si el proyecto se factura en dólares estadounidenses (USD) y el costo superó los $150,000.00.
*   **Filtro Químico (`Show Conc?`):** Un producto del inventario solo aparecerá en la tabla analítica de `Product Concentrations` si su configuración original en el `Product Setup Tab` tenía la casilla `Show Conc?` marcada[cite: 1].
*   **Lógica de Reutilización de Mallas (`Screens`):** Si un usuario intenta "reutilizar" (`Reuse`) una malla que fue registrada pero *nunca instalada* (`Undo Installation`), el sistema forzará el cambio de su estado en el inventario a `Used`, independientemente de si era nueva al principio.