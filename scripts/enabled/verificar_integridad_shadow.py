import hashlib
import subprocess
import sys

sys.path.append('/home/kali/hips/utils')
from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

# Ruta al archivo hash almacenado encriptado
HASH_ARCHIVO = "/var/secure_hashes_mount/hashes_shadow.txt"

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
        destinatario="federi.al2001@gmail.com",
        asunto="🚨 Alerta HIPS: Modificación en archivo crítico",
        cuerpo=mensaje
    )

if __name__ == "__main__":
    verificar_integridad()
