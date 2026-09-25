================================================================================
LISTA DE ERRORES O POSIBLES BUGS EN PROYECTO CHAPALA 
================================================================================
Fecha de Actualización: 24 de Septiembre de 2026
Entorno: Django / Python 3.14 / PostgreSQL / JavaScript Vanilla / CSS3
================================================================================

1. MARCA Y MODELO EN LA PESTAÑA DE BOMBAS EN EL REPORTE DIARIO

Por ahora aparecen 4 bombas pero el campo te da como la opción de seleccionar como si tuvieras mas bombas almacenadas, sin embargo puedes cambiarles el nombre y se guardan, pero al darle a esa selección únicamente te saldrá la que ya este escrita en el campo.


2. POSIBLE PROBLEMA DE INVENTARIO 

Parece haber un inventario diferente al que se utiliza durante la pestaña 8 del reporte diario. si uno quiere utilizar algún producto la cantidad de este aparecerá en 0, mientras que en la pestaña del inventario aparece que hay MUCHAS unidades (por lo menos en mi equipo) asi que sospecho que puedan haber dos diferentes conviviendo en el código. En esta parte para ser específicos, En la pestaña de inventario del programa aparecen con una gran cantidad de existencia de los mismos, mientras que durante la parte de inventario e hidráulica allí por mucho que aparezcan los mismos productos estos aparecen sin cantidad, por lo tanto no te deja utilizarlos. eso tomando en cuenta que podría ser un error durante la carga de estos productos en la pestaña de Productos / Equipos / Mallas Activas, asi que revisar esas pestañas. Debido a esto no se puede utilizar correctamente la pestaña 8 del reporte diario.


3. Revisar las pestañas de reportes
Durante la generación de reportes, noté que en algunas plantillas en excel al bajar estas se repetían pero sin datos. Sospecho que podría ser en caso de tener otros pozos activos pero sin nada. Se debería revisar eso en caso de que los reportes se creen asi para poder generarlos específicamente por el dia que se trabajen en especifico.

