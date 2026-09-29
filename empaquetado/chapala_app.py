"""
================================================================================
LANZADOR DEL EJECUTABLE DE PRUEBAS - PROYECTO CHAPALA
================================================================================
Punto de entrada de CHAPALA.exe (PyInstaller). Al ejecutarse:
  1. Usa una base SQLite propia en la carpeta "datos" junto al .exe.
  2. Aplica las migraciones pendientes (siempre, en cada arranque).
  3. La primera vez carga el catálogo de productos y el pozo PRUEBA-001.
  4. Levanta el servidor local y abre el navegador.
Cerrar la ventana negra detiene el sistema.

Modo verificación (lo usa "Construir EXE.bat"):
    CHAPALA.exe --verificar      o   python chapala_app.py --verificar
Crea una base temporal, migra, carga datos y abre las pantallas principales.
No toca la carpeta "datos" ni la licencia real. Sale con código 1 si algo falla.
"""

import os
import socket
import sys
import tempfile
import threading
import traceback
import webbrowser
from pathlib import Path

CONGELADO = getattr(sys, 'frozen', False)
VERIFICAR = '--verificar' in sys.argv

if CONGELADO:
    CARPETA_APP = Path(sys.executable).resolve().parent
else:
    CARPETA_APP = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(CARPETA_APP))

if VERIFICAR:
    CARPETA_DATOS = Path(tempfile.mkdtemp(prefix='chapala_verif_'))
else:
    CARPETA_DATOS = CARPETA_APP / 'datos'
BASE_DATOS = CARPETA_DATOS / 'chapala_pruebas.sqlite3'

os.environ['USE_POSTGRES'] = 'False'
os.environ['CHAPALA_DB_PATH'] = str(BASE_DATOS)
os.environ['DJANGO_SETTINGS_MODULE'] = 'chapala.settings'


def _puerto_libre(inicio=8000, fin=8020):
    for puerto in range(inicio, fin):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', puerto)) != 0:
                return puerto
    return inicio


def _cargar_datos_iniciales(estricto=False):
    from django.core.management import call_command
    try:
        import seed_data
        seed_data.seed_database()
    except Exception:
        if estricto:
            raise
        print('[AVISO] No se pudo cargar el catálogo de productos:')
        traceback.print_exc()
    try:
        call_command('seed_pozo_prueba')
    except Exception:
        if estricto:
            raise
        print('[AVISO] No se pudo crear el pozo de prueba PRUEBA-001:')
        traceback.print_exc()


def _preparar_base():
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    base_nueva = not BASE_DATOS.exists()

    import django
    django.setup()
    from django.core.management import call_command

    print('Preparando base de datos...')
    call_command('migrate', interactive=False, verbosity=0)
    return base_nueva


def verificar():
    """Prueba de humo completa. Devuelve 0 si todo bien, 1 si algo falla."""
    fallos = []

    def paso(nombre, funcion):
        try:
            resultado = funcion()
            print(f'  [OK]    {nombre}' + (f' ({resultado})' if resultado else ''))
        except Exception as exc:
            fallos.append(nombre)
            print(f'  [FALLA] {nombre}: {exc}')
            traceback.print_exc()

    print('=' * 70)
    print('  VERIFICACIÓN DEL PAQUETE CHAPALA' + (' (ejecutable)' if CONGELADO else ' (Python)'))
    print(f'  Base temporal: {BASE_DATOS}')
    print('=' * 70)

    paso('Migraciones sobre SQLite nueva', lambda: _preparar_base() and None)
    if fallos:
        return 1

    from django.core.management import call_command
    paso('Chequeo del sistema (manage.py check)', lambda: call_command('check') or None)
    paso('Carga de productos y pozo PRUEBA-001', lambda: _cargar_datos_iniciales(estricto=True))

    def _conteos():
        from operaciones.models import Pozo, Producto
        np, nz = Producto.objects.count(), Pozo.objects.count()
        if np == 0 or nz == 0:
            raise RuntimeError(f'productos={np}, pozos={nz}')
        return f'{np} productos, {nz} pozo(s)'
    paso('Datos cargados', _conteos)

    def _archivos():
        from operaciones import reporte_excel
        faltan = [p for p in (reporte_excel.PLANTILLA,) if not os.path.exists(p)]
        if faltan:
            raise FileNotFoundError(', '.join(faltan))
        return 'plantilla Excel presente'
    paso('Archivos del reporte Excel', _archivos)

    def _estaticos_y_plantillas():
        # El cliente de pruebas no sirve /static/; se usa el mismo buscador que runserver.
        from django.contrib.staticfiles import finders
        from django.template.loader import get_template
        estaticos = ['operaciones/css/licencia.css', 'operaciones/css/styles.css',
                     'operaciones/js/app.js']
        faltan = [e for e in estaticos if not finders.find(e)]
        if faltan:
            raise FileNotFoundError('estáticos: ' + ', '.join(faltan))
        get_template('operaciones/licencia/activar.html')
        get_template('operaciones/base.html')
        return f'{len(estaticos)} estáticos y 2 plantillas'
    paso('Archivos estáticos y plantillas', _estaticos_y_plantillas)

    # Pantallas: se simula licencia activa solo dentro de este proceso.
    from operaciones import licencia
    licencia.estado_licencia = lambda *a, **k: {
        'estado': licencia.ACTIVA, 'dias_restantes': 7, 'vence': None, 'aviso': True}

    from django.test import Client
    from operaciones.models import Pozo
    cliente = Client()
    rutas = ['/', '/pozos/', '/api/productos/']
    pozo = Pozo.objects.first()
    if pozo:
        rutas.append(f'/pozos/{pozo.pk}/')

    for ruta in rutas:
        def _get(ruta=ruta):
            r = cliente.get(ruta)
            if r.status_code >= 400:
                raise RuntimeError(f'HTTP {r.status_code}')
            return f'HTTP {r.status_code}'
        paso(f'Pantalla {ruta}', _get)

    print('=' * 70)
    if fallos:
        print(f'  RESULTADO: {len(fallos)} FALLA(S) -> {", ".join(fallos)}')
        return 1
    print('  RESULTADO: TODO CORRECTO')
    return 0


def main():
    print('=' * 70)
    print('  CHAPALA - Sistema de Operaciones (versión de prueba)')
    print('  NO cierre esta ventana mientras usa el sistema.')
    print('=' * 70)

    base_nueva = _preparar_base()
    from django.core.management import call_command

    if base_nueva:
        print('Primera ejecución: cargando datos iniciales...')
        _cargar_datos_iniciales()

    puerto = _puerto_libre()
    url = f'http://127.0.0.1:{puerto}/'
    print(f'\nSistema disponible en {url}')
    print('Para salir, cierre esta ventana.\n')
    threading.Timer(2.0, lambda: webbrowser.open(url)).start()

    call_command(
        'runserver', f'127.0.0.1:{puerto}',
        use_reloader=False, insecure_serving=True,
    )


if __name__ == '__main__':
    if VERIFICAR:
        try:
            codigo = verificar()
        except Exception:
            traceback.print_exc()
            codigo = 1
        sys.exit(codigo)
    try:
        main()
    except Exception:
        print('\n[ERROR] El sistema no pudo iniciar:')
        traceback.print_exc()
        input('\nPresione Enter para cerrar...')
