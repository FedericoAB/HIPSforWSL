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

UMBRAL = 5  # cantidad de mails por usuario

def analizar_mails_desde_journal():
    conteo = defaultdict(int)

    try:
        salida = subprocess.check_output(['journalctl', '-u', 'postfix', '--no-pager'], text=True)
        lineas = salida.strip().split('\n')

        for linea in lineas:
            match = re.search(r'from=<([^@]+)@?', linea)
            if match:
                usuario = match.group(1)
                conteo[usuario] += 1

        resumen = ""
        for usuario, cantidad in conteo.items():
            if cantidad >= UMBRAL:
                resumen += f"• {usuario} envió {cantidad} mails\n"
                registrar_alarma("Envío masivo de mails", "-", f"{usuario} envió {cantidad} mails")

        if resumen:
            enviar_alerta(
                destinatario=EMAIL['destinatario'],
                asunto="🚨 Alerta HIPS: Actividad de correo sospechosa",
                cuerpo=f"Se detectaron usuarios con envío excesivo de mails:\n\n{resumen}"
            )


    except Exception as e:
        print(f"Error al leer journalctl: {e}")

if __name__ == "__main__":
    analizar_mails_desde_journal()
