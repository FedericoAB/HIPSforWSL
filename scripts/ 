import subprocess
import re
import random
import string
from collections import defaultdict
import sys

sys.path.append('/home/kali/hips/utils')
from registrar_log import registrar_alarma
from enviar_mail import enviar_alerta

UMBRAL = 5  # cantidad de mails por usuario
USUARIO_EXCLUIDO = "kali"  # nunca se toca

def generar_password(longitud=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def cambiar_contrasena(usuario):
    nueva_pass = generar_password()
    try:
        # Crear el comando echo "usuario:nuevacontrasena" | chpasswd
        comando = f"echo '{usuario}:{nueva_pass}' | sudo chpasswd"
        subprocess.run(comando, shell=True, check=True)
        registrar_alarma("Contraseña cambiada", "-", f"Se cambió la contraseña de {usuario} por spam.")
        print(f"🔒 Contraseña cambiada para {usuario}")
    except Exception as e:
        registrar_alarma("Error al cambiar contraseña", "-", str(e))

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
            if cantidad >= UMBRAL and usuario != USUARIO_EXCLUIDO:
                resumen += f"• {usuario} envió {cantidad} mails\n"
                registrar_alarma("Envío masivo de mails", "-", f"{usuario} envió {cantidad} mails")
                cambiar_contrasena(usuario)

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
