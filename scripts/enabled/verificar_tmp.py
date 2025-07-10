import os
import shutil
import sys
import subprocess
import re
import hashlib
from collections import defaultdict

UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO  # Ajustar si tu usuario no es kali

from registrar_log import registrar_alarma, registrar_prevencion
from enviar_mail import enviar_alerta

# Extensiones sospechosas
extensiones = ['.sh', '.py', '.php', '.pl', '.exe']

# Ruta del directorio a inspeccionar
directorio_tmp = '/tmp'
cuarentena = '/tmp_cuarentena'

def mover_a_cuarentena(ruta):
    if not os.path.exists(cuarentena):
        os.makedirs(cuarentena)
    destino = os.path.join(cuarentena, os.path.basename(ruta))
    shutil.move(ruta, destino)
    return destino

def analizar_tmp():
    try:
        for archivo in os.listdir(directorio_tmp):
            ruta = os.path.join(directorio_tmp, archivo)
            if os.path.isfile(ruta):
                for ext in extensiones:
                    if archivo.endswith(tuple(extensiones)) or es_script(ruta):
                        cuerpo = registrar_alarma("Archivo sospechoso en /tmp", "-", f"Archivo: {archivo}")
                        enviar_alerta(
                            destinatario=EMAIL['destinatario'],
                            asunto="Alerta HIPS: Archivo sospechoso en /tmp",
                            cuerpo=cuerpo
                        )
                        nuevo_destino = mover_a_cuarentena(ruta)
                        registrar_prevencion("Archivo movido a cuarentena", "-", f"{nuevo_destino}")

    except Exception as e:
        print(f"Error al analizar /tmp: {e}")

def obtener_hash_md5(ruta_archivo):
    hash_md5 = hashlib.md5()
    with open(ruta_archivo, 'rb') as f:
        for bloque in iter(lambda: f.read(4096), b""):
            hash_md5.update(bloque)
    return hash_md5.hexdigest()

def verificar_integridad(ruta_archivo, hash_esperado):
    hash_actual = obtener_hash_md5(ruta_archivo)
    return hash_actual == hash_esperado


if __name__ == "__main__":
    analizar_tmp()
