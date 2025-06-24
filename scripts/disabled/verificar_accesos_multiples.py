import subprocess
import re
from collections import defaultdict
import sys
import os
UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO
from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

UMBRAL_IP = 5
UMBRAL_USUARIO = 5

def detectar_accesos_repetidos():
    intentos_por_ip = defaultdict(int)
    intentos_por_usuario = defaultdict(int)

    try:
        salida = subprocess.check_output(['journalctl', '-xe', '--no-pager'], text=True)
        lineas = salida.strip().split('\n')

        for linea in lineas:
            if "Failed password" in linea:
                ip_match = re.search(r'from ([\d.]+)', linea)
                user_match = re.search(r'for (invalid user )?(\w+)', linea)
                if ip_match:
                    ip = ip_match.group(1)
                    intentos_por_ip[ip] += 1
                if user_match:
                    usuario = user_match.group(2)
                    intentos_por_usuario[usuario] += 1

        for ip, count in intentos_por_ip.items():
            if count >= UMBRAL_IP:
                cuerpo = registrar_alarma("Accesos fallidos desde IP repetida", ip, f"{count} intentos fallidos")
                enviar_alerta(
                    destinatario=EMAIL['destinatario'],
                    asunto="🚨 Alerta HIPS: IP con múltiples intentos de acceso",
                    cuerpo=cuerpo
                )

        for user, count in intentos_por_usuario.items():
            if count >= UMBRAL_USUARIO:
                cuerpo = registrar_alarma("Accesos fallidos al usuario", "-", f"{user} recibió {count} intentos")
                enviar_alerta(
                    destinatario=EMAIL['destinatario'],
                    asunto="🚨 Alerta HIPS: Usuario atacado repetidamente",
                    cuerpo=cuerpo
                )

    except Exception as e:
        print(f"Error al analizar accesos múltiples: {e}")

if __name__ == "__main__":
    detectar_accesos_repetidos()
