# 14 — Papelera de pozos

Ver [24](../24_PAPELERA_Y_TIPOS_DE_DATOS.md). Migración **0034**.

## Cómo funciona

"Eliminar pozo" ya no borra nada: el pozo pasa a la papelera y deja de verse en el sistema. Sus reportes quedan intactos. Desde **Pozos › Papelera** se restaura tal como estaba.

## Pasos para verificar

- [ ] Correr `python manage.py migrate` (aplica la 0034).
- [ ] Abrir un pozo con reportes y pulsar **Eliminar pozo**. El aviso dice cuántos reportes diarios tiene y que se puede restaurar.
- [ ] El botón **Enviar a la papelera** queda desactivado hasta escribir el nombre exacto del pozo.
- [ ] Al confirmar, vuelve a la lista de pozos y el pozo ya no aparece. Arriba a la derecha aparece **Papelera (1)**.
- [ ] En la Papelera se ve el pozo con la fecha, el usuario y el número de reportes.
- [ ] Intentar crear un pozo nuevo con el mismo nombre: avisa que hay un pozo con ese nombre en la papelera.
- [ ] Pulsar **Restaurar**: el pozo vuelve a la lista con todos sus reportes, tanques e inventario.
- [ ] En un reporte, módulos opcionales: guardar una muestra con hora `08:30` (se guarda) y otra con `25:00` (avisa que use HH:MM de 00:00 a 23:59).
- [ ] Guardar un evento no programado con costo `1234.567`: se muestra `1234.57`.
