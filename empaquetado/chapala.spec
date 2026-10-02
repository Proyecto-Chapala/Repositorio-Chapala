# -*- mode: python ; coding: utf-8 -*-
# ==============================================================================
# SPEC DE PYINSTALLER - SmartMud.exe (modo carpeta, SIN ventana de consola)
# Se ejecuta desde "Construir EXE.bat"; no correr a mano desde otra carpeta.
# ==============================================================================
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

RAIZ = os.path.abspath(os.path.join(SPECPATH, '..'))
sys.path.insert(0, RAIZ)
os.environ['DJANGO_SETTINGS_MODULE'] = 'chapala.settings'
os.environ['USE_POSTGRES'] = 'False'

ICONO = os.path.join(SPECPATH, 'smartmud.ico')

datas = [
    (os.path.join(RAIZ, 'operaciones', 'templates'), 'operaciones/templates'),
    (os.path.join(RAIZ, 'operaciones', 'static'), 'operaciones/static'),
    (os.path.join(RAIZ, 'operaciones', 'plantillas'), 'operaciones/plantillas'),
    # Ícono de la bandeja de Windows (gota)
    (os.path.join(SPECPATH, 'smartmud.png'), '.'),
    (ICONO, '.'),
]
datas += collect_data_files('django')
datas += collect_data_files('openpyxl')

hiddenimports = (
    collect_submodules('django')
    + collect_submodules('operaciones')
    + collect_submodules('chapala')
    + collect_submodules('pystray')
    + ['seed_data', 'openpyxl', 'pypdf', 'sqlparse', 'asgiref', 'tzdata',
       'PIL.Image', 'PIL.ImageDraw']
)

a = Analysis(
    [os.path.join(SPECPATH, 'chapala_app.py')],
    pathex=[RAIZ],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    # No incluir herramientas del programador ni PostgreSQL en el paquete
    excludes=['scripts', 'scripts.generar_clave_licencia', 'psycopg2', 'tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SmartMud',
    icon=ICONO,
    debug=False,
    strip=False,
    upx=False,
    console=False,   # sin ventana negra: el sistema vive en el ícono de la bandeja
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='SmartMud',
)
