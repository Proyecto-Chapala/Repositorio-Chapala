# Correcciones de la revisión con el cliente (octubre 2026)

Fuente: transcripciones en `docs/fuentes/transcripciones_revision_oct/` (`1.txt`, `2.txt`, `3.txt`).
Estado: **hechos** los puntos 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 17 y 18. En el 1, el bloqueo era el rechazo por falta de existencia en la matriz (migración `0028_inventario_por_pozo`), y la parte de pérdidas y transferencias editables se resolvió con el 11. Hay que probarlos en pantalla. El resto sigue **pendiente**.

> **Punto 7, causa encontrada:** la fórmula ya existía en el motor (`volumetria.volumen_quimico_bbl`). El volumen salía en 0 por dos motivos. Primero, el inventario unificado rechazaba el agregado de químicos por falta de existencia en la matriz, así que el movimiento nunca se guardaba. Segundo, un producto en peso se podía guardar sin GE o sin tamaño de unidad, y entonces aportaba 0 sin avisar. Ahora *Productos activos* exige los dos datos a los productos medidos en peso (lb, kg, t), y la pestaña 8 muestra la columna **GE**.

> **Punto 8, decisión del usuario:** cada producto activo tiene un solo precio y un selector **Cobrar por: unidad | barril**. Si es por barril, el sistema calcula los barriles que ocupa cada unidad: con la GE si el producto se mide en peso, o por conversión directa si se mide en volumen. El motor sigue trabajando con precio por unidad (`volumetria.precio_por_unidad`). Para cobrar por barril, la unidad tiene que ser de peso o de volumen. Migración `0029_productoactivopozo_cobro_por`.

> **Punto 11, decisión del usuario:** "modificable" significa **editar los movimientos**. Transferencias, devoluciones y pérdidas se editan (tanque, destino, volumen, tipo) y cualquier movimiento del reporte se puede eliminar, no solo el último. Se mantiene la fórmula: cada cambio repite la línea de tiempo y se rechaza si algo deja de ser posible. No se agregaron ajustes manuales sueltos por celda. Pruebas: [pruebas/08](pruebas/08_EDITAR_MOVIMIENTOS.md).

> **Punto 10, causa encontrada:** el motor no tenía error. Se verificó que cada movimiento aparece en una fila del balance y que las filas suman el calculado (`tests/test_balance_volumetria.py`). La diferencia del cliente era el volumen de químicos en 0 (punto 7). Una diferencia que quede ahora es fluido realmente perdido y se registra como pérdida. Su ajuste manual es el punto 11.

> **Punto 9, decisión del usuario:** las dos tarifas son **alternativas**. Cada producto, equipo y malla tiene su precio en cada moneda (el del contrato, sin tasa de cambio), y el pozo elige en cuál cobra. Reemplaza el reparto por % y tasa del 02-oct. Detalle en [13](13_COSTOS.md). Migración `0031_tarifas_dos_monedas`.

> Prioridad sugerida: empezar por **Inventario (1–8)**, porque bloquea la volumetría.

## Inventario

1. **Desbloquear los campos del inventario diario.** Recibido, Devuelto, Usado hoy, Usado en otro módulo y Ajuste tienen que ser editables, porque son la carga diaria del ingeniero.
2. **Separar el inventario del pozo de la matriz/almacén.** La matriz es solo un catálogo (código, nombre, libraje/presentación) y no debe pasar al pozo ni cantidades ni costos.
3. **Precios en cero por defecto.** El precio lo ingresa el usuario según el contrato. No viene de la matriz ni aparece en los tickets, porque el contratista no debe ver precios.
4. **Lógica de Inicial y Final:**
   - La primera recepción por ticket define el **Inicial**.
   - Cada recepción nueva (ticket de almacén, de otro taladro o de otro pozo) se suma.
   - `Final = Inicial + Recibido − Devuelto − Usado − Usado otro módulo ± Ajuste`.
   - Al día siguiente, Recibido = 0 e Inicial = Final del día anterior.
5. **Mostrar el número de ticket en el inventario** al recibir. La cantidad real recibida puede ser distinta de la del ticket.
6. **"Usado en otro módulo"** (por ejemplo, cementación) descuenta inventario pero **no** afecta concentraciones ni volumetría del fluido.
7. **Gravedad específica (GE) por producto** (sólido/líquido), editable. Se usa para calcular el volumen agregado:
   `volumen (bbl) = libras / (350 × GE)`.
   Ese valor alimenta "Volumen de químicos agregados" en la volumetría. Hoy, al faltar la GE, no se calcula volumen.
8. **Dos tipos de precio:** **precio por unidad** (lb, saco, tambor, cuñete) y **precio por barril** (por ejemplo, salmuera 8.5). `Costo del día = cantidad × precio`.

## Monedas

9. **No hay "tercera moneda por barril".** El barril es solo una unidad de precio. Lo que se requiere es poder registrar **tarifa en USD y en Bs** para un mismo ítem y mostrar el costo en la moneda elegida, según el contrato.

## Volumetría

10. **El balance tiene que cerrar en 0.** Hoy aparece una diferencia (por ejemplo, 3), probablemente porque falta el volumen por material (punto 7).
11. **Pérdidas y transferencias modificables:** mantienen la fórmula, pero el ingeniero puede ajustarlas manualmente para cuadrar el balance.
12. **Transferencias:** tanque a tanque, envío a otro pozo y recepción desde otro pozo o almacén. Las pérdidas se registran por tanque de origen, así que los tanques deben estar definidos antes.
13. **"No ocupado por fluido":** al cerrar un sidetrack con tapón, el volumen por debajo del sidetrack pasa a no fluido (dejado/entrampado en el hoyo). Hay que verificar que la opción aparezca al marcar sidetrack, porque en la prueba no salió.

## Sidetrack / geometría

14. **Cerrar intervalo "como sidetrack"** (no como producción). En la prueba se cerró, pero no quedó guardado como sidetrack.

## Propiedades extra / reportito de 8 horas

15. **Las propiedades extra no se muestran.** Se guardan, pero no aparecen en la prueba o columna elegida (por ejemplo, % de carbonato). Tienen que mostrarse con su nombre y unidad.
16. **Reportito de propiedades editable:**
    - La hora de cada prueba la define el usuario (por ejemplo, 10:00 en lugar de 12:00).
    - Al exportar (Excel/PDF) deben salir todas las propiedades, el punto de muestreo (Flowline, Succión…) y los comentarios. Hoy las propiedades no salen.
    - Se descarga aparte del reporte general.

## Costos: categorías

17. **Ingeniero de fluidos:** no se encuentra dónde se carga su costo. Hay que revisarlo o hacerlo visible.
18. **Nueva categoría "Trailer":** se comporta como el ingeniero (tarifa diaria + acumulado). No afecta inventario ni volumen y **no** es equipo de control de sólidos. Se necesita para la próxima semana.

## Tickets

19. Tickets de entrega/envío y de recepción **sin precio**. Pendiente: pedir a administración la codificación de los números de guía/ticket.

## Hidráulica

20. Está bien en general. Pendiente: cargar el catálogo de herramientas/componentes del mercado. El Riser no aplica, porque no se trabaja en plataforma.

## Próxima sesión con el cliente

Prueba integral en un pozo nuevo: hoyo de 8½" con piloto, ampliación y varios sidetracks, y al final la impresión del reporte. Se harán dos equipos por computadora más una pantalla compartida. Después de esa sesión se cierra la revisión.
