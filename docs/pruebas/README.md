# Pruebas en pantalla

Un archivo por cambio aplicado. Cada uno explica **cómo funciona** y trae los **pasos para verificar**, con el resultado esperado. Las casillas se marcan al probar (`[x]`), y si algo falla se anota debajo del paso.

Las pruebas automáticas (`python manage.py test operaciones`) cubren los cálculos. Las de esta carpeta son las que hace una persona en la pantalla.

| N° | Cambio | Punto del doc 23 | Migración | Estado |
|---|---|---|---|---|
| 01 | [Inventario por pozo](01_INVENTARIO_POR_POZO.md) | 1, 2, 3, 4 | 0028 | Sin probar |
| 02 | [Gravedad específica](02_GRAVEDAD_ESPECIFICA.md) | 7 | — | Sin probar |
| 03 | [Precio por unidad o por barril](03_PRECIO_POR_BARRIL.md) | 8 | 0029 | Sin probar |
| 04 | [Número de ticket en el inventario](04_NUMERO_TICKET.md) | 5 | — | Sin probar |
| 05 | [Categoría Trailer](05_TRAILER.md) | 18 (y 17) | — | Sin probar |
| 06 | [Tarifas en dos monedas](06_TARIFAS_DOS_MONEDAS.md) | 9 | 0031 | Sin probar |
| 07 | [El balance cierra en 0](07_BALANCE_CIERRA.md) | 10 | — | Sin probar |
| 08 | [Editar y eliminar movimientos](08_EDITAR_MOVIMIENTOS.md) | 11 (y 1) | — | Sin probar |
| 09 | [Recepción y envío de fluido](09_FLUIDO_OTROS_POZOS.md) | 12 | — | Sin probar |
| 10 | [Cerrar un intervalo como side track](10_CERRAR_SIDETRACK.md) | 14 | — | Sin probar |
| 11 | [Dejar volumen en el hoyo](11_DEJAR_EN_HOYO.md) | 13 | — | Sin probar |
| 12 | [Propiedades extra que aparecen](12_PROPIEDADES_EXTRA.md) | 15 | — | Sin probar |
| 13 | [Reportito: comentario y Excel](13_REPORTITO.md) | 16 | 0032 | Sin probar |
| 14 | [Papelera de pozos](14_PAPELERA_POZOS.md) | — (doc 24) | 0034 | Sin probar |
| 15 | [Servicios del pozo](15_SERVICIOS_DEL_POZO.md) | — (doc 25) | 0035 | Sin probar |
| 16 | [Lodo reciclado solo como volumen](16_LODO_RECICLADO_SOLO_VOLUMEN.md) | — (doc 26) | — | Sin probar |
| 17 | [Acumulados por columna en el inventario](17_ACUMULADOS_INVENTARIO.md) | — (doc 26) | — | Sin probar |
| 18 | [Inventario de consumo separado del balance](18_INVENTARIO_DE_CONSUMO.md) | — (doc 26) | 0036 | Sin probar |
| 19 | [Dotación por tickets y recibido/devuelto manual](19_INVENTARIO_TICKETS_Y_MANUAL.md) | — (doc 09, 23) | 0037 | Sin probar |
| 20 | [Correcciones de lógica en reportes diarios](20_CORRECCIONES_LOGICA_REPORTES.md) | — (doc 16 C1, C2, C4, C5, C6, C9) | 0038 | Sin probar |
| 21 | [Volumen calculado en el Excel, tickets como recibido y pérdidas del sistema activo](21_VOLUMEN_CALCULADO_TICKETS_PERDIDAS.md) | — (doc 27) | — | Sin probar |
| 22 | [Barra de navegación de Información del Pozo](22_BARRA_INFORMACION_POZO.md) | [05](../05_CONFIGURACION_POZO.md) | — | Sin probar |
| 23 | [Panel "Reportes" en la barra lateral](23_MENU_REPORTES_BARRA_LATERAL.md) | [06](../06_REPORTE_DIARIO_PESTANAS_1_A_5.md) | — | Reemplazado por 24 |
| 24 | [Rediseño técnico de la interfaz](24_REDISENO_UI_TECNICO.md) | [28](../28_REDISENO_UI_TECNICO.md) | — | Sin probar |
| 25 | [Cerrar y reabrir pozo](25_CERRAR_Y_REABRIR_POZO.md) | — (doc 29) | — | Sin probar |
| 26 | [Modificar pozo](26_MODIFICAR_POZO.md) | — (doc 30) | — | Sin probar |
| 27 | [Eliminar reporte diario LIFO](27_ELIMINAR_REPORTE_LIFO.md) | — (doc 16 C10) | — | Sin probar |
| 28 | [Protección de intervalos de revestimiento](28_PROTECCION_INTERVALOS.md) | — (doc 05) | — | Sin probar |
| 29 | [Blindaje de pozo cerrado](29_BLINDAJE_POZO_CERRADO.md) | — (doc 29) | — | Sin probar |
| 30 | [Validación de fecha de reportes vs. Spud Date](30_VALIDACION_FECHA_SPUD_REPORTE.md) | — (doc 06) | — | Sin probar |
| 31 | [Sincronización Spud Date y Well Header Information](31_SINCRONIZACION_SPUD_DATE_WELL_HEADER.md) | — (doc 05, 06) | — | Sin probar |
| 32 | [Integridad de datos geológicos y perforación](32_INTEGRIDAD_DATOS_GEOLOGICOS_PERFORACION.md) | — (doc 06) | — | Sin probar |
| 33 | [Restauración de papelera, cierre e integridad de propiedades de lodo](33_RESTAURAR_PAPELERA_Y_PROPIEDADES_LODO.md) | — (doc 24, 06) | — | Sin probar |
| 34 | [Integridad de geometría de sarta y propiedades extra](34_GEOMETRIA_SARTA_Y_PROPIEDADES_EXTRA.md) | — (doc 06) | — | Sin probar |
| 35 | [Integridad en tanques, volumetría y listas activas](35_FOSAS_Y_VOLUMETRIA_INTEGRIDAD.md) | — (doc 05, 09) | — | Sin probar |
| 36 | [Integridad en catálogos maestros y componentes de sarta](36_CATALOGOS_MAESTROS_Y_COMPONENTES_SARTA.md) | — (doc 05, 06) | — | Sin probar |
| 37 | [Integridad en control de sólidos y módulos opcionales](37_CONTROL_SOLIDOS_Y_MODULOS_OPCIONALES.md) | — (doc 07, 08) | — | Sin probar |
| 38 | [Integridad en hidráulica, distribución de tiempo y reportes diarios](38_HIDRAULICA_Y_TIEMPO_INTEGRIDAD.md) | — (doc 06, 10) | — | Sin probar |
| 39 | [Blindaje del Reporte Final (Recap) y simetría 100% en Views](39_RECAP_Y_SIMETRIA_VIEWS.md) | — (doc 29) | — | Sin probar |
| 40 | [Productos usados en reporte de lodo, hoja única de inventario y rediseño visual en Excel](40_EXCEL_INVENTARIO_Y_PRODUCTOS_USADOS.md) | — (doc 14) | — | Sin probar |
| 41 | [Ajuste predeterminado de impresión en hoja tamaño Carta (Letter) para reportes de Excel](41_AJUSTE_IMPRESION_CARTA_EXCEL.md) | — (doc 14) | — | Sin probar |

## Antes de empezar

```bash
python manage.py migrate
python manage.py test operaciones
```

Conviene usar un **pozo nuevo**. Los pozos de prueba viejos tienen consumos sin tickets y, con el inventario por pozo, muestran error de línea de tiempo.
