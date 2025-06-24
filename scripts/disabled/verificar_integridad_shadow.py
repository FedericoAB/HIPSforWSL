import hashlib
import subprocess
import sys
import os
import re
from collections import defaultdict

UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO
from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

# Ruta al archivo hash almacenado encriptado
HASH_ARCHIVO = "/home/fedealon/Desktop/Proyecto-HIPS/config/hashes.txt"

def obtener_hash_actual():
    try:
        resultado = subprocess.check_output(['sha256sum', '/etc/shadow'], text=True)
        hash_actual = resultado.strip().split()[0]
        return hash_actual
    except Exception as e:
        print(f"❌ Error al calcular hash actual: {e}")
        return None

def leer_hash_original():
    try:
        with open(HASH_ARCHIVO, 'r') as f:
            hash_guardado = f.readline().strip().split()[0]
            return hash_guardado
    except Exception as e:
        print(f"❌ Error al leer hash guardado: {e}")
        return None

def verificar_integridad():
    hash_actual = obtener_hash_actual()
    hash_guardado = leer_hash_original()

    if not hash_actual or not hash_guardado:
        return

    if hash_actual != hash_guardado:
        mensaje = "El archivo /etc/shadow fue modificado."
        registrar_alarma("Modificación de archivo crítico", "-", mensaje)
        enviar_mail(mensaje)
        print("🚨 Hash modificado - se registró alarma y se envió mail.")
    else:
        print("✅ El archivo /etc/shadow está íntegro.")

def enviar_mail(mensaje):
    enviar_alerta(
        destinatario=EMAIL['destinatario'],
        asunto="🚨 Alerta HIPS: Modificación en archivo crítico",
        cuerpo=mensaje
    )

if __name__ == "__main__":
    verificar_integridad()
