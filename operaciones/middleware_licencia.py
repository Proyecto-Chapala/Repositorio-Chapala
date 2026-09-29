"""
================================================================================
MIDDLEWARE DE LICENCIA - PROYECTO CHAPALA
================================================================================
- Sin licencia activa: toda página redirige a /licencia/ y las APIs
  responden 403 en JSON.
- Con licencia activa y pocos días restantes: inserta en toda página HTML
  el aviso pequeño "Versión de prueba vencerá pronto".
"""

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import escape

from . import licencia


class LicenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _exenta(self, ruta):
        exentas = [reverse('licencia_activar'), '/favicon.ico']
        static_url = '/' + settings.STATIC_URL.lstrip('/')
        return ruta.startswith(static_url) or any(ruta.startswith(e) for e in exentas)

    def __call__(self, request):
        if self._exenta(request.path):
            return self.get_response(request)

        info = licencia.estado_licencia()

        if info['estado'] != licencia.ACTIVA:
            if request.path.startswith('/api/') or '/api/' in request.path:
                return JsonResponse(
                    {'error': 'Licencia no activa. Active el sistema para continuar.'},
                    status=403,
                )
            return HttpResponseRedirect(reverse('licencia_activar'))

        response = self.get_response(request)
        if info['aviso']:
            self._insertar_aviso(response, info['dias_restantes'])
        return response

    def _insertar_aviso(self, response, dias):
        if getattr(response, 'streaming', False):
            return
        if 'text/html' not in response.get('Content-Type', ''):
            return
        charset = response.charset or 'utf-8'
        try:
            contenido = response.content.decode(charset)
        except UnicodeDecodeError:
            return
        if '</body>' not in contenido:
            return

        texto_dias = 'Queda 1 día' if dias == 1 else f'Quedan {dias} días'
        aviso = (
            f'<link rel="stylesheet" href="{static("operaciones/css/licencia.css")}">'
            f'<div class="aviso-licencia" role="status">'
            f'<strong>Versión de prueba vencerá pronto</strong>'
            f'<span>{escape(texto_dias)}</span>'
            f'</div></body>'
        )
        contenido = contenido.replace('</body>', aviso, 1)
        response.content = contenido.encode(charset)
        if response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))
