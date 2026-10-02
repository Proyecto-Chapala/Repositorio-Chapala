"""
================================================================================
LANZADOR DEL EJECUTABLE - SMART MUD
================================================================================
Punto de entrada de SmartMud.exe (PyInstaller, SIN ventana de consola). Al abrirse:
  1. Usa una base SQLite propia en la carpeta "datos" junto al .exe.
  2. Aplica las migraciones pendientes (siempre, en cada arranque).
  3. La primera vez carga el catálogo de productos y el pozo PRUEBA-001.
  4. Levanta el servidor local, abre el navegador y deja un ícono (gota)
     en la bandeja de Windows, junto al reloj: "Abrir Smart Mud" y "Salir".
  5. Si el sistema ya estaba abierto, solo abre el navegador (no arranca otro).
Todo lo que antes salía en la ventana negra se guarda en datos\\smartmud.log.
Los errores de arranque se muestran en un cuadro de mensaje de Windows.

Modo verificación (lo usa "Construir EXE.bat"):
    SmartMud.exe --verificar      o   python chapala_app.py --verificar
Crea una base temporal, migra, carga datos y abre las pantallas principales.
No toca la carpeta "datos" ni la licencia real. Sale con código 1 si algo falla.
El resultado se escribe en el archivo indicado con --log (o en la consola si hay).
"""

import os
import socket
import sys
import tempfile
import threading
import traceback
import webbrowser
from pathlib import Path

NOMBRE = 'Smart Mud'
CONGELADO = getattr(sys, 'frozen', False)
VERIFICAR = '--verificar' in sys.argv

if CONGELADO:
    CARPETA_APP = Path(sys.executable).resolve().parent
    CARPETA_RECURSOS = Path(getattr(sys, '_MEIPASS', CARPETA_APP))
else:
    CARPETA_APP = Path(__file__).resolve().parent.parent
    CARPETA_RECURSOS = Path(__file__).resolve().parent
    sys.path.insert(0, str(CARPETA_APP))

if VERIFICAR:
    CARPETA_DATOS = Path(tempfile.mkdtemp(prefix='smartmud_verif_'))
else:
    CARPETA_DATOS = CARPETA_APP / 'datos'
# Se conserva el nombre del archivo de la base para no perder los datos de quien ya probó.
BASE_DATOS = CARPETA_DATOS / 'chapala_pruebas.sqlite3'
ARCHIVO_PUERTO = CARPETA_DATOS / 'servidor_en_uso.txt'
ARCHIVO_LOG = CARPETA_DATOS / 'smartmud.log'
LOG_MAXIMO = 5 * 1024 * 1024

os.environ['USE_POSTGRES'] = 'False'
os.environ['CHAPALA_DB_PATH'] = str(BASE_DATOS)
os.environ['DJANGO_SETTINGS_MODULE'] = 'chapala.settings'


