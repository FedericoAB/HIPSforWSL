import psutil
import os
import sys
import subprocess
import re
from collections import defaultdict
UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)
from configuracion import PATHS, EMAIL, ESCANEO 

from registrar_log import registrar_alarma, registrar_prevencion
from enviar_mail import enviar_alerta

UMBRAL_RAM = 1.0  # En porcentaje

def detectar_ram_excesiva():
    for proceso in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            pid = proceso.info['pid']
            nombre = proceso.info['name']
            memoria = proceso.info['memory_percent']

            if memoria and memoria > UMBRAL_RAM:
                detalle = f"{nombre} (PID: {pid}) usando {memoria:.2f}% RAM"
                cuerpo = registrar_alarma("RAM excesiva", "-", detalle)
                enviar_alerta(
                    destinatario=EMAIL['destinatario'],
                    asunto="🚨 Alerta HIPS: Uso excesivo de RAM",
                    cuerpo=cuerpo
                )
                os.kill(pid, 9)
                registrar_prevencion("Proceso terminado por RAM", "-", detalle)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

if __name__ == "__main__":
    detectar_ram_excesiva()
