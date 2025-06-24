import subprocess
import re
from collections import defaultdict
import sys

sys.path.append('/home/kali/hips/utils')

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
                destinatario="federi.al2001@gmail.com",
                asunto="🚨 Alerta HIPS: Actividad de correo sospechosa",
                cuerpo=f"Se detectaron usuarios con envío excesivo de mails:\n\n{resumen}"
            )


    except Exception as e:
        print(f"Error al leer journalctl: {e}")

if __name__ == "__main__":
    analizar_mails_desde_journal()
