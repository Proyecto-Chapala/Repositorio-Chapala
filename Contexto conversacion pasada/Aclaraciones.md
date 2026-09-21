Sección 6 "Equipo de Sólidos" NO es lo mismo que tu inventario de materiales/productos (químicos). Es un dominio distinto: se trata del equipo físico de control de sólidos (mallas vibratorias, centrífugas) y su desempeño durante la perforación. Mira sus 5 subsecciones: (Imagen)

el reporte diario no tiene sus propios campos maestros — todo lo que aparece como dropdown, botón de configuración, o cálculo automático, apunta hacia datos que se cargaron una sola vez en "Well Information". Si no existen esas pantallas, el reporte diario quedaría con dropdowns vacíos y sin poder calcular nada.

Dicho esto, no todos los 11 botones pesan igual. Con lo que he visto hasta ahora, puedo separarlos en dos grupos:

Imprescindibles para que el reporte diario funcione (alimentan directamente las 8 pestañas):

Well Header Information
Well Survey
Well Casing Intervals (Cost)
Active Products/Equipment/Screens
Loss Setup (probablemente para la pestaña 8)
Equipment Properties Setup (probablemente para la pestaña 6 y 2)
Benchmark Setup (para la pestaña 8)

Más bien de reporte/consulta, no alimentan la captura diaria en sí:

Unscheduled Events
Cost Overview
Pit Information (esta habría que confirmarla — puede que sí sea clave para volumetría, que ya dijiste que la vemos después)
General Setup (depende de qué configure exactamente — falta verlo)

[8:53 p. m., 17/9/2026] Román H: ¿Correcto, o el nombre se puede repetir y lo que identifica al pozo es otra cosa (ej. operador + nombre)?
Correcto no se pueden repetir

Categorías de pérdida predefinidas (M-I, UK, Hydro, Statoil, IFE) — por ahora solo guardo el tipo elegido (categoria_perdida_tipo) en el pozo; no traje las tablas fijas de esas listas (código/descripción de cada una) porque no las mostraste completas, solo la de M-I en la Imagen 2 de hace un rato (Shakers, Evaporation, Centrifuge, Formation, Left in Hole, Other). ¿Las tienes o las cargamos luego como datos semilla (fixtures)?

Se cargan luego como datos semilla

El campo unidades_personalizadas lo dejé como JSON en vez de una tabla aparte, para no crear un modelo con ~15 columnas fijas. ¿Te parece bien ese enfoque o prefieres una tabla relacional tipo CategoriaPerdidaItem?

Lo mejor es trabajar con tablas relacionesles, recuerda que las tablas deben ser clara con los campos para poder auditarlas correctamente.
[8:54 p. m., 17/9/2026] Román H: Ya quedó el modelo con tablas relacionales auditables:

Pozo — datos base, financiero, estado del wizard.
PropiedadUnidadPozo — una fila por cada una de las 16 propiedades de ingeniería (Profundidad, Caudal, Presión, etc.), cada una con su unidad elegida. Incluye validación (clean()) contra la lista de opciones válidas por propiedad, para que nadie guarde una unidad inválida.
CategoriaPerdidaItem — una fila por categoría de pérdida personalizada (Código, Descripción, Superficie/Subsuelo).
