import os
import subprocess
import sys

import sys
import os
import subprocess
import re
from collections import defaultdict

UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO 

from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

RUTAS_SOSPECHOSAS = ['/tmp', '/home']

def revisar_lineas_cron(lineas, fuente):
    for linea in lineas:
        if linea.strip().startswith("#") or not linea.strip():
            continue
        for ruta in RUTAS_SOSPECHOSAS:
            if ruta in linea:
                cuerpo = registrar_alarma("Tarea cron sospechosa", "-", f"{linea.strip()} [{fuente}]")
                enviar_alerta(
                    destinatario=EMAIL['destinatario'],
                    asunto=" Alerta HIPS: Cron sospechoso",
                    cuerpo=cuerpo
                )

def analizar_cron():
    try:
        # crontab del usuario
        resultado = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if resultado.stdout:
            revisar_lineas_cron(resultado.stdout.split('\n'), "crontab -l")

        # /etc/crontab
        if os.path.exists('/etc/crontab'):
            with open('/etc/crontab') as f:
                revisar_lineas_cron(f.readlines(), "/etc/crontab")

        # Archivos en /etc/cron.d/
        if os.path.isdir('/etc/cron.d/'):
            for archivo in os.listdir('/etc/cron.d/'):
                path = os.path.join('/etc/cron.d/', archivo)
                if os.path.isfile(path):
                    with open(path) as f:
                        revisar_lineas_cron(f.readlines(), path)

    except Exception as e:
        print(f"Error al analizar cron: {e}")

if __name__ == "__main__":
    analizar_cron()
