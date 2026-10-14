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
| 19 | [El inventario usa la cantidad "según ticket"](19_TICKET_SEGUN_GUIA.md) | — (doc 09) | — | Sin probar |

## Antes de empezar

```bash
python manage.py migrate
python manage.py test operaciones
```

Conviene usar un **pozo nuevo**. Los pozos de prueba viejos tienen consumos sin tickets y, con el inventario por pozo, muestran error de línea de tiempo.
