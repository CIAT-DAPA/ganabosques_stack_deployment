Write-Host "EJECUTANDO INSTALL:"
Write-Host $MyInvocation.MyCommand.Path

$ErrorActionPreference = "Stop"


Write-Host ""
Write-Host "====================================="
Write-Host " GanaBosques Deployment Installer"
Write-Host " Windows"
Write-Host "====================================="
Write-Host ""


#
# Verificar Docker
#

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {

    Write-Host "Docker no esta instalado."

    exit 1
}



#
# Crear entorno virtual Python
#

if (!(Test-Path "env")) {

    Write-Host "Creando entorno virtual..."

    python -m venv env
}



#
# Activar entorno
#

.\env\Scripts\Activate.ps1



#
# Instalar dependencias
#

Write-Host "Instalando dependencias Python..."

python -m pip install --upgrade pip

pip install -r requirements.txt



#
# Verificar .env
#

if (!(Test-Path ".env")) {


    if (Test-Path ".env.example") {


        Copy-Item ".env.example" ".env"


        Write-Host ""
        Write-Host "Se creo el archivo .env"
        Write-Host "Configure los valores antes de continuar."
        Write-Host ""

        exit 0

    }
    else {

        Write-Host "No existe .env ni .env.example"

        exit 1
    }

}



#
# Descargar repositorios
#

Write-Host ""
Write-Host "Clonando repositorios..."

python scripts\clone_repositories.py



#
# Crear configuraciones
#

Write-Host ""
Write-Host "Configurando variables internas..."

python scripts\configure_env.py


python scripts\generate_nginx.py

python scripts\generate_keycloak.py

#
# Construir imagenes
#

Write-Host ""
Write-Host "Construyendo imagenes Docker..."

docker compose --env-file .env build



#
# Levantar servicios
#

#
# Levantar servicios
#

Write-Host ""
Write-Host "Iniciando ecosistema GanaBosques..."



docker compose --env-file .env up -d




#
# Estado final
#

Write-Host ""

docker compose ps


Write-Host ""

Write-Host "====================================="
Write-Host " Instalacion completada"
Write-Host "====================================="