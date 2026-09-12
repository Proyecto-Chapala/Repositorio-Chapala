# Diccionario de datos

Glosario de términos usados en el proyecto — tanto del negocio (perforación e ingeniería de fluidos) como técnicos (Django/base de datos). Pensado para que cualquiera que se sume al proyecto entienda de qué se está hablando sin tener que preguntar.

## Términos del negocio (perforación e ingeniería de fluidos)

**ONE-TRAX** — Software de M-I SWACO que este proyecto replica/estandariza. Genera los reportes diarios de fluidos de un pozo petrolero.

**Mud Report (reporte de lodo)** — El reporte diario que resume el estado del fluido de perforación de un pozo: propiedades, volúmenes, productos usados, equipos, comentarios. Es el documento que todo el sistema busca reproducir digitalmente.

**Pozo** — El pozo petrolero en construcción. Tiene un operador, una ubicación, y se perfora por etapas (intervalos).

**Intervalo** — Tramo del pozo entre dos profundidades, delimitado por el punto donde se baja un revestidor (o por un side track). Cada intervalo tiene su propio sistema de fluido y su propio balance de volumen. Se abre, se opera durante varios días (varios reportes diarios), y se cierra cuando se baja el revestidor correspondiente.

**Sistema de fluido / gama de fluidos** — El tipo de lodo usado en un intervalo: base agua, polimérico, base aceite, o sintético (SBM). Puede cambiar de un intervalo a otro del mismo pozo según el diseño de fluidos del pozo.

**Cierre volumétrico** — El proceso de cerrar un intervalo: se fija la profundidad final, se registra la tubería instalada (revestidor), y se calcula qué queda del volumen — lo que no es fluido recuperable se registra como pérdida "Left in Hole" para que el balance cuadre en cero. El intervalo queda congelado (no editable) después de esto.

**Left in Hole** — Categoría de pérdida de volumen: el lodo que queda atrapado en el hoyo bajo la profundidad de cierre y no se puede recuperar.

**Volume Not Fluids** — El volumen que queda "por debajo" de la profundidad de cierre de un intervalo — es lo que termina registrado como pérdida Left in Hole.

**Side Track** — Procedimiento donde se desvía la perforación desde un punto anterior del pozo (típicamente sobre un tapón de cemento). Se fija el Bit Depth en el tope del tapón, se cierra el intervalo actual, y se abre uno nuevo.

**Bit Depth** — Profundidad de la broca (bit) de perforación en un momento dado — la profundidad "actual" de perforación.

**Revestidor (casing)** — Tubería de acero que se baja y cementa dentro del hoyo perforado, para sostener las paredes y aislar formaciones. Tiene diámetro externo (OD) e interno (ID).

**Liner** — Un tipo de revestidor que no llega hasta la superficie, sino que se cuelga (se ancla) dentro del revestidor anterior.

**Hoyo abierto (open hole)** — La sección del pozo que ya se perforó pero todavía no tiene revestidor instalado.

**Zapata (casing shoe)** — El extremo inferior de un revestidor, donde termina.

**Sarta de perforación / tubería de perforación (drill string / drill pipe)** — La tubería que baja desde la superficie hasta la broca, por dentro del hoyo o del revestidor, y que hace circular el fluido de perforación. Tiene su propio diámetro externo (OD) e interno (ID).

**Diámetro externo (OD)** — En hoyo/revestidor: el borde de lo que se perforó o se metió de hierro (define el "ancho" de la sección). En la tubería de perforación: el diámetro exterior de la sarta.

**Diámetro interno (ID)** — En el revestidor: el espacio libre (drift) por donde pasa la tubería. En la tubería de perforación: el diámetro del canal interno por donde fluye el lodo — el que se usa para calcular capacidad.

**Capacidad interna de tubería** — Volumen que cabe dentro de la tubería de perforación. Fórmula: `(ID² / 1029.4) × longitud` (bbl).

**Volumen anular** — Volumen del espacio entre la tubería de perforación y la pared del hoyo o revestidor. Fórmula: `((ID_hoyo_o_revestidor)² − (OD_tubería)²) / 1029.4 × longitud` (bbl).

**bbl (barril)** — Unidad de volumen usada en la industria petrolera (42 galones estadounidenses).

**Libraje** — Peso total de un producto usado, en libras. Fórmula: `libraje_final = cantidad_unitaria × cantidad de empaques`.

