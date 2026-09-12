# Cosas a tener en cuenta

Advertencias, limitaciones y decisiones de diseño que conviene no perder de vista.

## Alerta de calidad de datos: gravedad específica de líquidos (CHAPALA)

`Producto.gravedad_especifica` de los productos líquidos `AOS-LIQ-01` y `AOS-LIQ-02` en `mychapala` contiene texto como `"11.0 LPG"` — eso es **densidad en lb/gal (ppg)**, no una gravedad específica adimensional real. Si se usa tal cual en la fórmula de volumen (`Libraje Final / (Gravedad Específica × 350)`), el resultado sale mal. No se corrigió todavía porque no se ha llegado a implementar el cálculo de volumen (Misión 5) — hay que resolverlo antes de esa implementación.

## Este entorno de trabajo no tiene acceso a PyPI

Las migraciones que agregan modelos nuevos en `reportes` no se pueden generar automáticamente desde esta sesión (el proxy de red bloquea `pypi.org`, así que no se puede instalar Django aquí para correr `makemigrations`). Por eso:

- Migraciones con **pocos modelos simples y sin dependencias complejas** (ej. `0002_equipo_comentario.py`) se escriben a mano, cuidando que coincidan exactamente con los campos de `models.py`.
- Migraciones con **muchos modelos interdependientes** (la inicial de `reportes`, con 13 modelos) las genera el propio usuario en su máquina real con `makemigrations`, porque es mucho más seguro que Django la autogenere contra el entorno real que escribirla a mano.
- Cada vez que se agrega un campo o modelo nuevo, el usuario tiene que correr `python manage.py migrate` él mismo — nunca queda aplicado automáticamente desde esta sesión.

## Dos modelos `Producto` distintos, sin relación entre sí

`mychapala.Producto` (esquema plano, ID entero) y `reportes.Producto` (esquema ONE-TRAX, UUID) son tablas completamente independientes, aunque tengan el mismo nombre y campos parecidos (`cantidad_unitaria`, `unidad_medida`, `tipo_empaque`). Cargar un producto en uno no lo crea en el otro. Si en algún momento se decide unificarlos, hay que migrar datos explícitamente — no ocurre solo.

## El costo y el volumen siempre salen de una fórmula, nunca se guardan a mano

Regla de negocio confirmada desde el inicio del proyecto (sección 5 del contexto original) y aplicada consistentemente:

- `UsoMaterial.subtotal_costo = cantidad_usada × precio_unitario`
- `UsoEquipo.subtotal_costo = costo_diario × horas_usadas / 24`
- `Producto.libraje(cantidad) = cantidad_unitaria × cantidad`

Ninguno de estos son columnas editables — son propiedades calculadas en el modelo. Si en el futuro se agrega un campo de "costo total" o "volumen" en algún formulario, debe seguir el mismo patrón (fórmula, no campo libre).

## El bloqueo por intervalo cerrado vive en los modelos, no solo en las vistas

Cada modelo que depende de un `Intervalo` (`ReporteDiario`, `MuestraFluido`, `PropiedadValor`, `InventarioItem`, `UsoMaterial`, `UsoEquipo`, `Comentario`) valida en su propio `clean()`/`save()` que el intervalo no esté cerrado. Esto es intencional: así la regla se respeta también si alguien edita datos desde el admin de Django, no solo desde la interfaz web. Si se agrega un modelo nuevo que cuelgue de `ReporteDiario` o `Intervalo`, hay que replicar esa misma validación.

## APIs sin autenticación todavía

Tanto `mychapala` como `reportes` exponen sus endpoints con `@csrf_exempt` y sin ningún control de acceso — cualquiera que llegue a la URL puede leer y escribir datos. Aceptable mientras el sistema no esté expuesto a producción real ni a internet, pero es lo primero que hay que resolver antes de ese paso (ver "Próximos pasos a seguir.md").

## Unidades de trabajo: inglesas

Todo el sistema trabaja en unidades inglesas (ft, in, bbl, lb), consistente con el mud report de referencia. No mezclar con métrico en ningún campo nuevo sin conversión explícita.

## La geometría del pozo es una demo, no la lógica final

La pestaña "Geometría del Pozo" (`geometria.js`) es intencionalmente un módulo aislado que no lee de la base de datos: usa valores por defecto y los recalcula en el navegador. No reemplaza ni valida datos reales de `Intervalo`/`TuberiaInstalada`. Antes de considerarla "funcional" para uso real hay que conectarla a la API y extenderla a múltiples revestidores apilados (ver "Próximos pasos a seguir.md").

## Convención de diámetros (aclarada por el usuario)

Para evitar confusión al leer los modelos o la interfaz:

- **Diámetro externo (OD)** de hoyo o revestidor = el borde de lo que se perforó o se metió de hierro. Define el ancho de la sección en el dibujo de geometría.
- **Diámetro interno (ID)** de la sarta de perforación (tubería) = el del taladro/tubería que va adentro del hoyo o revestidor. Es el que se usa en las fórmulas de capacidad interna y volumen anular.
- El revestidor también tiene su propio ID (el "drift", el espacio libre por donde pasa la tubería) — no confundir con el ID de la tubería.

## Conexión intermitente con la máquina del usuario

Durante el desarrollo, la conexión de esta sesión con la computadora del usuario se cae y se restablece sola ocasionalmente (normal en este tipo de sesión remota). Cuando eso pasa, los archivos generados quedan disponibles en la conversación para descarga manual mientras se reintenta la escritura automática.
