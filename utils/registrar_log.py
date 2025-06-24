import datetime

# Ruta fija del directorio de logs
RUTA_ALARMAS = '/var/log/hips/alarmas.log'
RUTA_PREVENCION = '/var/log/hips/prevencion.log'

def registrar_alarma(tipo_alarma, ip='-', detalle=''):
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linea = f"{timestamp} :: {tipo_alarma} :: {ip} {detalle}\n"
    try:
        with open(RUTA_ALARMAS, 'a') as f:
            f.write(linea)
        print(linea.strip())
        return linea  # para enviar por correo
    except Exception as e:
        print(f"Error al registrar alarma: {e}")

def registrar_prevencion(accion, ip='-', detalle=''):
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linea = f"{timestamp} :: {accion} :: {ip} {detalle}\n"
    try:
        with open(RUTA_PREVENCION, 'a') as f:
            f.write(linea)
        print(linea.strip())
    except Exception as e:
        print(f"Error al registrar prevención: {e}")
