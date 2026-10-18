# 28 — Rediseño de la interfaz: estilo técnico (rama `refactorizacion_ui`, 18-oct-2026)

Pedido del usuario: la interfaz se veía genérica, no era adaptable al celular y para llegar a los reportes había que dar muchos clics. Se armó un prototipo interactivo, el usuario eligió el estilo "más técnico" y se aplicó en la rama `refactorizacion_ui`.

## Decisiones

- **Estilo técnico**: gris pizarra, barra lateral casi negra, números y nombres de pozo en letra monoespaciada (JetBrains Mono), textos en IBM Plex Sans. Sin internet se usan Segoe UI y Consolas.
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

## Pendiente (siguientes partes)

- Pasar al estilo nuevo las 8 pestañas del reporte diario, Inventario y Catálogos (hoy heredan colores y fuentes, pero conservan su maquetación).
- Selector de pozo en la barra superior para cambiar de pozo sin volver a la lista.
- Guardar las fuentes dentro del proyecto para que el `.exe` las tenga sin internet (hay que bajar los archivos; pedir permiso antes).
- Que el navegador tome los CSS/JS nuevos sin Ctrl+F5 (versión en la URL de los estáticos).
