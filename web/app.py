from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
from flask import send_file
import matplotlib.pyplot as plt
import io
import datetime
import subprocess
MODULOS_PATH = "/home/kali/hips/config/modulos.json"

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

USUARIO = "admin"
CLAVE = "admin123"
@app.route('/scripts')
def mostrar_scripts():
    scripts_dir = os.path.expanduser('~/hips/scripts/enabled')
    scripts = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
    return render_template('scripts.html', scripts=scripts)

@app.route('/ejecutar_script', methods=['POST'])
def ejecutar_script():
    nombre_script = request.form.get('script')
    script_path = os.path.expanduser(f'~/hips/scripts/enabled/{nombre_script}')

    try:
        resultado = subprocess.check_output(['sudo', 'python3', script_path], stderr=subprocess.STDOUT, text=True)
        flash(f"✅ Script '{nombre_script}' ejecutado correctamente:\n\n{resultado}")
    except subprocess.CalledProcessError as e:
        flash(f"❌ Error al ejecutar '{nombre_script}':\n\n{e.output}")

    return redirect(url_for('mostrar_scripts'))

@app.route('/')
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
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/ver_alarmas')
def ver_alarmas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        with open('/var/log/hips/alarmas.log', 'r') as f:
            contenido = f.readlines()
    except:
        contenido = ["No se pudo leer el archivo de alarmas."]
    return render_template('alarmas.html', log=contenido)

@app.route('/ver_prevencion')
def ver_prevencion():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        with open('/var/log/hips/prevencion.log', 'r') as f:
            contenido = f.readlines()
    except:
        contenido = ["No se pudo leer el archivo de prevenciones."]
    return render_template('prevencion.html', log=contenido)

@app.route('/graficos')
def graficos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    import matplotlib.pyplot as plt
    import io
    import datetime

    fechas = {}

    try:
        with open('/var/log/hips/alarmas.log', 'r') as f:
            for linea in f:
                if "::" in linea:
                    fecha = linea.split("::")[0].strip()
                    try:
                        fecha_obj = datetime.datetime.strptime(fecha, "%d/%m/%Y %H:%M:%S")
                        clave = fecha_obj.strftime("%d/%m")
                        fechas[clave] = fechas.get(clave, 0) + 1
                    except:
                        continue
    except:
        fechas = {"Sin datos": 1}

    # Ordenar las fechas
    try:
        fechas_ordenadas = dict(sorted(
            fechas.items(),
            key=lambda x: datetime.datetime.strptime(x[0], "%d/%m")
        ))
    except:
        fechas_ordenadas = fechas

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(fechas_ordenadas.keys(), fechas_ordenadas.values(), color='#00ff88', edgecolor='black')
    ax.set_title("📊 Alarmas por Día", fontsize=14)
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.set_xlabel("Fecha", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Exportar imagen
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype='image/png')


@app.route('/correos')
def correos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    historial = []
    try:
        with open('/var/log/hips/alarmas.log', 'r') as f:
            for linea in f:
                if any(palabra in linea.lower() for palabra in ["detectado", "correo", "ram", "password", "shadow", "http", "ddos", "cron", "tmp", "mail", "mails"]):
                    historial.append(linea.strip())
    except:
        historial = ["No se pudo leer el archivo."]

    return render_template('correos.html', correos=historial)

@app.route('/modulos', methods=['GET', 'POST'])
def modulos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    enabled_path = os.path.expanduser('~/hips/scripts/enabled')
    disabled_path = os.path.expanduser('~/hips/scripts/disabled')

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
    app.run(debug=True)

