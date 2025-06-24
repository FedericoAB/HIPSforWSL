import hashlib
import os
import sys

sys.path.append('/home/kali/hips/utils')

from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

# Archivos a verificar
archivos = ['/etc/passwd', '/etc/shadow']
# Archivo donde guardaremos los hashes
hash_file = '/home/kali/hips/config/hashes.txt' 

def calcular_hash(ruta):
    try:
        with open(ruta, 'rb') as f:
            data = f.read()
            return hashlib.sha256(data).hexdigest()
    except Exception as e:
        print(f"No se puede leer {ruta}: {e}")
        return None

def cargar_hashes_guardados():
    hashes = {}
    if not os.path.exists(hash_file):
        return hashes
    with open(hash_file, 'r') as f:
        for linea in f:
            nombre, valor = linea.strip().split('::')
            hashes[nombre] = valor
    return hashes

def guardar_hashes(hashes):
    with open(hash_file, 'w') as f:
        for nombre, valor in hashes.items():
            f.write(f"{nombre}::{valor}\n")

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
                enviar_alerta(
                    destinatario="federi.al2001@gmail.com",
                    asunto="🚨 Alerta HIPS: Archivo Crítico Modificado",
                    cuerpo=cuerpo
                )
        else:
            print(f"No se encontró hash previo de {archivo_simple}, agregando.")

    guardar_hashes(hashes_actuales)

if __name__ == "__main__":
    verificar_integridad()
