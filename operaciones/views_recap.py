"""
Reporte final del pozo (recap): pantalla para escribir conclusiones y elegir qué descargar,
descarga en Excel y página imprimible (PDF desde el navegador). Ver recap_pozo.py.
"""

from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Pozo
from .models_recap import RecapPozo
from .recap_pozo import SECCIONES, datos_recap, generar_recap_excel

LIMITE_TEXTO = 20000


def _hasta(request):
    texto = (request.GET.get('hasta') or '').strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, '%Y-%m-%d').date()
    except ValueError:
        return None


def _secciones(request):
    elegidas = [s for s in request.GET.getlist('s') if s in SECCIONES]
    return elegidas or list(SECCIONES)


def recap_view(request, pk):
    """Pantalla del reporte final: textos del ingeniero + opciones de descarga."""
    from .views import _version_estaticos
    pozo = get_object_or_404(Pozo, pk=pk)
    recap, _ = RecapPozo.objects.get_or_create(pozo=pozo)

    if request.method == 'POST':
        for campo in ('resumen', 'conclusiones', 'recomendaciones', 'lecciones'):
            setattr(recap, campo, (request.POST.get(campo) or '').strip()[:LIMITE_TEXTO])
        recap.save()
        return redirect(reverse('operaciones:recap_pozo', args=[pozo.pk]) + '?guardado=1')

    primero = pozo.reportes_diarios.order_by('fecha').first()
    ultimo = pozo.reportes_diarios.order_by('-fecha').first()
    return render(request, 'operaciones/pozos/recap.html', {
        'pozo': pozo, 'recap': recap, 'secciones': SECCIONES,
        'primero': primero, 'ultimo': ultimo,
        'total_reportes': pozo.reportes_diarios.count(),
        'guardado': request.GET.get('guardado') == '1',
        'version_estaticos': _version_estaticos('operaciones/css/recap.css'),
    })


def recap_excel_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    d = datos_recap(pozo, _hasta(request))
    contenido, nombre = generar_recap_excel(d, _secciones(request))
    respuesta = HttpResponse(contenido, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return respuesta


def recap_imprimible_view(request, pk):
    """Página imprimible del reporte final: el navegador la guarda como PDF."""
    from .views import _version_estaticos
    pozo = get_object_or_404(Pozo, pk=pk)
    d = datos_recap(pozo, _hasta(request))
    d['secciones'] = _secciones(request)
    d['titulos'] = SECCIONES
    d['version_estaticos'] = _version_estaticos('operaciones/css/recap.css')
    return render(request, 'operaciones/pozos/recap_imprimible.html', d)
