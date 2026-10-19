# 28 — Rediseño de la interfaz: estilo técnico (rama `refactorizacion_ui`, 18-oct-2026)

Pedido del usuario: la interfaz se veía genérica, no era adaptable al celular y para llegar a los reportes había que dar muchos clics. Se armó un prototipo interactivo, el usuario eligió el estilo "más técnico" y se aplicó en la rama `refactorizacion_ui`.

## Decisiones

- **Estilo técnico**: gris pizarra, barra lateral casi negra, números y nombres de pozo en letra monoespaciada (JetBrains Mono), textos en IBM Plex Sans. Las dos fuentes van dentro del proyecto (ver "Fuentes dentro del proyecto").
- **Naranja solo para la acción principal y lo seleccionado.**
- **Íconos SVG en lugar de emojis**, dentro del HTML (`componentes/iconos.html`) para que funcionen sin internet.
- **Solo tema claro.** Hay miles de colores escritos a mano en los CSS de las pestañas del reporte; un tema oscuro rompería esas pantallas.
- Todo se hizo cambiando los valores de `variables.css` sin renombrar las variables, para que todas las pantallas cambien a la vez sin tocar su lógica.

## Qué cambió

| Parte | Qué hace | Archivos |
|---|---|---|
| Barra lateral | Íconos SVG, etiquetas "Operación" / "Acciones", botón Colapsar abajo | `componentes/sidebar.html`, `layout.css` |
| Barra superior | Ubicación (bloque `{% block migas %}`) y botón Buscar con Ctrl+K | `base.html`, `layout.css` |
| Buscador Ctrl+K | Pozos, "Reportes pozo X" y, dentro de un pozo, sus 8 pantallas de configuración. Cada palabra escrita debe aparecer ("reportes prueba"). Muestra 6 por grupo. Reemplaza al panel "Reportes" | `componentes/buscador.html`, `App.initBuscador` en `app.js`, `context_processors.py` |
| Lista de pozos | Tabla con estado, operador, campo, cantidad y fecha del último reporte; filtro por texto y por estado; el más reciente primero | `pozos_list.html`, `pozos_lista.js`, `views.pozos_list_view` |
| Tablero del pozo | Indicadores (último reporte, profundidad, reportes, días de operación), últimos 6 reportes con Excel y "Abrir", avance de la configuración. Botones "Reporte del día" y "Reporte final" | `pozos/main.html`, `views.pozo_main_view` |
| Pantallas de configuración | Una sola lista en `navegacion.py` (`PANTALLAS_INFO_POZO`), que usan la barra de configuración, el buscador y el tablero | `navegacion.py`, `pozos/_nav_info_pozo.html` |
| Celular y tablet (< 900 px) | La barra lateral pasa a un menú inferior; tablas anchas se desplazan dentro de su caja; indicadores en 2 columnas | `layout.css`, `pozos.css` |

**Avance de la configuración:** se mide en 6 pantallas que tienen un "listo" claro (información general completada, y al menos un intervalo, una pérdida, un producto, un benchmark y un tanque). Configuración general y Propiedades de equipo aparecen como "Revisar" porque no tienen un dato que diga si están completas (`navegacion.estado_configuracion`).

**Costo acumulado:** no se muestra en el tablero. Calcularlo exige correr la simulación de inventario completa (`resumen_costos`), demasiado lenta para la pantalla principal.

## Reporte diario (8 pestañas)

- **Colores:** los grises y naranjas escritos a mano en `daily_reports.css`, `reporte_*.css`, `reporte_diario_detalle.html` y `daily_reports_hub.html` pasaron a las variables de `variables.css` (unas 450 apariciones). Así todas las pestañas usan la misma paleta. Excepción: los colores del dibujo del pozo (pestaña 4) quedan en hexadecimal porque van en atributos SVG, donde una variable CSS no funciona.
- **Cabecera:** "Reporte #N" y la fecha en mono, chips del tipo de lodo y unidades, y botón **Excel**. La ruta (Pozos › pozo › Reportes › fecha) va en la barra superior.
- **Pestañas:** botones (`role="tab"`, `aria-selected`) con su número en un recuadro. Quedan fijas debajo de la barra superior al bajar en la página y, si no caben, se desplazan de lado. `switchTab` no cambió: sigue buscando cada pestaña por su clase (`.tab-general`, …).
- **Desplazamiento:** `.subpage` ya no tiene su propia barra de desplazamiento; desplaza la página entera (`.main-wrapper`).
- Se quitaron los emojis de los títulos de sección.
- Pestaña 8 en celular: `.va-grid-2` usa `minmax(0, 1fr)` para que las tablas se desplacen dentro de su caja en vez de ensanchar la pantalla.
- Revisado a 1366 px y 390 px: ninguna de las 8 pestañas desborda la pantalla.

## Inventario y Catálogos

