import configparser
import os

CONFIG_PATH = os.path.expanduser('~/Desktop/Proyecto-HIPS/config/hips_config.ini')

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

EMAIL = config['EMAIL']
PATHS = config['PATHS']
ESCANEO = config['ESCANEO']
