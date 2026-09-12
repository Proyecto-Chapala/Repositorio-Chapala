# Módulo 2: Catálogos Maestros (Product, Screens & Equipment Setup)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Project Information

## 1. Reglas de Validación Base: Approved vs. Un-Approved Items
Este patrón de diseño aplica transversalmente a los catálogos de Productos, Mallas y Equipos para proteger la integridad de la facturación[cite: 2].

*   **Approved Items:** Elementos extraídos directamente del maestro de datos corporativo de M-I SWACO[cite: 2]. 
    *   **Bloqueo de campos:** Los atributos críticos como `Item Code` y `Description` quedan bloqueados (Read-Only) en la interfaz para garantizar la sincronización con el sistema Flex-Billing[cite: 2].
*   **Un-Approved Items:** Elementos de terceros o variaciones no estándar (ej. equipos propios del taladro)[cite: 2]. 
    *   El usuario puede modificar libremente el `Item Code`, la descripción, el tamaño y la unidad de empaque[cite: 2].
    *   Un ítem `Approved` puede convertirse a `Un-Approved` mediante el botón `Unlock` si es necesario editarlo, perdiendo su enlace estricto de facturación[cite: 2].

## 2. Product Setup Tab (Catálogo de Químicos y Fluidos)
Define la lista de materiales consumibles, sus costos y comportamiento físico[cite: 2].

*   **Atributos Físico-Contables (Models):**
    *   `Taxable`: Checkbox para cálculo de impuestos[cite: 2].
    *   `SG` (Specific Gravity): Gravedad específica del producto, requerida para el balance de masa volumétrico[cite: 2].
    *   `Show Conc?`: Flag crítico. Si está activo, el software calculará e incluirá la concentración de este producto ($\text{lb/bbl}$) cuando se añada al lodo[cite: 2].
    *   `Inventory Item`: Checkbox. Si se desmarca (ej. para cargos de flete o servicios), el sistema ignora las cantidades finales negativas y no exige conteo físico[cite: 2].
*   **Historial de Precios (Product Date Range Price Table):**
    *   Relación **1 a N** con el producto. Permite actualizar el precio (`Price`) a partir de una fecha de inicio (`Start Date`) sin alterar las transacciones facturadas en fechas anteriores[cite: 2].
    *   Al guardar un nuevo rango de precio, es obligatorio ejecutar el botón `Recalculate` para sincronizar los costos del inventario y evitar discrepancias[cite: 2].

## 3. Screens Setup Tab (Catálogo de Mallas)
Maneja el inventario de zarandas para control de sólidos[cite: 2].

*   **Inventario Inicial Dividido:**
    *   Al configurar una malla, la base de datos exige definir el stock de arranque separado en dos campos: `Start Qty New` (mallas nuevas) y `Start Qty Used` (mallas recicladas/usadas)[cite: 2].
*   **Atributos Principales:** `Mesh Size` (Tamaño API de la malla), `Price` y `Discount %`[cite: 2].

## 4. Equipment Setup Tab (Catálogo de Equipos Mecánicos)
Registra todo el hardware operativo (centrífugas, shakers, bombas) propio o de terceros[cite: 2].

*   **Atributos de Tarificación:**
    *   `Rental Price`: Costo diario operativo[cite: 2]. (Se establece en `0` si es equipo de la contratista del taladro[cite: 2]).
    *   `Stand-by Price`: Costo penalizado/reducido cuando el equipo está en locación pero no en uso continuo[cite: 2].
*   **Parámetros Técnicos Especiales:**
    *   `Hazardous Area Classification`: Define el nivel de riesgo de explosión del equipo (`Non-hazardous`, `Zone 0`, `Zone 1`, `Zone 2`)[cite: 2].
    *   **Validación Condicional (Centrífugas):** Si el `Equip. Type` es `Centrifuge`, se despliega un campo dinámico llamado `Property to recalculate`[cite: 2]. Permite al ingeniero elegir si la base de datos calculará matemáticamente el peso de descarga (`Discharge Weight`) o el caudal de descarga (`Flow Rate of the Discharge`)[cite: 2].
*   **Propiedades Custom (`Equipment Properties Setup`):**
    *   Permite crear dinámicamente columnas/atributos extra (ej. `Hours Ran`, `Vacuum Size`) asociados a tipos específicos de equipos para incluirlos en los reportes diarios[cite: 2].