# 07 — El balance de volumetría cierra en 0

**Punto del doc 23:** 10 · **Migración:** ninguna · **Estado:** sin probar · **Requiere:** pruebas [01](01_INVENTARIO_POR_POZO.md) y [02](02_GRAVEDAD_ESPECIFICA.md)

## Cómo funciona

- Para cada grupo (activo, reserva, premezcla):
  `final calculado = inicial + fluido base + agua + químicos + lodo reciclado − devuelto + transferido desde otros grupos − transferido a otros grupos − pérdidas`.
  `No contabilizado = real medido − final calculado`, y al cierre del día tiene que ser **0**.
- El sistema activo incluye el **hoyo**. Al perforar, el fluido pasa de los tanques al hoyo y el total no cambia.
- **Causa de la diferencia que vio el cliente** ("no puede dar 1.003, tiene que dar 1.000"): el *Volumen de químicos agregados* salía en 0, por la falta de GE y el bloqueo del inventario. El material sí ocupaba volumen en los tanques, pero el balance no lo registraba. Las dos causas quedaron corregidas en las pruebas 01 y 02.
- Se revisó el cálculo completo: cada movimiento aparece en una fila del balance y las filas suman exactamente el calculado. Lo cubren pruebas automáticas (`test_balance_volumetria.py`).
- Si después de esto queda una diferencia, es **real**: fluido que se perdió y no se registró. Se explica cargando la pérdida correspondiente. Que el ingeniero pueda ajustar a mano esos valores es el punto 11.

## Pasos para verificar

Preparación: pozo nuevo con un tanque activo y BARITA activa (LBS, 100, GE 4,2), con ticket de entrada.

- [ ] **Día 1.** *Agregar químicos* con 1.000 bbl de agua en el tanque activo, real = 1.000 → *No contabilizado* = **0** (en verde).
- [ ] **Químicos.** Día 2: *Agregar químicos* con 30 sacos de barita → *Volumen de químicos agregados* ≈ **2,0 bbl**. *Final calculado* ≈ 1.002,0.
- [ ] **Cierre.** Real del día 2 = 1.002 → *No contabilizado* ≈ 0. Solo queda la fracción decimal, que se ve si se escribe 1.002,04.
- [ ] **Filas que suman.** En la tabla del balance, sumar a mano *Volumen inicial* + las filas de movimientos → da el *Volumen final calculado* en cada columna (activo, reserva, premezcla, total).
- [ ] **Hoyo.** Día 3: más profundidad en la pestaña 4 (el hoyo crece unos 30 bbl) y el real del tanque baja 30 → *No contabilizado* = 0.
- [ ] **Transferencia entre grupos.** Transferir 50 bbl de reserva al activo → aparece en "Transferido a otros grupos" (reserva) y en "Transferido desde otros grupos" (activo), y el total no cambia.
- [ ] **Diferencia real.** Escribir un real 10 bbl menor que el calculado → *No contabilizado* = −10 en rojo ("Falta fluido real"). Cargar una pérdida de 10 bbl → vuelve a 0.
- [ ] **Datos del cliente.** Repetir el caso que dio 1.003 en la revisión con los mismos datos → ahora debe cerrar.

**Notas de la prueba:**
