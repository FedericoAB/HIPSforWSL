import hashlib
import os
import sys
import subprocess
import re
from collections import defaultdict
UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO

from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

# Archivos a verificar
archivos = ['/etc/passwd', '/etc/shadow']
# Archivo donde guardaremos los hashes
hash_file = PATHS['hash'] 


def calcular_hash(ruta):
    try:
        # Usar sudo para archivos del sistema si es necesario
        if '/etc/' in ruta:
            resultado = subprocess.run(['sudo', 'sha256sum', ruta], 
                                     capture_output=True, text=True, check=True)
            return resultado.stdout.strip().split()[0]
        else:
            with open(ruta, 'rb') as f:
                data = f.read()
                return hashlib.sha256(data).hexdigest()
    except Exception as e:
        print(f"No se puede leer {ruta}: {e}")
        return None

def cargar_hashes_guardados():
    hashes = {}
    if not os.path.exists(hash_file):
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(hash_file), exist_ok=True)
        return hashes
    try:
        with open(hash_file, 'r') as f:
            for linea in f:
                if '::' in linea:
                    nombre, valor = linea.strip().split('::', 1)
                    hashes[nombre] = valor
    except Exception as e:
        print(f"Error cargando hashes: {e}")
    return hashes

def guardar_hashes(hashes):
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(hash_file), exist_ok=True)
        with open(hash_file, 'w') as f:
            for nombre, valor in hashes.items():
                f.write(f"{nombre}::{valor}\\n")
    except Exception as e:
        print(f"Error guardando hashes: {e}")

def verificar_integridad():
    hashes_guardados = cargar_hashes_guardados()
    hashes_actuales = {}

    for archivo in archivos:
        hash_actual = calcular_hash(archivo)
        if hash_actual is None:
            continue

        archivo_simple = os.path.basename(archivo)
        hashes_actuales[archivo_simple] = hash_actual

        if archivo_simple in hashes_guardados:
            if hash_actual != hashes_guardados[archivo_simple]:
                cuerpo = registrar_alarma(
                    "Modificación Detectada",
                    "-",
                    f"Archivo: {archivo_simple}"
                )
                try:
                    enviar_alerta(
                        destinatario=EMAIL['destinatario'],
                        asunto=" Alerta HIPS: Archivo Crítico Modificado",
                        cuerpo=cuerpo
                    )
                except Exception as e:
                    print(f"Error enviando email: {e}")
        else:
            print(f"No se encontró hash previo de {archivo_simple}, agregando.")

    guardar_hashes(hashes_actuales)

if __name__ == "__main__":
    verificar_integridad()