# ------------------------------------------------------------------------------
# Salida: sin consola, sys.stdout/sys.stderr son None y cualquier print fallaría.
# ------------------------------------------------------------------------------
def _redirigir_salida(ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.exists() and ruta.stat().st_size > LOG_MAXIMO:
        ruta.unlink()
    archivo = open(ruta, 'a', encoding='utf-8', buffering=1, errors='replace')
    sys.stdout = archivo
    sys.stderr = archivo
    return archivo


def _hay_consola():
    return sys.stdout is not None and sys.stderr is not None


def _mensaje(texto, error=False):
    """Cuadro de mensaje de Windows (sin depender de tkinter)."""
    try:
        import ctypes
        icono = 0x10 if error else 0x40  # MB_ICONERROR / MB_ICONINFORMATION
        ctypes.windll.user32.MessageBoxW(None, texto, NOMBRE, icono)
    except Exception:
        print(texto)


# ------------------------------------------------------------------------------
# Servidor
# ------------------------------------------------------------------------------
def _puerto_libre(inicio=8000, fin=8020):
    for puerto in range(inicio, fin):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', puerto)) != 0:
                return puerto
    return inicio


def _responde(puerto):
    try:
        with socket.create_connection(('127.0.0.1', int(puerto)), timeout=1):
            return True
    except (OSError, ValueError):
        return False


def _instancia_abierta():
    """Puerto de un Smart Mud que ya está corriendo con esta misma carpeta de datos."""
    try:
        puerto = ARCHIVO_PUERTO.read_text(encoding='utf-8').strip()
    except OSError:
        return None
    return int(puerto) if _responde(puerto) else None


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


def _servir(puerto, listo):
    """Servidor HTTP de Django en un hilo (mismo motor que runserver, sin consola)."""
    from django.contrib.staticfiles.handlers import StaticFilesHandler
    from django.core.servers.basehttp import run
    from django.core.wsgi import get_wsgi_application

    aplicacion = StaticFilesHandler(get_wsgi_application())
    try:
        run('127.0.0.1', puerto, aplicacion, threading=True)
    except Exception:
        traceback.print_exc()
    finally:
        listo.set()


# ------------------------------------------------------------------------------
# Ícono de la bandeja
# ------------------------------------------------------------------------------
def _imagen_icono():
    from PIL import Image
    for nombre in ('smartmud.png', 'smartmud.ico'):
        ruta = CARPETA_RECURSOS / nombre
        if ruta.exists():
            return Image.open(ruta)
    return Image.new('RGBA', (64, 64), (34, 40, 49, 255))


def _bandeja(url):
    """Bloquea hasta que el usuario elige "Salir". Devuelve False si no hay pystray."""
    try:
        import pystray
    except Exception:
        traceback.print_exc()
        return False

    def abrir(icono=None, item=None):
        webbrowser.open(url)

    def salir(icono, item=None):
        icono.stop()

    menu = pystray.Menu(
        pystray.MenuItem(f'Abrir {NOMBRE}', abrir, default=True),
        pystray.MenuItem('Salir', salir),
    )
    icono = pystray.Icon('SmartMud', _imagen_icono(), f'{NOMBRE} - {url}', menu)

    def al_iniciar(ic):
        ic.visible = True
        try:
            ic.notify(f'{NOMBRE} está abierto. Para cerrarlo, use el ícono de la gota junto al reloj.', NOMBRE)
        except Exception:
            pass

    icono.run(setup=al_iniciar)
    return True


# ------------------------------------------------------------------------------
# Verificación (Construir EXE.bat)
# ------------------------------------------------------------------------------
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
    print(f'  VERIFICACIÓN DEL PAQUETE {NOMBRE.upper()}' + (' (ejecutable)' if CONGELADO else ' (Python)'))
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
        # El cliente de pruebas no sirve /static/; se usa el mismo buscador que el servidor.
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

    def _bandeja_disponible():
        import pystray  # noqa: F401
        _imagen_icono()
        return 'pystray e ícono presentes'
    paso('Ícono de la bandeja', _bandeja_disponible)

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


# ------------------------------------------------------------------------------
# Arranque normal
# ------------------------------------------------------------------------------
def main():
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)

    abierto = _instancia_abierta()
    if abierto:
        webbrowser.open(f'http://127.0.0.1:{abierto}/')
        return

    if not _hay_consola():
        _redirigir_salida(ARCHIVO_LOG)

    import datetime
    print('=' * 70)
    print(f'  {NOMBRE} - inicio {datetime.datetime.now():%d/%m/%Y %H:%M:%S}')
    print('=' * 70)

    base_nueva = _preparar_base()
    if base_nueva:
        print('Primera ejecución: cargando datos iniciales...')
        _cargar_datos_iniciales()

    puerto = _puerto_libre()
    url = f'http://127.0.0.1:{puerto}/'
    listo = threading.Event()
    hilo = threading.Thread(target=_servir, args=(puerto, listo), daemon=True)
    hilo.start()
    import time
    for _ in range(60):  # hasta 30 s
        if _responde(puerto) or listo.is_set():
            break
        time.sleep(0.5)
    if not _responde(puerto):
        raise RuntimeError(f'El servidor no respondió en el puerto {puerto}.')

    ARCHIVO_PUERTO.write_text(str(puerto), encoding='utf-8')
    print(f'Sistema disponible en {url}')
    webbrowser.open(url)

    try:
        if not _bandeja(url):
            # Sin ícono de bandeja: se queda corriendo hasta que se cierre el proceso.
            print('[AVISO] Sin ícono de bandeja; el sistema queda abierto en segundo plano.')
            hilo.join()
    finally:
        try:
            ARCHIVO_PUERTO.unlink()
        except OSError:
            pass
        print('Sistema cerrado.')


def _opcion(nombre):
    if nombre in sys.argv:
        i = sys.argv.index(nombre)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


if __name__ == '__main__':
    if VERIFICAR:
        ruta_log = _opcion('--log')
        if ruta_log or not _hay_consola():
            _redirigir_salida(ruta_log or (CARPETA_APP / 'verificacion.log'))
        try:
            codigo = verificar()
        except Exception:
            traceback.print_exc()
            codigo = 1
        sys.stdout.flush()
        os._exit(codigo)
    try:
        main()
    except Exception:
        detalle = traceback.format_exc()
        print('\n[ERROR] El sistema no pudo iniciar:')
        print(detalle)
        _mensaje(
            'El sistema no pudo iniciar.\n\n'
            f'{detalle[-900:]}\n'
            f'El detalle completo está en:\n{ARCHIVO_LOG}\n'
            'Envíe ese archivo al programador.',
            error=True,
        )
        os._exit(1)
    os._exit(0)
