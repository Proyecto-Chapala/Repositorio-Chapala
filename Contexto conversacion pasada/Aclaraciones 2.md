
Project Main Screen (nueva, antes solo sabíamos que faltaba)
Header: Operator, Well Name, Unit System (resumen de solo lectura).
Botones "Well Information" (columna izq. + der., 11 en total — coincide exacto con tu lista de memoria):
Well Header Information, Well Casing Intervals (Cost), Well Survey, Pit Information, General Setup, Loss Setup, Active Products/Equipment/Screens, Benchmark Setup, Equipment Properties Setup, Unscheduled Events, Cost Overview.
Sección "ONE-TRAX Modules": Drilling Fluids and Equipment, RDF Module, Completion Fluids, Waste Treatment and Disposal.
Extra: Recap Reports, Activate GRAFX.

Well Header Information — Tab 1 "Well Information"

Offshore (obligatorio si aplica, afecta cálculos de volumen): Air Gap, Water Depth, Sea Floor Temp.
Well Data: Operator, Well Name, Field/Area, Description, Location, Warehouse, Contractor, Rig Name, Project Engineer, M-I SWACO Engineer 1 y 2, Spud Date, TD Date, TD Days, Re-Entry Depth, Latitude NS Indicator, Longitude EW Indicator, Surface Temp, Temp Gradient (estos 2 últimos + Sea Floor Temp son los 3 campos nuevos de "API 5th edition", opcional pero si se usa hay que llenarlos).
End of Well (se llena al FINAL del pozo, no al crearlo): Total Depth, Total Days, Maximum Temperature, TVD, End Date, Total Cost (calculado), Horiz. Displacement (nuevo, identifica pozos Extended Reach).
Comments (texto libre), Log-It Project Control Number (+ botón Edit).
Flujo: completar → Save → pasar a Tab 2.

Tab 2 "Marketing Codes"

Primary Mud Type, Well Type, Contract Type, Completion Fluid Type — cada uno es un código (dropdown) + descripción auto-rellenada.
Obligatorio antes de subir a ONE-TRAX Central (no bloquea el uso diario, se puede llenar después).

Well Casing Intervals (Cost)

Tabla resumen "Casing Interval Summary": Interval Number, Type, Casing OD, Casing ID, Depth, TVD, Top of Liner, Hole Size, Maximum Angle, Maximum Density, Frac Grad, Fluid Type Code 1 y 2. Botones New / Edit / Exit.
Al dar "New" se abre el formulario del intervalo: Interval Number, Type, Casing OD/ID, Hole Size, Depth, TVD, Top of Liner, Maximum Density, Max BHT (renombrado de "Max Temperature"), Maximum Angle, Interval Days, Planned Days, Planned Length, Interval Cost (calculado), Planned Cost, Frac Grad, Fluid Type Code 1 y 2, botón "Unscheduled Events", botón "Interval Comments for Recap" (nuevo, hasta 10,000 caracteres), y "Observations and Recommendations" (texto libre).
Se puede crear el intervalo 1 vacío y salir sin llenar más — la fila queda resaltada en amarillo indicando que el costo del intervalo fue creado.

Esta es Pit Information, accesible desde el Project Main Screen:

Pits and Tanks Information (tabla principal, hasta 30 filas)

Columnas: Pit No. (autonumérico), Pit Description, Capacity.
Ejemplo simple: Pit #1-6, Slug Pit, Sand Trap, Trip Tank.
Regla clave: el nombre/descripción de la fosa es solo descriptivo — su uso real en la operación diaria lo determina el "Pit Type" que se seleccione día a día en la pestaña "Volume Accounting" (que cae dentro del módulo 8, Vol. Accounting and Product Inventory).
Advertencia explícita: no usar "Active", "Reserve" ni "Premix" como parte del nombre de la fosa, porque puede confundir la captura de datos durante el pozo (aunque tu tercera captura muestra un caso real donde sí lo hicieron — Active-1, Reserve-1, Premix-1 — como ejemplo de qué NO hacer, o de que el sistema lo permite pese a la sugerencia).
Botón "Save as Default" — guarda esta configuración de fosas como plantilla por defecto (esto conecta directo con el mecanismo que ya tienes en el modelo Pozo para clonar configuración desde un pozo plantilla).

Pit Type Setup (panel secundario, botón desde la pantalla anterior)

Lista de tipos de fosa: # + Descripción.
Lista estándar por defecto: 0-Empty, 1-Active, 2-Reserve, 3-Premix, 4-Spacer, 5-Pill, 6-Breaker.
Pill y Breaker son nuevos en esta versión de ONE-TRAX — cubren necesidades del nuevo "RDF Module" pero también están disponibles en "Completion Fluids".
Extensible: se pueden agregar tipos personalizados adicionales (tu ejemplo muestra "Base Oil" y "Brine" agregados a mano).
También tiene su propio "Save as Default".

Esto encaja con el modelo de datos que ya tienes: básicamente son dos tablas relacionadas al Pozo — Fosa (número, descripción, capacidad) y TipoFosa (código, descripción), ambas clonables como plantilla, igual que PropiedadUnidadPozo y CategoriaPerdidaItem.

Analizando estas dos pantallas:

General Setup — Esta pantalla resume la configuración del archivo/proyecto y no está implementada todavía (ni el modelo, ni la vista, ni la pantalla existen). Lo que trae:

Bloque "Setup": Decimales de Moneda, Símbolo de Moneda, Tasa de Impuesto (%).
Casilla "Con Tratamiento y Disposición de Desechos" (esto ya existe parcialmente como concepto: el modelo Pozo no tiene ese campo todavía, habría que agregarlo).
Casilla "Usar API 5ta Edición para Cálculo Hidráulico" con botón de ayuda.
Botón Warehouse Code Setup → abre un popup con tabla Código / Nombre de Almacén (CRUD simple, "Guardar como Predeterminado"). No existe modelo Almacen aún.
Botón Time Distribution Setup → abre un popup con tabla Número / Descripción / Tipo (DF, CF o DF/CF) — es el catálogo de actividades de taladro en 24h (Rig Up/Service, Drilling, Tripping, BOP NU, Cementing, Condition Hole, etc.). No existe modelo para esto.
"Solids Analysis Equations": Water-Based Mud / Oil-Based-Synthetic-Based Mud, ambos con valor "M-I" (parecen ser un selector de fórmula, probablemente fijo a M-I SWACO).
"Windows": Símbolo Decimal y Formato de Fecha — ONE-TRAX aclara que estos los controla Windows, no la app; en nuestro caso no aplican (Django ya maneja esto por configuración regional del servidor), así que podemos omitirlos o dejarlos solo informativos.

Loss Setup — Aquí sí hay una base ya construida: el modelo CategoriaPerdidaItem (código, descripción, Superficie/Subsuelo) ya existe exactamente con esos 3 campos, y se llena durante el Paso 3 del wizard de creación del pozo cuando el pozo usa categorías personalizadas (categoria_perdida_tipo = 'CUSTOM'). Lo que falta es lo que muestra esta imagen: una pantalla independiente, accesible después de creado el pozo (como Información General, Intervalos de Revestimiento y Fosas), con tabla editable + botones Agregar/Eliminar + "Guardar como Predeterminado", para poder modificar esas categorías en cualquier momento sin tener que pasar por el wizard otra vez. Esa es la tarjeta "Configuración de Pérdidas" que dejamos como "Próximamente" en la Pantalla Principal.

