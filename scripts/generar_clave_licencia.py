"""
Genera el hash de una nueva clave de programador para operaciones/licencia.py.
USO (solo el programador, NO incluir en el paquete que se entrega):
    python scripts/generar_clave_licencia.py MI-CLAVE-NUEVA
Luego copiar _SAL_CLAVE y _HASH_CLAVE en operaciones/licencia.py.
"""
import hashlib
import secrets
import sys

if len(sys.argv) != 2:
    print('Uso: python scripts/generar_clave_licencia.py CLAVE')
    sys.exit(1)

clave = sys.argv[1].strip().upper()
sal = secrets.token_hex(16)
hash_clave = hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), bytes.fromhex(sal), 200_000).hex()
print(f"_SAL_CLAVE = bytes.fromhex('{sal}')")
print(f"_HASH_CLAVE = '{hash_clave}'")
