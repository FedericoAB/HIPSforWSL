import subprocess
import sys
import re
from datetime import datetime
import os
from collections import defaultdict
UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO 
from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

# Obtener solo eventos recientes con "Failed password"
def obtener_intentos_fallidos():
    try:
        salida = subprocess.check_output(['journalctl', '-xe', '--no-pager'], text=True)
        lineas = salida.strip().split('\n')
        ips_detectadas = set()
        for linea in lineas:
            if "Failed password" in linea:
                match = re.search(r'from ([\d.]+)', linea)
                if match:
                    ip = match.group(1)
                    if ip not in ips_detectadas:
                        cuerpo = registrar_alarma("Intento fallido de acceso", ip, "SSH - Failed password")
                        enviar_alerta(
                            destinatario=EMAIL['destinatario'],
                            asunto="Alerta HIPS: Intento fallido de acceso",
                            cuerpo=cuerpo
                        )
                        ips_detectadas.add(ip)
    except Exception as e:
        print(f"Error al leer journalctl: {e}")

if __name__ == "__main__":
    obtener_intentos_fallidos()
