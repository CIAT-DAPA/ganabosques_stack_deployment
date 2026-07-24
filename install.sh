#!/bin/bash

set -e


echo ""
echo "====================================="
echo " GanaBosques Deployment Installer"
echo " Linux/macOS"
echo "====================================="
echo ""



#
# Docker
#

if ! command -v docker &> /dev/null
then

    echo "Docker no esta instalado"

    exit 1

fi



#
# Entorno Python
#

if [ ! -d "env" ]
then

    echo "Creando entorno virtual..."

    python3 -m venv env

fi



source env/bin/activate



#
# Dependencias
#

echo "Instalando dependencias..."

pip install --upgrade pip

pip install -r requirements.txt



#
# .env
#

if [ ! -f ".env" ]
then


    if [ -f ".env.example" ]
    then

        cp .env.example .env


        echo ""
        echo "Se creo .env"
        echo "Configure las variables antes de continuar."
        echo ""

        exit 0

    else

        echo "No existe .env.example"

        exit 1

    fi

fi



#
# Repositorios
#

echo "Clonando repositorios..."

python scripts/clone_repositories.py



#
# Variables internas
#

echo "Configurando servicios..."

python scripts/configure_env.py



#
# Docker
#

echo "Construyendo imagenes..."

docker compose --env-file .env build



echo "Iniciando servicios..."

docker compose --env-file .env up -d



docker compose ps



echo ""

echo "====================================="
echo " Instalacion completada"
echo "====================================="