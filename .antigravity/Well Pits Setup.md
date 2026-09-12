# Módulo 3: Configuración Geométrica y de Fosas (Lithology, Well Survey, Pits & Loss Setup)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Project Information

## 1. Topología de Superficie: Arquitectura de Tanques (Pit Setup Tab)
Este submódulo establece el inventario físico de las fosas del taladro y sus reglas de comportamiento volumétrico[cite: 2].

*   **Transactional Pits and Tanks:**
    *   Fosas donde el software calcula automáticamente los volúmenes[cite: 2]. Son afectadas directamente por transacciones de `Add Chemical`, `Add Whole Mud` y `Transfer`[cite: 2].
    *   **Validación de Integridad Relacional:** Un tanque no puede ser eliminado si ya fue utilizado en un registro diario (`The Record Is In Use By Table [DayPit]`)[cite: 2].
    *   **Actualización Retroactiva:** Si se edita la descripción o capacidad de una fosa, el cambio afecta a todos los registros diarios creados previamente[cite: 2].
    *   **Validación de Unicidad:** El sistema prohíbe descripciones duplicadas; si se ingresa un nombre idéntico, la fila se resalta en rojo indicando `Pit Description is Invalid`[cite: 2].
*   **Pit Types (Tipos de Fosas):**
    *   Define categorías operativas (`Active`, `Reserve`, `Premix`, `Spacer`, etc.)[cite: 2]. 
    *   El catálogo mezcla valores predefinidos (fondo gris, inmutables desde la base de datos) y valores definidos por el usuario (fondo blanco, editables)[cite: 2].
*   **Non-Transactional Pits:**
    *   Fosas de almacenamiento puro (ej. `Base Oil Storage`)[cite: 2].
    *   **Regla Estricta de Negocio:** No son afectadas por ninguna transacción contable de volumen de ONE-TRAX (no se les puede aplicar `Transfer`, `Dump` ni `Add Chemical` transaccional)[cite: 2]. Sus balances se ingresan de manera estrictamente manual en el reporte diario[cite: 2].

## 2. Geometría Direccional y Fluidos (Lithology / Well Survey / Fluid Systems Tab)
Define las características del subsuelo y la disponibilidad de sistemas químicos[cite: 2].

*   **Well Survey (Trayectoria Direccional):**
    *   Tabla que registra `Starting Depth (ft)`, `Inclination` y `Azimuth`[cite: 2].
    *   **Trigger de Cálculo:** Requiere que el checkbox `Use Well Survey` esté marcado para inyectar estos datos en los cálculos precisos de hidráulica del pozo[cite: 2].
    *   Permite importación masiva desde Excel mapeando las columnas exactas[cite: 2].
*   **Lithology:**
    *   Registra `Starting Depth`, `Lithology Type` y `% Sand`[cite: 2]. Su impacto principal es en la visualización cruzada de la herramienta `SnapShot` para correlacionar problemas de arrastre o hidráulica con la formación[cite: 2].
*   **Fluid Systems (Declaración Obligatoria):**
    *   Todo sistema de fluido a utilizarse en el pozo debe ser instanciado aquí para que aparezca en los reportes diarios[cite: 2].
    *   Asigna estrictamente un `Operational Mode` (`Drilling` o `Completion`) a un `Fluid System` específico (ej. `VERSACLEAN`, `Spud Mud`, `Calcium Chloride`)[cite: 2].

## 3. Categorización de Pérdidas (Loss Setup Tab)
Establece los motivos contables para justificar las reducciones del sistema activo[cite: 2].

*   **Aislamiento de Dominios (Isolation Rule):**
    *   Las categorías de pérdida **no se comparten** entre modos operativos[cite: 2]. Deben configurarse por separado para el modo `Drilling` y para el modo `Completion`[cite: 2].
*   **Pre-Defined Sets:**
    *   Permite la carga rápida de paquetes de categorías predefinidas en la base de datos maestra (ej. paquetes de justificación específicos de operadoras o conjuntos estándar como `Evaporation Related`)[cite: 2].