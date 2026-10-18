# 24 — Rediseño técnico de la interfaz (18-oct-2026)

## Cómo funciona

Ver [28](../28_REDISENO_UI_TECNICO.md). La barra lateral y la barra superior son nuevas, la lista de pozos es una tabla y la pantalla del pozo es un tablero. **Ctrl+K** abre un buscador de pozos, reportes y pantallas. En celular aparece un menú abajo.

## Pasos para verificar

Antes: estar en la rama `refactorizacion_ui` y recargar con **Ctrl + F5**.

- [ ] **Pozos:** se ve una tabla ordenada por el último reporte. Filtrar escribiendo y con los botones Todos / Activos / En creación / Cerrados. Al pulsar una fila se abre el pozo.
- [ ] **Tablero del pozo:** muestra el último reporte, la profundidad, los reportes y los días de operación. Los últimos reportes tienen botón de Excel y "Abrir".
- [ ] **Configuración del pozo** (en el tablero): cada pantalla dice Lista, Pendiente o Revisar, y abre la pantalla al pulsarla. El contador (por ejemplo 2/6) coincide.
- [ ] **Reporte del día** abre la pantalla de reportes del pozo; **Reporte final** abre el recap.
- [ ] **Ctrl + K** desde cualquier pantalla: escribir "reportes" más parte del nombre del pozo; Enter abre sus reportes. Dentro de un pozo, escribir "tanques" abre esa pantalla. Esc cierra.
- [ ] El botón **Reportes** de la barra lateral abre el buscador con "reportes " ya escrito.
- [ ] **Colapsar** la barra lateral: quedan solo los íconos, y al recargar sigue colapsada.
- [ ] **Celular** (o ventana angosta): aparece el menú inferior con Pozos, Reportes, Inventario y Catálogos. Ninguna pantalla se corta; las tablas anchas se desplazan de lado dentro de su caja.
- [ ] Recorrer Inventario, Catálogos, las 8 pantallas de configuración y un reporte diario: todo sigue funcionando igual, solo cambian colores, fuentes y barras.
- [ ] **Eliminar pozo** sigue al final del tablero y pide escribir el nombre.
