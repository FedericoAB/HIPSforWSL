import os
import subprocess
import sys
from configuracion import PATHS, EMAIL, ESCANEO

sys.path.append(PATHS['utils'])


from enviar_mail import enviar_alerta
from registrar_log import registrar_alarma, registrar_prevencion

sniffers = ['tcpdump', 'wireshark', 'ethereal', 'dumpcap']

def detectar_y_prevenir_sniffers():
    try:
        procesos = subprocess.check_output(['ps', '-eo', 'pid,comm'], text=True).splitlines()
        for linea in procesos[1:]:
            partes = linea.strip().split(None, 1)
            if len(partes) != 2:
                continue
            pid, nombre = partes
            if nombre in sniffers:
                cuerpo = registrar_alarma("Sniffer Detectado", "-", f"Proceso: {nombre}")
                enviar_alerta(
                    destinatario=EMAIL['destinatario']
                    asunto="🚨 Alerta HIPS: Sniffer Detectado",
                    cuerpo=cuerpo
                )
                try:
                    os.kill(int(pid), 9)
                    registrar_prevencion("Proceso Eliminado", "-", f"{nombre} (PID: {pid})")
                except Exception as e:
                    print(f"No se pudo matar {nombre} (PID {pid}): {e}")
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    detectar_y_prevenir_sniffers()

