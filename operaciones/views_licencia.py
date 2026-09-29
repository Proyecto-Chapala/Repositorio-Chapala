"""
================================================================================
VISTA DE ACTIVACIÓN DE LICENCIA - PROYECTO CHAPALA
================================================================================
"""

from django.shortcuts import redirect, render

from . import licencia


def licencia_activar_view(request):
    info = licencia.estado_licencia(registrar_uso=False)
    mensaje, error = '', False

    if request.method == 'POST':
        ok, mensaje = licencia.activar(request.POST.get('clave', ''))
        if ok:
            return redirect('/')
        error = True
        info = licencia.estado_licencia(registrar_uso=False)
    elif info['estado'] == licencia.ACTIVA:
        return redirect('/')

    return render(request, 'operaciones/licencia/activar.html', {
        'info': info,
        'mensaje': mensaje,
        'error': error,
        'dias_prueba': licencia.DIAS_PRUEBA,
        'bloqueada': info['estado'] in (licencia.VENCIDA, licencia.ALTERADA),
    })
