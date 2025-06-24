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

import subprocess
import re

def obtener_conexiones_remotas():
    try:
        resultado = subprocess.check_output(['ss', '-tnp'], text=True)
        lineas = resultado.strip().split('\n')

        for linea in lineas[1:]:
            if 'ESTAB' in linea:
                partes = linea.split()
                if len(partes) >= 5:
                    remote_addr = partes[4]
                    # remote_addr puede ser [::1]:puerto para IPv6 o ip:puerto para IPv4
                    # Quitar los corchetes si existen (IPv6)
                    if remote_addr.startswith('['):
                        ip = remote_addr.split(']:')[0][1:]
                    else:
                        ip = remote_addr.rsplit(':', 1)[0]

                    if ip != '127.0.0.1' and ip != '::1':
                        print(f"Conexión remota detectada: {ip}")
                        # registrar_alarma y enviar_alerta aquí

    except Exception as e:
        print(f"Error al obtener conexiones remotas: {e}")

if __name__ == "__main__":
    obtener_conexiones_remotas()
