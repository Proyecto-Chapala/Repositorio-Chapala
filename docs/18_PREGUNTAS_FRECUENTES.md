# 18 — Preguntas frecuentes

### ¿La pestaña 8 usa el mismo inventario que la pantalla *Inventario*?
Sí. Desde el 25-sep-2026 hay **un solo inventario**: lo que se usa en el reporte diario se descuenta de la cantidad de la pantalla *Inventario* (de todos los pozos). Si un producto sale en 0, carga la existencia en *Inventario*. Los tickets de productos son solo registro. Detalle en [15](15_INVENTARIO_ALMACEN.md).

### No me deja instalar una malla nueva: "no hay mallas nuevas en stock".
Primero registra en la pestaña 6 un **ticket de mallas** de tipo entrada con las mallas **nuevas** recibidas (cantidad real). (Con los productos es distinto: su existencia se carga en *Inventario*.)

### Me rechaza un cambio en un día viejo, diciendo que otro día queda negativo.
Es a propósito. El sistema vuelve a calcular **todos** los días del pozo y no permite que ninguno quede con inventario negativo. Corrige primero el día que indica el mensaje (por ejemplo, agregando el ticket de mallas que falta) o deshaz el cambio.

### ¿Cómo corrijo un movimiento mal hecho?
Con **Deshacer la última transacción**, que solo sirve para el **último** movimiento del pozo y solo desde su propio reporte. Si ya hay movimientos posteriores, hay que deshacerlos en orden inverso, o compensar con otro movimiento (por ejemplo, un ajuste de inventario).

### ¿Por qué el volumen calculado del tanque activo no coincide con el real?
Porque el **hoyo es parte del sistema activo**. El balance se hace por **grupo** (activo = tanques activos + fluido en el hoyo), no por tanque. Lo que debe quedar en cero es el **"No contabilizado" del grupo**. Si no queda en cero, registra la pérdida o el movimiento que falta: **no cambies el volumen real** para cuadrar.

### La lista de modelos de bomba solo me muestra un modelo.
El campo filtra las sugerencias por lo que ya está escrito. Bórralo y haz clic de nuevo o presiona ↓ para ver todos. También puedes escribir cualquier modelo.

### El Excel trae hojas o páginas vacías y repetidas.
Ya no debería pasar: desde el 02-oct-2026 queda **una sola hoja** de inventario químico, se borran las páginas sin productos y se quitan *Equipos* y *Mallas* si no tienen datos. Ver [14](14_REPORTE_EXCEL.md).

### La hidráulica de la pantalla no coincide con la del Excel.
La pantalla abre en la **5ª edición** y el Excel usa el ajuste del pozo (*Configuración General → Usar API 5ª edición*), que por defecto está en la 4ª. Activa ese ajuste o cambia la pantalla a 4ª para compararlas.

### La hidráulica dice "faltan datos".
Necesita: caudal de bombas y boquillas (pestaña 2), un chequeo de lodo con peso y R600/R300 o PV/YP (pestaña 3) y la sarta (pestaña 4). Guarda esas pestañas y vuelve a abrir la hidráulica.

### Los volúmenes del hoyo (pestaña 4) salen en 0 o raros.
Revisa: (1) que existan los **intervalos de revestimiento** con su ID y profundidad; (2) la **profundidad de la barrena** y la profundidad actual en la pestaña 1; (3) el **diámetro de la barrena o del washout** en la pestaña 2; (4) la **sarta**, cargada desde la mecha hacia arriba. En pozos offshore con riser, el ID del riser es obligatorio.

### No puedo crear un reporte: "Ya existe un reporte para esa fecha".
Solo se permite un reporte por día y pozo. Ábrelo desde el historial del hub (botón **Abrir**).

### El número de reporte cambió.
El número se calcula por fecha. Si se crea un reporte de una fecha anterior (o se borra uno por la API), los siguientes se renumeran.

### No puedo cambiar la fecha de primera captura ni el tipo de fluido inicial.
Quedan fijos al confirmar la pantalla **Fecha inicial** (antes *Spud Date*). Solo se pueden cambiar desde `/admin/`, con cuidado.

### Cambié el precio de una malla o de un equipo, pero los días anteriores siguen con el precio viejo.
Es correcto: el precio se **congela** al registrar la instalación (mallas) o el uso (equipos). Así el costo histórico no cambia.

### ¿Qué pasa si quito un producto, equipo o malla de la lista activa del pozo?
Los datos de días anteriores se conservan (guardan su propia copia). Los productos quitados siguen apareciendo en el inventario de la pestaña 8 como inactivos si tuvieron movimiento.

### No puedo borrar un producto del Inventario.
Solo se puede borrar con cantidad 0 y si **no está activo en ningún pozo**; si lo está, el mensaje dice en qué pozos. Tiene historia en los reportes, así que no conviene borrarlo.

### Los cambios en la pantalla no se ven después de actualizar el sistema.
Presiona **Ctrl + F5** para recargar sin caché.

### No me deja crear un intervalo nuevo.
Hay un intervalo **abierto**. Cuando se baje el revestidor, abre ese intervalo, completa tipo y profundidad, **Guardar** y **Cerrar intervalo**. Recién ahí se habilita **+ Nuevo**.

### ¿Dónde borro un reporte que empecé mal?
La página de Fluidos de Perforación y Equipos está bloqueada (solo crea y abre). Si el pozo completo se empezó mal, usa **Eliminar pozo** en la pantalla del pozo. Corrige un reporte con movimientos o ajustes.

### ¿Cómo cobro parte en dólares y parte en bolívares?
En *Configuración General → Cobro en una Segunda Moneda* elige la moneda, la tasa y el %. La pantalla de costos del reporte muestra cuánto va en cada moneda. Ver [13](13_COSTOS.md).

### Cerré el navegador y el sistema sigue abierto.
Es normal con `SmartMud.exe`: queda la gota junto al reloj. Doble clic en la gota o en `SmartMud.exe` lo abre de nuevo; clic derecho → **Salir** lo cierra.
