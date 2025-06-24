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

# 4. Mensaje final
echo ""
echo "Setup completo. Para correr la app:"
echo "cd web && source venv/bin/activate && python app.py"
