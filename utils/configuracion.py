import configparser
import os

CONFIG_PATH = os.path.expanduser('/home/fedealon/Desktop/Proyecto-HIPS/config/hips_config.ini')

config = configparser.ConfigParser()
loaded_files = config.read(CONFIG_PATH)

if not loaded_files:
    raise FileNotFoundError(f"Error: No se pudo cargar el archivo de configuración desde {CONFIG_PATH}")

# Ahora sí asignamos
EMAIL = config['EMAIL']
PATHS = config['PATHS']
ESCANEO = config['ESCANEO']
LOGIN = config['LOGIN']
SCRIPTS = config['SCRIPTS']
