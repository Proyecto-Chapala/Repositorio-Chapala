# 18 — Preguntas frecuentes

### ¿Por qué un producto aparece con 0 en la pestaña 8 si en *Inventario* tiene muchas unidades?
Son dos inventarios distintos. *Inventario* (menú) es el **almacén**. La pestaña 8 es el inventario **en el taladro de ese pozo**, que empieza en 0. Para tener existencias en el pozo, registra un **ticket de recepción de productos** en la pestaña 8 con la cantidad real recibida. Después ya puedes usarlo en *Agregar químicos*. Detalle en [15](15_INVENTARIO_ALMACEN.md).

### No me deja instalar una malla nueva: "no hay mallas nuevas en stock".
Igual que con los productos: primero registra en la pestaña 6 un **ticket de mallas** de tipo entrada con las mallas **nuevas** recibidas (cantidad real).

### Me rechaza un cambio en un día viejo, diciendo que otro día queda negativo.
Es a propósito. El sistema vuelve a calcular **todos** los días del pozo y no permite que ninguno quede con inventario negativo. Corrige primero el día que indica el mensaje (por ejemplo, agregando el ticket que falta) o deshaz el cambio.

### ¿Cómo corrijo un movimiento mal hecho?
Con **Deshacer la última transacción**, que solo sirve para el **último** movimiento del pozo y solo desde su propio reporte. Si ya hay movimientos posteriores, hay que deshacerlos en orden inverso, o compensar con otro movimiento (por ejemplo, un ajuste de inventario).

### ¿Por qué el volumen calculado de la fosa activa no coincide con el real?
Porque el **hoyo es parte del sistema activo**. El balance se hace por **grupo** (activo = fosas activas + fluido en el hoyo), no por fosa. Lo que debe quedar en cero es el **"No contabilizado" del grupo**. Si no queda en cero, registra la pérdida o el movimiento que falta: **no cambies el volumen real** para cuadrar.

### La lista de modelos de bomba solo me muestra un modelo.
El campo filtra las sugerencias por lo que ya está escrito. Bórralo y haz clic de nuevo o presiona ↓ para ver todos. También puedes escribir cualquier modelo.

### El Excel trae hojas o páginas vacías y repetidas.
Hay tres hojas de inventario químico (por código, por nombre y completa) y la plantilla trae 3 páginas dibujadas en cada una. Al **imprimir** solo salen las páginas con datos. Ver [14](14_REPORTE_EXCEL.md).

### La hidráulica de la pantalla no coincide con la del Excel.
La pantalla abre en la **5ª edición** y el Excel usa el ajuste del pozo (*Configuración General → Usar API 5ª edición*), que por defecto está en la 4ª. Activa ese ajuste o cambia la pantalla a 4ª para compararlas.

### La hidráulica dice "faltan datos".
Necesita: caudal de bombas y boquillas (pestaña 2), un chequeo de lodo con peso y R600/R300 o PV/YP (pestaña 3) y la sarta (pestaña 4). Guarda esas pestañas y vuelve a abrir la hidráulica.

### Los volúmenes del hoyo (pestaña 4) salen en 0 o raros.
Revisa: (1) que existan los **intervalos de revestimiento** con su ID y profundidad; (2) la **profundidad de la barrena** y la profundidad actual en la pestaña 1; (3) el **diámetro de la barrena o del washout** en la pestaña 2; (4) la **sarta**, cargada desde la mecha hacia arriba. En pozos offshore con riser, el ID del riser es obligatorio.

### No puedo crear un reporte: "Ya existe un reporte para esa fecha".
Solo se permite un reporte por día y pozo. Ábrelo desde el historial del hub.

### El número de reporte cambió.
El número se calcula por fecha. Si se crea o se borra un reporte de una fecha anterior, los siguientes se renumeran.

### No puedo cambiar la fecha de primera captura ni el tipo de fluido inicial.
Quedan fijos al confirmar la pantalla **Spud Date**. Solo se pueden cambiar desde `/admin/`, con cuidado.

### Cambié el precio de una malla o de un equipo, pero los días anteriores siguen con el precio viejo.
Es correcto: el precio se **congela** al registrar la instalación (mallas) o el uso (equipos). Así el costo histórico no cambia.

### ¿Qué pasa si quito un producto, equipo o malla de la lista activa del pozo?
Los datos de días anteriores se conservan (guardan su propia copia). Los productos quitados siguen apareciendo en el inventario de la pestaña 8 como inactivos si tuvieron movimiento.

### No puedo borrar un producto del Inventario.
Solo se puede borrar con cantidad 0. Si además se usó en algún pozo, hoy el sistema responde con un error del servidor (bug B3 en [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)): no se debe borrar, porque tiene historial.

### Los cambios en la pantalla no se ven después de actualizar el sistema.
Presiona **Ctrl + F5** para recargar sin caché.
