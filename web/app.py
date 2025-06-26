from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import sys
import subprocess
import io
import datetime
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

from flask import send_file
import matplotlib.pyplot as plt
from configuracion import PATHS, EMAIL, ESCANEO, LOGIN, SCRIPTS
from registrar_log import registrar_alarma, registrar_prevencion

print("DEBUG: registrar_alarma cargado desde:", registrar_alarma.__code__.co_filename)

MODULOS_PATH = PATHS['modulos']

def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def cargar_modulos():
    try:
        with open(MODULOS_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_modulos(data):
    with open(MODULOS_PATH, "w") as f:
        json.dump(data, f, indent=4)

app = Flask(__name__)
app.secret_key = 'superclavehips2025'

USUARIO = LOGIN['user']
CLAVE = LOGIN['pass']

# Scripts que requieren sudo
SCRIPTS_REQUIEREN_SUDO = [
    'verificar_archivos.py',
    'verificar_integridad_shadow.py',
    'detectar_sniffers.py',
    'verificar_memoria.py'
]

def necesita_sudo(nombre_script):
    """Determina si un script necesita ejecutarse con sudo"""
    return nombre_script in SCRIPTS_REQUIEREN_SUDO

@app.route('/scripts')
@login_requerido
def mostrar_scripts():
    scripts_dir = SCRIPTS['enabled']
    scripts = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
    return render_template('scripts.html', scripts=scripts)

@app.route('/ejecutar_script', methods=['POST'])
@login_requerido
def ejecutar_script():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nombre_script = request.form.get('script')
    script_path = os.path.join(SCRIPTS['enabled'], nombre_script)

    USE_SUDO = True  # cambiá esto si no necesitás sudo
    comando = ['python3', script_path]
    if USE_SUDO:
        comando.insert(0, 'sudo')
    try:
        resultado = subprocess.check_output(comando, stderr=subprocess.STDOUT, text=True, timeout=10)
        registrar_alarma("Ejecución de script", "-", f"{nombre_script} ejecutado correctamente")
        flash(f"✅ Script '{nombre_script}' ejecutado correctamente:\n\n{resultado}")
    except subprocess.CalledProcessError as e:
        registrar_alarma("Error de script", "-", f"{nombre_script} falló:\n{e.output}")
        flash(f"❌ Error al ejecutar '{nombre_script}':\n\n{e.output}")
    except subprocess.TimeoutExpired:
        registrar_alarma("Timeout de script", "-", f"{nombre_script} excedió el tiempo máximo")
        flash(f"❌ El script '{nombre_script}' tardó demasiado y fue abortado.")
    except Exception as e:
        registrar_alarma("Excepción ejecutando script", "-", str(e))
        flash(f"❌ Error inesperado ejecutando '{nombre_script}':\n\n{e}")
    return redirect(url_for('mostrar_scripts'))

@app.route('/test_dependencies')
def test_dependencies():
    """Endpoint para probar dependencias de los scripts"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    dependencias = {
        'psutil': False,
        'matplotlib': False,
        'flask': False,
    }
    
    # Probar importaciones
    try:
        import psutil
        dependencias['psutil'] = True
    except ImportError:
        pass
    
    try:
        import matplotlib
        dependencias['matplotlib'] = True
    except ImportError:
        pass
    
    try:
        import flask
        dependencias['flask'] = True
    except ImportError:
        pass
    
    # Verificar permisos y archivos
    verificaciones = {
        'Acceso a /etc/passwd': os.access('/etc/passwd', os.R_OK),
        'Acceso a /etc/shadow': os.access('/etc/shadow', os.R_OK),
        'Directorio config existe': os.path.exists('/home/fedealon/Desktop/Proyecto-HIPS/config'),
        'Directorio log existe': os.path.exists('/var/log/hips'),
        'Comando sudo disponible': subprocess.run(['which', 'sudo'], capture_output=True).returncode == 0,
    }
    
    return render_template('test_dependencies.html', 
                         dependencias=dependencias, 
                         verificaciones=verificaciones)

@app.route('/')
@login_requerido
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['clave'] == CLAVE:
            session['usuario'] = USUARIO
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_requerido
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Alarmas
    alarmas = []
    for ruta in [PATHS.get('log_alarmas', '')]:
        if ruta and os.path.exists(ruta):
            try:
                with open(ruta, 'r') as f:
                    alarmas = f.readlines()[-10:]  # Últimas 10 líneas
                break
            except:
                continue

    # Prevención
    prevenciones = []
    for ruta in [PATHS.get('log_prevencion', '')]:
        if ruta and os.path.exists(ruta):
            try:
                with open(ruta, 'r') as f:
                    prevenciones = f.readlines()[-10:]
                break
            except:
                continue

    # Correos
    correos = []
    for ruta in [PATHS.get('log_alarmas', '')]:
        if ruta and os.path.exists(ruta):
            try:
                with open(ruta, 'r') as f:
                    for linea in f:
                        if any(palabra in linea.lower() for palabra in ["detectado", "correo", "ram", "password", "shadow", "http", "ddos", "cron", "tmp", "mail", "mails"]):
                            correos.append(linea.strip())
                    correos = correos[-10:]
                break
            except:
                continue

    return render_template('dashboard.html', alarmas=alarmas, prevenciones=prevenciones, correos=correos)


@app.route('/graficos')
def graficos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    fechas = {}

    posibles_rutas = [
        '/home/fedealon/Desktop/Proyecto-HIPS/alarmas.log',
        PATHS.get('log_alarmas', '')
    ]

    for ruta in posibles_rutas:
        if ruta and os.path.exists(ruta):
            with open(ruta, 'r') as f:
                for linea in f:
                    if "::" in linea:
                        fecha = linea.split("::")[0].strip()
                        try:
                            fecha_obj = datetime.datetime.strptime(fecha, "%d/%m/%Y %H:%M:%S")
                            clave = fecha_obj.strftime("%d/%m")
                            fechas[clave] = fechas.get(clave, 0) + 1
                        except:
                            continue
            break
    else:
        fechas = {"Sin archivo": 1}

    try:
        fechas_ordenadas = dict(sorted(
            fechas.items(),
            key=lambda x: datetime.datetime.strptime(x[0], "%d/%m")
            if x[0] not in ["Sin datos", "Sin archivo"]
            else datetime.datetime.min
        ))
    except:
        fechas_ordenadas = fechas

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(list(fechas_ordenadas.keys()), list(fechas_ordenadas.values()), 
            color='#121212', marker='o', linestyle='-', linewidth=2,markersize=8  )
    ax.set_title("Alarmas por Día", fontsize=14)
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.set_xlabel("Fecha", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype='image/png')



@app.route('/modulos', methods=['GET', 'POST'])
def modulos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    enabled_path = SCRIPTS['enabled']
    disabled_path = SCRIPTS['disabled']

    if request.method == 'POST':
        script = request.form.get('script')
        action = request.form.get('action')
        try:
            if action == 'desactivar':
                os.rename(os.path.join(enabled_path, script), os.path.join(disabled_path, script))
                flash(f"Módulo {script} desactivado correctamente.")
            elif action == 'activar':
                os.rename(os.path.join(disabled_path, script), os.path.join(enabled_path, script))
                flash(f"Módulo {script} activado correctamente.")
        except Exception as e:
            flash(f"Error al mover el módulo: {e}")
        return redirect(url_for('modulos'))

    try:
        activos = os.listdir(enabled_path)
        inactivos = os.listdir(disabled_path)
    except Exception as e:
        activos = []
        inactivos = []
        flash(f"Error al leer carpetas: {e}")

    return render_template('modulos.html', activos=activos, inactivos=inactivos)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)