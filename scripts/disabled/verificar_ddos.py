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

LOG_PATH = PATHS['log_ddos']
UMBRAL = 30  # solicitudes desde misma IP

def detectar_ddos():
    ip_contador = defaultdict(int)

    try:
        with open(LOG_PATH, 'r') as f:
            for linea in f:
                match = re.search(r'request from ([\d.]+)', linea)
                if match:
                    ip = match.group(1)
                    ip_contador[ip] += 1

        for ip, cantidad in ip_contador.items():
            if cantidad >= UMBRAL:
                cuerpo = registrar_alarma("Posible DDoS", ip, f"{cantidad} solicitudes DNS")
                enviar_alerta(
                    destinatario=EMAIL['destinatario'],
                    asunto=" Alerta HIPS: Ataque DDoS detectado",
                    cuerpo=cuerpo
                )

    except Exception as e:
        print(f"Error al analizar log DDoS: {e}")

if __name__ == "__main__":
    detectar_ddos()
