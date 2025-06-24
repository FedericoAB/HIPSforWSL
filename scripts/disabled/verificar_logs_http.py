import re
from collections import defaultdict
import sys
import os
import subprocess
UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO

from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

# Umbral de errores 404 o 403 por IP
UMBRAL = 1
LOG_PATH = "/tmp/access.log"

def analizar_log_http():
    errores_por_ip = defaultdict(int)

    try:
        with open(LOG_PATH, 'r') as f:
            for linea in f:
                match = re.search(r'([\d.:a-fA-F]+) - - .*"\w+ .*" (\d{3})', linea)
                if match:
                    ip = match.group(1)
                    codigo = match.group(2)
                    if codigo in ['403', '404']:
                        errores_por_ip[ip] += 1


        for ip, cantidad in errores_por_ip.items():
            if cantidad >= UMBRAL:
                cuerpo = registrar_alarma("Errores HTTP desde IP", ip, f"{cantidad} errores 403/404")
                enviar_alerta(
                    destinatario=EMAIL['destinatario'],
                    asunto="🚨 Alerta HIPS: Ataques web sospechosos",
                    cuerpo=cuerpo
                )

    except Exception as e:
        print(f"Error al analizar el log de Apache: {e}")

if __name__ == "__main__":
    analizar_log_http()
