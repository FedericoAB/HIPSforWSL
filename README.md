# Manual de Instalación y Uso del Sistema HIPS (Host-based Intrusion Prevention System)

---

## Descripción General

El sistema HIPS es una herramienta de prevención de intrusiones basada en host, desarrollada principalmente en Python y con una interfaz web basada en Flask. Su propósito es monitorear un sistema operativo Linux (en este caso, bajo un entorno WSL en Ubuntu), detectar comportamientos sospechosos y tomar acciones preventivas ante potenciales amenazas. El sistema permite registrar eventos, emitir alertas por correo electrónico y actuar automáticamente sobre posibles intrusiones. También ofrece una interfaz web básica para la configuración de módulos y visualización de alarmas.

---

## Requisitos del Sistema

* Entorno: Ubuntu corriendo bajo WSL (Windows Subsystem for Linux)
* Python 3.10 o superior
* Sistema de correo instalado (postfix o sendmail)
* Navegador web para acceder a la interfaz

### Dependencias de Python

Dentro del entorno WSL:

```bash
sudo apt update
sudo apt install python3-pip git postfix -y
pip install flask matplotlib psutil
```

---

## Estructura del Proyecto

```
Proyecto-HIPS/
├── config/hips_config.ini          # Configuración general del sistema
├── utils/                          # Módulos compartidos: configuracion.py, enviar_mail.py, registrar_log.py
├── scripts/
│   ├── enabled/                    # Módulos activos
│   └── disabled/                   # Módulos desactivados
├── web/                            # Interfaz web con Flask
│   └── templates/                  # Archivos HTML para la interfaz
├── datos_prueba/                   # Logs y archivos de prueba
└── venv/                           # Entorno virtual de Python (recomendado)
```

---

## Instalación Paso a Paso

### 1. Clonar el repositorio

Abrir la terminal de WSL:

```bash
git clone https://github.com/usuario/Proyecto-HIPS.git
cd Proyecto-HIPS
```

### 2. Crear entorno virtual y activar

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install flask matplotlib psutil
```

### 4. Crear archivo de configuración

Editar `config/hips_config.ini` con las credenciales y rutas deseadas:

```ini
[EMAIL]
remitente = admin@example.com
clave = TU_CLAVE_SEGURA

destinatario = seguridad@example.com

[PATHS]
log_alarmas = /var/log/hips/alarmas.log
log_prevencion = /var/log/hips/prevencion.log
modulos = /home/usuario/Proyecto-HIPS/scripts/enabled

[LOGIN]
user = admin
pass = admin123
```

### 5. Crear directorio de logs

```bash
sudo mkdir -p /var/log/hips
sudo touch /var/log/hips/alarmas.log /var/log/hips/prevencion.log
sudo chmod 666 /var/log/hips/*.log
```

---

## Ejecución del Sistema

Desde la carpeta `web`:

```bash
cd web
source ../venv/bin/activate
python3 app.py
```

Esto iniciará el servidor en `http://localhost:5000` dentro del entorno WSL. Podés acceder desde tu navegador en Windows.

---

## Acceso a la Interfaz Web

El acceso está protegido mediante usuario y contraseña. Estos datos se definen en el archivo de configuración (`hips_config.ini`).

* Usuario: `admin`
* Contraseña: `admin123`

---

## Funcionalidades Principales

### Módulos Disponibles

Los scripts ubicados en `scripts/enabled/` pueden ser ejecutados manualmente desde la interfaz web. Algunos ejemplos:

* Detección de conexiones remotas
* Detección de sniffers
* Monitoreo del uso de memoria
* Comparación de hash de archivos sensibles (`/etc/shadow`, `/etc/passwd`)
* Análisis del directorio `/tmp` para scripts sospechosos
* Revisión de logs de envío de correos

Los módulos también pueden desactivarse y activarse desde la interfaz, moviéndolos entre `enabled/` y `disabled/`.

---

## Archivos de Logs

* `/var/log/hips/alarmas.log`: contiene todas las alarmas detectadas
* `/var/log/hips/prevencion.log`: registra las acciones preventivas tomadas

Ejemplo de entrada:

```
26/06/2025 20:45:31 :: Detección de sniffer :: 192.168.1.22 eth0 en modo promiscuo
```

---

## Alertas por Correo Electrónico

Cuando un evento sospechoso es detectado, el sistema genera un correo automático al administrador definido en el archivo de configuración. Esto requiere que el sistema de correo (como `postfix`) esté correctamente configurado en el entorno WSL.

---

## Pruebas Recomendadas

Para verificar el funcionamiento completo del sistema, se deben realizar las siguientes pruebas:

* Simular múltiples accesos fallidos por SSH
* Crear archivos `.sh`, `.php` o `.exe` en `/tmp`
* Modificar manualmente el archivo `/etc/shadow`
* Detectar procesos en modo promiscuo
* Detectar excesivo envío de correos desde un usuario local

Verificar:

* Que se registren los eventos en los logs
* Que lleguen correos de alerta
* Que se ejecuten acciones de prevención como bloqueo de IP o aislamiento del archivo

---

## Seguridad y Buenas Prácticas

* No subir claves ni configuraciones sensibles al repositorio
* Usar variables de entorno o archivos cifrados para guardar contraseñas
* Usar PostgreSQL sólo con usuarios de privilegios mínimos
* Cifrar los archivos que contienen firmas o hashes de archivos críticos
* Ejecutar en una máquina virtual o contenedor para evitar dañar el sistema principal

---

## Créditos y Desarrollo

Este sistema fue desarrollado por estudiantes de la carrera de Ingeniería Informática como parte del proyecto final de la asignatura Lenguaje de Programación. El código fue validado en entorno Ubuntu bajo WSL con compatibilidad verificada para CentOS.