- Cabecera común `.modulo-cabecera` (título, filtros y buscador con ícono SVG) en `inventario.css`; la ubicación va en la barra superior.
- Inventario: filtros Todos / Sólidos / Líquidos como botones segmentados, con su contador en mono. Se mantienen los `id` que usa `inventario.js`.
- Catálogos: pestañas segmentadas con ícono SVG y contador; en celular se desplazan de lado. Se mantienen los `id` que usa `catalogos_maestros.js`.
- Colores de `catalogos_maestros.css` pasados a las variables.

## Caché del navegador

Los CSS y JS de `base.html` (variables, layout, styles, pozos, app.js, pozos_lista.js) llevan `?v={{ version_base }}` (`context_processors.version_base`, que usa `views._version_estaticos`: la fecha de modificación de los archivos). Inventario y Catálogos pasan su propio `version_estaticos` para `inventario.css`. Antes la vista de Inventario no lo pasaba: la dirección quedaba `?v=` vacía y el navegador seguía usando el archivo viejo. Esa fue la causa de la barra lateral colapsada "rota" del 18-oct.

## Selector de pozo (barra superior)

En las pantallas de un pozo, el nombre del pozo en la barra superior es un botón que abre la lista de pozos con buscador (el de reporte más reciente primero, con la fecha del último reporte). Al elegir otro pozo **se abre la misma pantalla de ese pozo** (de Tanques a Tanques); desde un reporte diario se va a los reportes del otro pozo, porque cada reporte es de su pozo. Arriba de la lista está "Tablero de este pozo". Enter abre el primero que coincide; Esc cierra.

- Datos: `context_processors.selector_pozo` (destino y nombre de la pantalla; `DESTINO_AL_CAMBIAR_DE_POZO` para las pantallas que no existen igual en otro pozo).
- Plantilla: `componentes/selector_pozo.html`. `base.html` arma la ubicación por defecto en las pantallas de un pozo (Pozos › selector › pantalla); el reporte diario la sobrescribe para agregar la fecha.
- Comportamiento: `App.initSelectorPozo` en `app.js`. Estilos `.selector-pozo*` en `layout.css`; en celular la lista ocupa el ancho de la pantalla.

## Estilos en línea del reporte (18-oct-2026)

`reporte_diario_detalle.html` tenía 190 estilos en línea. 143 eran estilo visual y pasaron a clases al final de `daily_reports.css`:

- **Con colores propios** (avisos, notas, caudal de bombas, botón de guardar geometría…): clases con el nombre de lo que son (`.aviso-profundidad-mecha`, `.nota-azul`, `.nota-naranja`, `.input-caudal`, `.celda-caudal-bomba`, `.insignia-norma`, `.caja-vacia`, …).
- **Repetidos y simples**: clases utilitarias (`.txt-centro`, `.peso-800`, `.color-secundario`, `.fs-12`, `.mb-12`, `.ancho-50`, `.fila-flex`, …). Llevan `!important` porque reemplazan a un estilo en línea, que tenía prioridad sobre las reglas de cada tabla; sin eso, por ejemplo, `.pumps-table td` cambiaría la alineación de las celdas. `.fila-flex` no lo lleva para no impedir que el JavaScript oculte un elemento.

**Se quedan en línea (47 + 1):** los `style="display:none;"` y el `width:0%` de la barra de avance de la geometría. Son el estado inicial que maneja el JavaScript (paneles, pestañas y modales que abre y cierra con `style.display`). No se pueden pasar a `hidden` ni a una clase: los modales tienen `display: flex` en su clase, que le gana a `hidden`, y una clase con `!important` impediría que el script los abra. La prueba `EstilosEnLineaReporteTests` falla si aparece cualquier otro estilo en línea.

Revisado en el navegador: los elementos visibles en las 8 pestañas tienen el mismo estilo calculado que antes; los modales arrancan cerrados, abren y cierran; sin errores en la consola.

## Fuentes dentro del proyecto (18-oct-2026, con permiso del usuario)

IBM Plex Sans y JetBrains Mono se descargaron de Google Fonts y quedaron en `operaciones/static/operaciones/fonts/` (`ibm-plex-sans-latin.woff2`, `jetbrains-mono-latin.woff2`, 77 KB entre las dos). Son fuentes variables (un archivo cubre todos los grosores), solo el juego latino (acentos y ñ incluidos), con licencia SIL Open Font License 1.1, que permite usarlas y distribuirlas.

- `css/fuentes.css` declara los `@font-face`; `base.html` y `recap_imprimible.html` lo cargan en lugar de pedir las fuentes a internet. El reporte final imprimible pasó de Inter a IBM Plex Sans.
- `chapala.spec` ya empaqueta toda la carpeta `static`, así que el `.exe` las incluye sin cambiar el empaquetado. Hay que **volver a construir el `.exe`** (`Construir EXE.bat`) para que los equipos de los ingenieros las tengan.
- `FuentesSinInternetTests` falla si una plantilla vuelve a pedir fuentes a `fonts.googleapis.com`.

## Pendiente

Nada del rediseño. Ideas para después: tema oscuro (requiere quitar los colores escritos a mano que quedan en las pestañas del reporte).
