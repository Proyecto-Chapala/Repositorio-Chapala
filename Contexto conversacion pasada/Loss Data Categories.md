Imágenes 1-2 — Loss Data Categories (Categorías de Pérdida de Fluido):

En la pantalla de "New Well Information" hay un botón "Change" junto a Loss Data Categories (mostrando "M-I" como valor actual). Esto define dónde se puede perder fluido durante el proyecto — se usa para la contabilidad de volumen.
Al hacer clic, abre "Loss Setup": un dropdown con listas predefinidas (M-I, UK, Hydro, Statoil, IFE, Completion Fluids, Custom) y una tabla con Código/Descripción (ej. 1-Shakers, 2-Evaporation, 3-Centrifuge, 4-Formation, 5-Left in Hole, 6-Other).
Si eliges "Custom", puedes editar las etiquetas de cada categoría, y además para cada una defines si la pérdida es "Surface" o "Subsurface" (si el fluido se pierde en superficie o dentro del pozo).

Imagen 3 — Currency Symbol & Tax Rate:

Símbolo de moneda (⚠️ también queda bloqueado una vez das OK, igual que las unidades — dato importante que no había capturado antes).
Tax Rate % (este sí se puede cambiar después).
Nombre del archivo del pozo, y el botón OK final que crea el pozo.

Imagen 4 — Esto es un flujo aparte: no es parte de "Nuevo Pozo", es "Abrir Pozo Existente" (ONE-TRAX Wellsite → botón "Open" → explorador de archivos .MDB). Es decir, la pantalla de inicio tiene dos caminos distintos: crear uno nuevo, o abrir uno ya creado — no lo mezclo con el wizard de creación.

Ajuste al plan de 4 pasos:

Con este nuevo dato, el Paso 4 (Financiero/Ajustes) se está llenando bastante: Moneda, Decimales, Tax Rate, Ecuaciones de Sólidos (agua/aceite), y ahora también Categorías de Pérdida. Para no amontonar todo, propongo que Categorías de Pérdida funcione igual que "Custom Units" en el Paso 2: un dropdown con las listas predefinidas, y solo si eligen "Personalizado" se despliega la tabla editable (Código, Descripción, Superficie/Subsuelo) dentro del mismo Paso 4 — sin crear un Paso 5.

Paso 1 — Datos Básicos: Nombre del pozo + plantilla (clonar de pozo anterior, sí/no).

Paso 2 — Sistema de Unidades: Presets en tarjetas (Standard Oilfield, Métrico, etc.) + acordeón "Personalizado" con los ~15 dropdowns si aplica.

Paso 3 — (lo dejamos igual que tenías, o si quieres lo renombro): ¿Este paso lo reservamos para algo específico, o prefieres que sea directamente "Resumen y Confirmación" antes de crear el pozo?

Paso 4 — Ajustes Financieros y de Pérdida: Moneda, Decimales, Tax Rate, Ecuaciones de Sólidos (agua/aceite), y el acordeón de Categorías de Pérdida (dropdown con listas predefinidas: M-I, UK, Hydro, Statoil, IFE, Completion Fluids, Custom → tabla editable con Código/Descripción/Superficie-Subsuelo si elige Custom) + nombre del archivo + botón final "Crear Pozo".

Y aparte, ya anotado como flujo independiente (fuera del wizard): "Abrir Pozo Existente" — se queda como una acción separada desde la pantalla de inicio, no forma parte del wizard de creación.

Imagen 1 — "Spud Date" (pantalla de un solo uso):
Aparece solo la primera vez que se abre el pozo (después del wizard de creación, antes de entrar a cualquier módulo). Pide:

Primera fecha de datos del archivo (puede ser anterior a la fecha de spud) — inmutable tras dar OK.
Tipo de fluido para el primer chequeo (Water Base, Water Base CaCl2, Oil Base, Synthetic Base, Completion Fluids) — también inmutable.
Checkbox "Con Tratamiento y Disposición de Desechos" (esto sí se puede activar después).
Número de Control de Proyecto Log-It (opcional).

Imágenes 2-5 — "Project Main Screen" (la pantalla central del pozo ya creado):
Aquí es donde entiendo que se reorganiza todo lo que habíamos hablado. Esta pantalla muestra:

Encabezado: Operador, Nombre del Pozo, Sistema de Unidades (fijo, de solo lectura).
Bloque "Well Information" (Configuración del Proyecto y Datos Comunes) — 11 botones: Well Header Information, Loss Setup, Well Casing Intervals (Cost), Active Products/Equipment/Screens, Well Survey, Benchmark Setup, Pit Information, Equipment Properties Setup, General Setup, Unscheduled Events, Cost Overview.
Bloque "ONE-TRAX Modules" (Módulos de Captura Diaria) — 4 botones: Drilling Fluids and Equipment (este es el que ya tiene las 8 secciones que armamos), RDF Module, Completion Fluids, Waste Treatment and Disposal.
Recap Reports, Activate GRAFX, Exit.

Imágenes 6-7 — "Well Header Information" (uno de los 11 botones de Well Information):
Formulario detallado con 2 pestañas ("1-Well Information" y "2-Marketing Codes"): Operador, Nombre de Pozo, Ingenieros MI SWACO 1/2, Campo/Área, Descripción, Ubicación, Warehouse, Contratista, Taladro, Ingeniero de Proyecto, fechas de Spud/TD, TD Days, Re-Entry Depth, coordenadas, Surface Temp, Temp Gradient, sección Offshore (Air Gap, Water Depth, Sea Floor Temp), sección End of Well (Total Depth, TVD, Horiz. Displacement, Total Days, End Date, Total Cost, Max Temp), Comentarios, y Número de Control Log-It.