"""
================================================================================
LICENCIA DE PRUEBA - PROYECTO CHAPALA
================================================================================
Lógica pura (sin vistas) de la licencia de prueba:

- Al primer arranque el sistema pide la clave del programador.
- La clave válida activa un período de prueba de DIAS_PRUEBA días.
- Cuando faltan DIAS_AVISO días o menos se muestra el aviso
  "Versión de prueba vencerá pronto".
- Al vencer, el sistema se bloquea. La misma clave NO reactiva la prueba.

El estado se guarda firmado (HMAC) en dos ubicaciones fuera de la carpeta
del programa, para que sobreviva a un reempaquetado y no se pueda editar
a mano la fecha:
    %PROGRAMDATA%\\AOS\\Chapala\\licencia.dat
    %APPDATA%\\AOS\\Chapala\\licencia.dat
Si el reloj de la máquina se atrasa respecto al último uso, se bloquea.

Para cambiar la clave: scripts/generar_clave_licencia.py (NO distribuir).
"""

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ------------------------------------------------------------------------------
# Configuración
# ------------------------------------------------------------------------------
DIAS_PRUEBA = 7
DIAS_AVISO = 2
TOLERANCIA_RELOJ = timedelta(hours=2)

# Hash PBKDF2 de la clave del programador (la clave en texto no está en el código).
_SAL_CLAVE = bytes.fromhex('664e5d6415949d85dc9e1856f5f56128')
_HASH_CLAVE = '4e14b08a648c8130df28017754e3b7c9f33d4b362dc5488b375b81c1864298ec'
_ITERACIONES = 200_000

# Secreto para firmar el archivo de estado.
_SECRETO_FIRMA = b'chapala-aos-licencia-7c1e9b2f5d'

# Estados posibles
ACTIVA = 'activa'
SIN_ACTIVAR = 'sin_activar'
VENCIDA = 'vencida'
ALTERADA = 'alterada'


def _ahora():
    return datetime.now(timezone.utc)


def rutas_estado():
    """Ubicaciones donde se guarda el estado de la licencia."""
    rutas = []
    for var in ('PROGRAMDATA', 'APPDATA'):
        base = os.environ.get(var)
        if base:
            rutas.append(Path(base) / 'AOS' / 'Chapala' / 'licencia.dat')
    if not rutas:  # fuera de Windows (pruebas)
        rutas.append(Path.home() / '.chapala' / 'licencia.dat')
    return rutas


def clave_valida(clave):
    """Compara la clave ingresada contra el hash guardado."""
    clave = (clave or '').strip().upper()
    if not clave:
        return False
    calculado = hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), _SAL_CLAVE, _ITERACIONES).hex()
    return hmac.compare_digest(calculado, _HASH_CLAVE)


# ------------------------------------------------------------------------------
# Serialización firmada
# ------------------------------------------------------------------------------
def _firmar(datos):
    cuerpo = json.dumps(datos, sort_keys=True).encode('utf-8')
    firma = hmac.new(_SECRETO_FIRMA, cuerpo, hashlib.sha256).hexdigest()
    return base64.b64encode(cuerpo).decode('ascii') + '.' + firma


def _verificar(texto):
    """Devuelve el dict si la firma es correcta, None si está alterado."""
    try:
        cuerpo_b64, firma = texto.strip().split('.', 1)
        cuerpo = base64.b64decode(cuerpo_b64)
        esperada = hmac.new(_SECRETO_FIRMA, cuerpo, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(esperada, firma):
            return None
        return json.loads(cuerpo.decode('utf-8'))
    except Exception:
        return None


def _leer_estados():
    """Lee todas las copias. Devuelve (lista_validas, hay_alterada)."""
    validas, alterada = [], False
    for ruta in rutas_estado():
        try:
            if ruta.exists():
                datos = _verificar(ruta.read_text(encoding='utf-8'))
                if datos is None:
                    alterada = True
                else:
                    validas.append(datos)
        except OSError:
            continue
    return validas, alterada


def _guardar(datos):
    texto = _firmar(datos)
    guardado = False
    for ruta in rutas_estado():
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(texto, encoding='utf-8')
            guardado = True
        except OSError:
            continue
    return guardado


# ------------------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------------------
def estado_licencia(ahora=None, registrar_uso=True):
    """
    Devuelve un dict:
        estado: activa | sin_activar | vencida | alterada
        dias_restantes: int (solo si activa)
        vence: datetime | None
        aviso: bool  -> mostrar "vencerá pronto"
    """
    ahora = ahora or _ahora()
    validas, alterada = _leer_estados()

    if alterada:
        return {'estado': ALTERADA, 'dias_restantes': 0, 'vence': None, 'aviso': False}
    if not validas:
        return {'estado': SIN_ACTIVAR, 'dias_restantes': 0, 'vence': None, 'aviso': False}

    # Se toma la activación más antigua y el último uso más reciente de todas las copias.
    activado = min(datetime.fromisoformat(d['activado']) for d in validas)
    ultimo_uso = max(datetime.fromisoformat(d['ultimo_uso']) for d in validas)
    vence = activado + timedelta(days=DIAS_PRUEBA)

    if ahora + TOLERANCIA_RELOJ < ultimo_uso:
        return {'estado': ALTERADA, 'dias_restantes': 0, 'vence': vence, 'aviso': False}
    if ahora >= vence:
        return {'estado': VENCIDA, 'dias_restantes': 0, 'vence': vence, 'aviso': False}

    if registrar_uso and ahora > ultimo_uso:
        _guardar({'activado': activado.isoformat(), 'ultimo_uso': ahora.isoformat()})

    restante = vence - ahora
    dias = restante.days + (1 if restante.seconds or restante.microseconds else 0)
    return {
        'estado': ACTIVA,
        'dias_restantes': dias,
        'vence': vence,
        'aviso': restante <= timedelta(days=DIAS_AVISO),
    }


def activar(clave, ahora=None):
    """
    Activa la prueba con la clave del programador.
    Devuelve (ok, mensaje).
    """
    ahora = ahora or _ahora()
    actual = estado_licencia(ahora, registrar_uso=False)['estado']

    if not clave_valida(clave):
        return False, 'La clave ingresada no es válida.'
    if actual == ACTIVA:
        return True, 'La licencia ya estaba activa.'
    if actual in (VENCIDA, ALTERADA):
        return False, 'El período de prueba ya fue utilizado en este equipo. Contacte al programador.'

    if not _guardar({'activado': ahora.isoformat(), 'ultimo_uso': ahora.isoformat()}):
        return False, 'No se pudo guardar la licencia en este equipo (permisos).'
    return True, f'Versión de prueba activada por {DIAS_PRUEBA} días.'
