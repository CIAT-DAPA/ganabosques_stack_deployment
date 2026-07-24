#!/bin/bash

set -e

echo "EJECUTANDO INSTALL:"
echo "$(realpath "$0")"

echo ""
echo "====================================="
echo " GanaBosques Deployment Installer"
echo " Linux"
echo "====================================="
echo ""

#
# Verificar Python
#
if ! command -v python3 &> /dev/null
then
    echo "Python 3 no esta instalado."
    exit 1
fi

#
# Verificar Docker
#
if ! command -v docker &> /dev/null
then
    echo "Docker no esta instalado."
    exit 1
fi

#
# Verificar Docker Compose
#
if ! docker compose version &> /dev/null
then
    echo "Docker Compose no esta disponible."
    exit 1
fi

#
# Crear entorno virtual
#
if [ ! -d "env" ]
then
    echo "Creando entorno virtual..."
    python3 -m venv env
fi

#
# Activar entorno
#
source env/bin/activate

#
# Instalar dependencias
#
echo "Instalando dependencias Python..."

python -m pip install --upgrade pip
pip install -r requirements.txt

#
# Verificar .env
#
if [ ! -f ".env" ]
then
    if [ -f ".env.example" ]
    then
        cp .env.example .env

        echo ""
        echo "Se creo el archivo .env"
        echo "Configure los valores antes de continuar."
        echo ""

        exit 0
    else
        echo "No existe .env ni .env.example"
        exit 1
    fi
fi

#
# Descargar repositorios
#
echo ""
echo "Clonando repositorios..."

python scripts/clone_repositories.py

#
# Crear configuraciones
#
echo ""
echo "Configurando variables internas..."

python scripts/configure_env.py
python scripts/generate_nginx.py
python scripts/generate_keycloak.py

#
# Construir imagenes
#
echo ""
echo "Construyendo imagenes Docker..."

docker compose --env-file .env build

#
# Levantar servicios
#
echo ""
echo "Iniciando ecosistema GanaBosques..."

docker compose --env-file .env up -d

#
# Estado final
#
echo ""

docker compose ps

echo ""
echo "====================================="
echo " Instalacion completada"
echo "====================================="