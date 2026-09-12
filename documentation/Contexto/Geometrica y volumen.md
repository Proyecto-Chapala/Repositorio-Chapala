# Módulo 5: Configuración Geométrica y Contabilidad de Volumen (Geometry & Volume Accounting)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information

## 1. Modelo Geométrico y Capacidades del Hoyo (Geometry Tab)
Define la arquitectura del pozo y la sarta de perforación para calcular los volúmenes del sistema activo[cite: 2].

*   **Wellbore Geometry (Geometría del Hoyo):**
    *   `Type`: Clasifica la sección en `Casing`, `Liner` u `Open Hole`[cite: 2].
    *   `Hole Size` (Calculado): Se determina automáticamente a partir del tamaño de la mecha (`Bit Size`) y el porcentaje de ensanchamiento (`% Washout`) ingresado en la sección de información[cite: 2]. Si el Washout es `0`, asume un hoyo en calibre (*gauge hole*)[cite: 2].
*   **Drill String Geometry (Sarta de Perforación):**
    *   **Cálculo Inverso de Longitud:** La longitud del primer componente de la sarta (ej. Drill Pipe) se autocalcula tomando la profundidad actual de la mecha (`Bit Depth`) menos la suma de las longitudes de los demás componentes inferiores (BHA)[cite: 2].
    *   *Caso Borde:* Si la mecha está en superficie (Profundidad = 0), esta longitud arrojará un valor negativo lógico[cite: 2].
*   **Parámetros Offshore y Riser:**
    *   Si el pozo es marino, habilita el checkbox `Riserless Drilling?`[cite: 2].
    *   Al desmarcarlo, el sistema exige ingresar `Riser OD`, `Riser ID` y `Riser Length` (obtenido al restar el `Water Depth` y el `Air Gap`), sumando este volumen crítico al cálculo hidrostático[cite: 2].

## 2. Motor de Contabilidad de Volumen (Volume Accounting Tab)
Es el "libro mayor" del sistema de lodos. Su regla de oro es que el balance volumétrico diario debe cuadrar a cero[cite: 2].

*   **Arquitectura de la Interfaz (6 Bloques):**
    1.  **Pit Section:** Muestra el volumen inicial (`Start Volume`), peso del lodo (`Fluid Weight`) y calcula el volumen final teórico (`Calc End Volume`)[cite: 2]. Exige la medición manual del ingeniero (`End Volume`)[cite: 2].
    2.  **Fluids in Hole Section:** Segmenta el volumen alojado en el anular (`Annulus`), dentro de la sarta (`Total DS`) y debajo de la mecha (`Below`)[cite: 2]. Resta cualquier volumen catalogado como `Volume Not Fluids` (ej. agua de mar temporal o aire)[cite: 2].
    3.  **Total Loss Breakdown Section:** Consolidado de todas las pérdidas mecánicas, de superficie y subsuelo[cite: 2].
    4.  **Fluid Volume Section (El Cuadre):** Compara el `Calc Value` contra el `Actual Values`[cite: 2]. La diferencia arroja la columna `Not Accounted`[cite: 2]. **Regla estricta:** Esta celda debe ser `0.00`; de lo contrario, exige asentar una transacción para justificar el desfase[cite: 2].
    5.  **Non-Transactional Pits:** Tanques ciegos (almacenaje pasivo) que no se ven afectados por las matemáticas transaccionales hasta que su fluido se trasvase al sistema activo[cite: 2].
    6.  **Fluids Balance Section:** Resumen contable de entradas (`Water Added`, `Transferred In`, `Received`) y salidas (`Transferred Out`, `Back Load`, `Loss and Dumped`)[cite: 2].

## 3. Transacciones Volumétricas (Transaction Buttons)
Lógica de los movimientos de masa en la base de datos[cite: 2].

*   **Add Chemicals:** Suma masa y volumen al pozo desde el inventario. Incorpora el checkbox `Is Dilution` para que la base de datos etiquete el movimiento como una táctica de reducción de sólidos de baja gravedad (LGS), impactando los reportes analíticos[cite: 2].
*   **Add Whole Mud:** Ingresa lodo formulado a granel. 
    *   Cuenta con la validación `Add Without Charge` para saltarse la facturación si el lodo pertenece a la operadora[cite: 2]. 
    *   Asimila la concentración química entrante para recalcular el promedio ponderado del tanque destino sin descontar sacos de la bodega física[cite: 2].
*   **Transfer:** Trasvase de fluidos.
    *   El checkbox `All Volume` jala matemáticamente el `Calc End Volume` exacto de la fosa origen para vaciarla a cero, previniendo la retención de residuos decimales fantasmas[cite: 2].
*   **Return (Back Load):** Despacha lodo fuera del taladro. 
    *   Se refleja en la fila `Back Load` del balance general[cite: 2]. 
    *   **Aislamiento Financiero:** Esta acción vacía el tanque físico pero **no emite crédito monetario automático**. Cualquier nota de crédito debe conciliarse manualmente usando la columna `Used Other` en el inventario[cite: 2].
*   **Create Equipment Loss Transaction:** Función puente que importa el lodo neto descartado con los ripios calculados matemáticamente desde la pestaña `Equipment` (ej. Shakers, Centrífugas) para generar una salida automatizada del sistema activo[cite: 2].

## 4. Gestión de Desplazamientos (Displacements Tab)
Módulo para maniobras de cambio de fluido (ej. lodo a salmuera)[cite: 2].

*   **Estructura de Componentes (Tren de Baches):**
    *   El usuario declara componentes separados (espaciadores, píldoras viscosas)[cite: 2].
    *   **Precondición:** Cada componente debe haberse mezclado primero en un tanque válido usando la herramienta transaccional de `Volume Accounting`[cite: 2].
    *   Controla la disposición final del fluido retornado a superficie: si se marca `Reclaimed`, exige declarar a qué tanque específico (`Reclaimed to Pit`) va a retornar el volumen[cite: 2].