# Módulo 6: Logística, Inventario y Equipos Diarios (Material Transfers, Inventory, Screens, Equipment & Filtration)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information

## 1. Control de Inventario (Inventory Tab)
Gestiona la contabilidad física de los productos en la locación, separando el consumo volumétrico del consumo logístico[cite: 2].

*   **Variables Editables de Ajuste:**
    *   `Used Other`: Registra la cantidad de producto que se consumió físicamente pero que **no se inyectó al fluido** a través de una transacción volumétrica[cite: 2]. Se utiliza para facturar empaques termocontraíbles, paletas, sacos dañados o productos de limpieza (`Clean-Up`)[cite: 2].
    *   `On Order`: Campo estrictamente informativo para mostrar en el reporte la cantidad de material pedido que aún no ha llegado al taladro[cite: 2]. No afecta el inventario final[cite: 2].
    *   `Exclude from Print`: Checkbox que omite el producto de todos los reportes generados[cite: 2].
*   **Variable Calculada de Carga (`Chemical Weight`):**
    *   Campo de solo lectura que calcula el peso total de todos los productos químicos presentes actualmente en la locación basándose en la cantidad en mano[cite: 2].

## 2. Trazabilidad de Tickets (Material & Screen Transfer Tickets)
Módulo de ingresos y egresos físicos hacia y desde el taladro[cite: 2].

*   **Tipología de Transacción:**
    *   Soporta cuatro rutas logísticas: `Receive from Warehouse`, `Receive from Other Well`, `Return to Warehouse` y `Return to Other Well`[cite: 2].
*   **Ticket Browser (Filtros de Búsqueda):**
    *   Permite auditar el historial completo de tickets[cite: 2]. 
    *   **Regla de Búsqueda:** El filtro por ítem exige usar coincidencias parciales sin espacios finales (ej. escribir `poly` en lugar de `poly-plus` o `poly `) para evitar resultados nulos en la base de datos[cite: 2].

## 3. Ciclo de Vida de las Mallas (Screens Tab)
Controla la instalación, desgaste y facturación de los tamices de las zarandas y mud cleaners[cite: 2].

*   **Instalación (`Installed Screens Table`):**
    *   Vincula un modelo de malla específico a un equipo activo[cite: 2]. No se define la posición exacta de la malla dentro del equipo[cite: 2].
*   **Remoción y Disposición (Estados de Inventario):**
    *   `Disposed`: La malla se desinstala y se elimina definitivamente del inventario[cite: 2].
    *   `Reused`: La malla se desinstala pero retorna al inventario bajo el estatus de malla usada (`Used`)[cite: 2].
    *   `Undo`: Revierte una instalación errónea, devolviendo la malla a su estado original de inventario (nueva o usada) como si nunca se hubiera instalado[cite: 2].

## 4. Rendimiento y Facturación de Equipos (Equipment Tab)
Calcula el balance de masa de los sólidos separados y maneja los cobros diarios[cite: 2].

*   **Propiedades de Balance de Masa (Cálculos Críticos):**
    *   `Mud On Cuttings`: Relación volumétrica ingresada por el usuario[cite: 2]. Si el valor es `1`, la descarga es 50% lodo y 50% ripios[cite: 2]. Si es `0.8`, significa que por cada 0.8 barriles de lodo hay 1 barril de ripios (44% lodo y 56% sólidos)[cite: 2].
    *   `% of Cuttings Removed by this Equipment` (Shakers): Exige dividir la eficiencia estimada. Si 3 shakers remueven el 90% de los ripios, cada uno debe registrar un 30%[cite: 2].
*   **Modelos de Equipo Específicos:**
    *   **Centrífugas:** Calcula 31 propiedades, incluyendo tasas de flujo, velocidades del tazón (`Bowl Speed`) y volumen de lodo botado en los sólidos[cite: 2].
    *   **Mud Cleaner:** Mide presión, tamaño de cono (`Cone Size`) y cantidad de conos operando (`Cones Used`)[cite: 2].
    *   **Verti-G:** Calcula el `Volume Recovered` (volumen de lodo recuperado) y monitorea el torque del tornillo sinfín (`Feed Auger Torque`)[cite: 2].
*   **Reglas de Facturación (`Equipment Utilization Table`):**
    *   Aplica cargos operativos mediante el campo `Charge` (`Full Charge`, `Stand-By` o `No Charge`)[cite: 2].
    *   Acepta fracciones en el campo `Used` para facturar medios días[cite: 2].
    *   Botones de acción masiva (`Set all to Full Charge`, etc.) actualizan todas las filas y recalculan el costo diario y acumulado[cite: 2].

## 5. Operaciones de Filtración (Filtration Tab)
*   **Aislamiento de Lógica Comercial vs. Operativa (Regla Estricta):**
    *   La facturación monetaria de los equipos de filtración se ingresa **exclusivamente** en la tabla de utilización de la pestaña `Equipment`[cite: 2]. 
    *   Los datos operativos y de uso se registran **exclusivamente** en la pestaña `Filtration`[cite: 2].
*   **Métricas del Ciclo:**
    *   Requiere obligatoriamente muestras de entrada (`Suction`) y salida (`Discharge`), permitiendo hasta 10 muestras intermedias[cite: 2].
    *   Registra NTUs, porcentaje de sólidos, flujo promedio y consumibles gastados (`Cartridges Used`, `DE Sacks Used`)[cite: 2].
    *   Rastrea el tiempo de inactividad (`Downtime Reason`, `Duration of Issue`) para el cálculo de horas NPT (Non-Productive Time)[cite: 2].