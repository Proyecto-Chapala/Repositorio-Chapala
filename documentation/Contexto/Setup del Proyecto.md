# Módulo 1: Project Setup & General Information
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Project Information

## 1. Modelo Principal: Configuración del Pozo (General Tab)
Este módulo define la identidad del proyecto y las variables que dictan el comportamiento global del sistema[cite: 2].

*   **Identificación (Inmutables tras creación):**
    *   `Log-It Number`: Identificador único corporativo[cite: 2].
    *   `Unit Set`: Sistema de unidades (`Standard Oilfield`, `Metric`, etc.)[cite: 2]. Se bloquea definitivamente al crear el primer reporte diario[cite: 2].
    *   `Decimal Char` y `Currency`: Bloqueados tras el primer reporte diario[cite: 2].
*   **Parámetros Offshore (Condicionales):**
    *   `Is Offshore?`: Checkbox que bloquea su estado tras el primer día[cite: 2].
    *   Campos dependientes: `Air Gap (ft)`, `Water Depth (ft)`, `Sea Floor Temp (°F)`[cite: 2]. Estos campos numéricos sí pueden actualizarse durante el proyecto[cite: 2].
    *   `Uses Riser`: Activa la contabilidad volumétrica del riser[cite: 2].
*   **Gradientes Térmicos (Cálculo Hidráulico):**
    *   `Surface Temp` y `Temp Gradient`: Críticos para cálculos de presión anular según API 5ta Edición[cite: 2].

## 2. Gestión de Fases Operativas (Intervals Tab)
Los intervalos dividen la contabilidad de costos y fluidos del pozo por etapas de perforación o completación[cite: 2].

*   **Atributos del Intervalo:**
    *   `Interval Number` y `Operational Mode` (`Drilling` o `Completion`)[cite: 2].
    *   `Type`: Casing, Liner, u Open Hole[cite: 2]. Determina si los campos `Casing OD` y `Casing ID` se habilitan[cite: 2].
    *   `Time First Used`: Selector de hora (ej. `00:00`) que marca el inicio exacto del intervalo para la distribución de costos[cite: 2].
*   **Atributos de Completación (Dinámicos):**
    *   Si `Type == Completion`, la interfaz despliega los campos de cañoneo (`Perforations From / To`) y presión de formación (`BH Formation Pressure`)[cite: 2].
*   **Regla de Negocio: Interval Transaction Movement:**
    *   Los volúmenes y transacciones pueden moverse masivamente de un intervalo a otro usando rangos de fechas mediante la función `Move Transactions`[cite: 2]. Esto reasigna la contabilidad sin alterar la fecha original de la transacción[cite: 2].

## 3. Catálogo de Personal (Personnel Setup Tab)
Gestiona los ingenieros y técnicos asignados, vinculándolos a la facturación diaria del reporte[cite: 2].

*   **Campos de Registro:**
    *   `Name`, `LDAP ID`, `Email` (`@slb.com` preferido)[cite: 2].
    *   `Service Line` y `Charge Item` (Código de facturación contable)[cite: 2].
    *   `Daily Charge Amount`: Tarifa plana diaria[cite: 2].
*   **Validación de Identidad (LDAP):**
    *   Botón `Validate SLB User Names`[cite: 2].
    *   **Lógica UI:** Al consultar el servidor corporativo, la celda se pinta de verde si es válida, rojo si no existe, o se mantiene sin color si no se ha validado[cite: 2].

## 4. Flujo de Cierre de Proyecto (Project Closeout)
Proceso estricto de bloqueo de escritura (Read-Only) para auditoría y facturación final[cite: 2].

*   **Condición de Activación:** El botón `Project Closeout` solo funciona si el usuario se encuentra en el último día registrado del proyecto[cite: 2].
*   **Validaciones en Cascada (Hard Stops):**
    1.  Verificación de datos maestros (TD, fechas, costos)[cite: 2]. Si falta información, el sistema arroja error y detiene el proceso[cite: 2].
    2.  Verificación estricta de LDAP válido para todo el personal[cite: 2].
    3.  Confirmación mediante Checkbox obligatorio: *"I certify that the information above is complete and accurate..."*[cite: 2].
    4.  Auditoría de Problemas: Exige confirmar tabla de `Operational Problems` y `Fluid Problems`[cite: 2].
*   **Reapertura (`Re-open Project`):** Solo activa si el pozo está cerrado. Exige repetir todo el proceso de validación en cascada para volver a cerrarlo[cite: 2].