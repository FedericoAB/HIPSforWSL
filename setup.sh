#!/bin/bash

echo "Configurando entorno virtual para HIPS..."

cd web || { echo "No se encontró el directorio 'web'"; exit 1; }

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# 2. Activar el entorno
echo "Activando entorno virtual..."
source venv/bin/activate

# 3. Instalar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
pip install flask matplotlib
pip install psutil

sudo chown $USER:$USER /var/log/hips
sudo chown $USER:$USER /tmp_cuarentena
sudo chmod 755 /var/log/hips
sudo chmod 755 /tmp_cuarentena
# 4. Crear directorios
echo "Creando directorios necesarios..."
sudo mkdir -p /var/log/hips
sudo mkdir -p /var/secure_hashes_mount
sudo mkdir -p /tmp_cuarentena
# 5. Crear archivos de log de prueba
echo "📄 Creando archivos de log..."
touch /home/fedealon/Desktop/Proyecto-HIPS/alarmas.log
touch /home/fedealon/Desktop/Proyecto-HIPS/prevencion.log
touch /home/fedealon/Desktop/Proyecto-HIPS/datos_prueba/log_ddos.txt
cat > /home/fedealon/Desktop/Proyecto-HIPS/datos_prueba/log_ddos.txt << 'EOF'
2025-06-24 10:30:15 DNS request from 192.168.1.100
2025-06-24 10:30:16 DNS request from 192.168.1.100
2025-06-24 10:30:17 DNS request from 192.168.1.100
2025-06-24 10:30:18 DNS request from 192.168.1.100
2025-06-24 10:30:19 DNS request from 192.168.1.100
2025-06-24 10:30:20 DNS request from 192.168.1.101
2025-06-24 10:30:21 DNS request from 192.168.1.102
2025-06-24 10:30:22 DNS request from 10.0.0.50
EOF
# 6. Mensaje final
echo ""
echo "Setup completo. Para correr la app:"
echo "cd web && source venv/bin/activate && python app.py"