**Gravedad específica** — Densidad relativa de un producto o fluido respecto al agua dulce. Se usa junto al libraje para calcular el volumen que genera un material: `Volumen (bbl) = Libraje Final / (Gravedad Específica × 350)`. El 350 es lb/bbl de agua dulce (8.34 lb/gal × 42 gal/bbl).

**Unit Size** — Formato original (texto libre) en que venía la presentación de un producto en el mud report, ej. `"100. LB BG"` (100 libras, en saco/bolsa). En este proyecto se separó en 3 campos estructurados: cantidad unitaria, unidad de medida, tipo de empaque.

**Presentación** — El texto reconstruido a partir de esos 3 campos (equivalente al Unit Size original), ej. `"100. LB BG"`.

**Daily Used / Cum Used** — Cantidad de un producto usada en el día / acumulada históricamente.

**Daily Cost / Cum. Cost** — Costo del día / acumulado histórico de un producto.

**Start Amt / Final Stock** — Existencia inicial del día (= stock final del día anterior) / existencia al cierre del día. Relación: `Final Stock = Start Amt − Daily Used + Daily Rec'd`.

**Muestra de fluido (Sample From)** — Cada toma de muestra de lodo durante el día (ej. "TK 2 20:00", tanque 2 a las 8pm), con su propio set de valores de propiedades. Un reporte diario puede tener varias.

**Propiedades del lodo (mud properties)** — Mediciones de laboratorio sobre una muestra de lodo: peso del lodo, viscosidad (embudo, plástica), punto cedente (YP), geles, filtrado API/HTHP, pH, cloruros, sólidos, etc. No todas las propiedades aplican a todos los tipos de sistema de fluido — de ahí la "matriz de propiedades selectivas".

**PV (viscosidad plástica) / YP (punto cedente)** — Dos parámetros reológicos clave del lodo, derivados de las lecturas del viscosímetro (R600, R300, etc.).

**Gel (10 seg / 10 min / 30 min)** — Medición de la resistencia del lodo a fluir después de reposar ese tiempo.

**MBT** — Methylene Blue Test — mide la capacidad de intercambio catiónico de las arcillas en el lodo (relacionado con contenido de sólidos activos).

**Equipo** — Maquinaria usada en la operación de fluidos (bombas, zarandas, centrífugas, etc.), con un costo diario que se prorratea según las horas realmente usadas.

## Términos técnicos (Django / base de datos)

**Modelo (model)** — En Django, la definición de una tabla de base de datos como una clase de Python. Cada modelo de este proyecto tiene su propio archivo `models.py` dentro de su app.

**Migración (migration)** — Un archivo que describe un cambio en el esquema de la base de datos (crear tabla, agregar campo, etc.). Django las genera con `makemigrations` y las aplica con `migrate`.

**FK (ForeignKey / llave foránea)** — Un campo que referencia a otra tabla (ej. `Intervalo.pozo` referencia a `Pozo`).

**UUID** — Identificador único universal (ej. `a1b2c3d4-...`), usado como llave primaria en todos los modelos de la app `reportes` (en vez de números autoincrementales).

**`on_delete=PROTECT`** — Regla que impide borrar un registro si todavía tiene otros registros relacionados que dependen de él (ej. no se puede borrar un `Producto` si tiene movimientos de inventario).

**`on_delete=CASCADE`** — Regla que borra automáticamente los registros relacionados cuando se borra el registro principal (ej. borrar un `Intervalo` borra sus `TuberiaInstalada`).

**`clean()` / `full_clean()`** — Métodos de Django donde se implementan las validaciones de negocio de un modelo (ej. "no se puede editar si el intervalo está cerrado").

**`to_dict()`** — Convención usada en este proyecto: cada modelo tiene un método que arma su representación en JSON, para que las vistas la usen al responder a la API.

**API JSON** — Los endpoints (`/api/...`) que el frontend consume para leer y escribir datos, todos respondiendo `{"success": true/false, ...}`.

**SPA (Single Page Application)** — La interfaz web de cada app: una sola página HTML que cambia de contenido con JavaScript (pestañas) sin recargar, consumiendo la API JSON.

**CSRF** — Mecanismo de seguridad de Django contra peticiones falsificadas entre sitios. Los endpoints de este proyecto están marcados `@csrf_exempt` (sin esa protección) — ver la advertencia correspondiente en "Cosas a tener en cuenta.md".

**Admin de Django** — Interfaz automática que Django genera para gestionar los modelos registrados (`/admin/`), útil como respaldo de bajo nivel además de las interfaces web propias del proyecto.
