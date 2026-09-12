# Módulo 4: Reporte Diario y Propiedades de Fluido (General, Pumps/Bits & Fluid Checks)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information

## 1. Ciclo de Vida del Día Operativo (Starting a New Day & General Tab)
Gestiona la creación del reporte diario y la contabilidad del tiempo en locación[cite: 2].

*   **Creación del Primer Día (Hard Locks):**
    *   Almacena la fecha inicial, el `Default Interval` y el `Default Fluid System`[cite: 2].
    *   **Evento Irreversible:** Una vez creado el primer día, las variables globales `Is Offshore?` y `Unit Set` quedan bloqueadas de por vida en la base de datos[cite: 2].
*   **Creación de Días Subsecuentes:**
    *   Soportado por la función `Copy Data From Prior Day?`, que clona el estado de los equipos y fluidos del día anterior[cite: 2].
*   **Distribución del Tiempo (`Time Distribution`):**
    *   **Validación Estricta:** La sumatoria de horas de las actividades del taladro debe ser exactamente 24 horas[cite: 2]. 
    *   Si es $< 24$, el texto indicativo permanece en color rojo; si es $> 24$, el sistema arroja una alerta bloqueante (`Warning: The total hours entered... is greater than 24`)[cite: 2].
*   **Gestión del Intervalo Activo (`Default Interval`):**
    *   Cambiar el intervalo en la pestaña `General` a mitad de jornada **no altera** el intervalo de las transacciones ya guardadas ese día, sino que asigna el nuevo intervalo exclusivamente a las transacciones creadas a partir de ese momento[cite: 2].

## 2. Hidráulica y Parámetros de Perforación (Pumps/Bits Tab)
Alimenta el motor de cálculo de presiones y limpieza del hoyo[cite: 2].

*   **Inputs Críticos del Sistema:**
    *   `Pump Data`: Incluye eficiencia (`Eff%`), diámetro de camisa (`Liner Diameter`) y longitud de carrera (`Stroke Length`) para determinar la tasa de bombeo[cite: 2].
    *   `Bit Information`: El Área Total de Flujo (`TFA`) se autocalcula ingresando la cantidad y tamaño fraccional de las boquillas (ej. $12/32''$)[cite: 2].
    *   `Temperatures`: `Bottomhole Circulating Temp` y `Surface Temp` son obligatorias para la corrección reológica y el cálculo de pérdida de presión anular según API 5ta Edición[cite: 2].
*   **Motor de Resultados (`Hydraulics Result`):**
    *   Genera la tabla matemática por secciones del pozo evaluando el Número de Reynolds (`AnnRe`)[cite: 2]. Si `AnnRe > 2000`, el flujo se cataloga como turbulento[cite: 2].
    *   Calcula la velocidad crítica anular (`AnnVCritical`)[cite: 2].

## 3. Matriz de Propiedades del Fluido (Fluid Checks Tab)
El núcleo de la física y química del lodo para el balance de sólidos[cite: 2].

*   **Tipología del Chequeo (`Fluid Type`):**
    *   Varía los campos de entrada según el fluido base: `Make Up Water` para lodos base agua (WBM); `Internal Phase Salt` para OBM/SBM; `Base Fluid` para salmueras[cite: 2].
*   **El Concepto de `Primary Check`:**
    *   Un día puede tener múltiples chequeos (hasta 4 por pestaña), pero **solo uno puede marcarse como `Make Primary`**[cite: 2]. 
    *   El chequeo primario es el único que se utiliza para calcular la hidráulica del pozo y para exportar telemetría en formatos `WITSML` y `OpenWells`[cite: 2].
*   **Calculadora de Retorta y Sólidos (`Solids Analysis Page`):**
    *   Interrelaciona los volúmenes de Agua, Aceite y Sólidos (%)[cite: 2].
    *   Requiere que el usuario ingrese la concentración de aditivos químicos solubles (`Chem Conc`) para excluirlos y no sobredimensionar la masa de sólidos perforados (`Drill Solids`)[cite: 2].
    *   **Validación UI:** Si las fórmulas despejan concentraciones negativas de sólidos de baja gravedad (LGS), la celda infractora se encierra en un borde rojo indicando un error en el balance de masa ingresado[cite: 2].
*   **Propiedades Extendidas (`Extra Fluid Properties`):**
    *   Existen 10 variables libres (`Custom Property 1-10`) donde el ingeniero puede definir descripciones personalizadas[cite: 2].
    *   **Regla de Negocio (Integridad de Reportes Antiguos):** El manual prohíbe eliminar propiedades extendidas que ya no se usen, ya que corrompería los reportes impresos de días anteriores. En su lugar, el sistema exige cambiar el valor de la columna `Print Order` a `0` para ocultarlas[cite: 2].
*   **Especificaciones Diarias (`Daily Property Specifications`):**
    *   Fija las tolerancias operativas (`Min Value` / `Max Value`) para cualquier variable (ej. `Fluid Weight`, `PV`, `YP`)[cite: 2]. Cualquier valor que se salga de este umbral en la matriz de chequeo activará alertas visuales en rojo[cite: 2].