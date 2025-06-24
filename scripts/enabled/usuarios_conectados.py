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

def obtener_conexiones_remotas():
    try:
        resultado = subprocess.check_output(['w'], text=True)
        lineas = resultado.strip().split('\n')

        for linea in lineas[2:]:  # Saltar encabezados
            if '127.0.0.1' in linea or '192.' in linea or '10.' in linea:  # Ajustable para otras IPs
                partes = linea.split()
                if len(partes) >= 3:
                    usuario = partes[0]
                    ip = partes[2]
                    cuerpo = registrar_alarma("Conexión remota detectada (w)", ip, f"Usuario: {usuario}")
                    enviar_alerta(
                        destinatario=EMAIL['destinatario'],
                        asunto="🚨 Alerta HIPS: Usuario conectado remotamente (w)",
                        cuerpo=cuerpo
                    )

    except Exception as e:
        print(f"Error al obtener conexiones remotas: {e}")

if __name__ == "__main__":
    obtener_conexiones_remotas()
