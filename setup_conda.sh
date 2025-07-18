#!/bin/bash

# RADOX - Script de Instalación para Conda
# Sistema de Detección de Neumonía con IA

set -e

echo "🚀 RADOX - Instalación con Conda"
echo "================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar conda
check_conda() {
    print_status "Verificando Conda..."
    
    if ! command -v conda &> /dev/null; then
        print_error "Conda no está instalado"
        print_warning "Instala Miniconda desde: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    print_success "Conda está instalado"
}

# Crear entorno conda
create_conda_env() {
    print_status "Creando entorno conda..."
    
    if conda env list | grep -q "radox"; then
        print_warning "El entorno 'radox' ya existe"
        read -p "¿Quieres recrearlo? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            conda env remove -n radox
            conda create -n radox python=3.11 -y
        fi
    else
        conda create -n radox python=3.11 -y
    fi
    
    print_success "Entorno conda creado"
}

# Crear estructura de directorios
create_directories() {
    print_status "Creando estructura de directorios..."
    
    mkdir -p backend/{api/{routes},models,services,config,utils}
    mkdir -p data/{models,uploads}
    mkdir -p scripts logs
    
    print_success "Estructura de directorios creada"
}

# Instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias..."
    
    # Activar entorno conda
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate radox
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias
    pip install -r requirements.txt
    
    print_success "Dependencias instaladas"
}

# Configurar variables de entorno
setup_environment() {
    print_status "Configurando variables de entorno..."
    
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_warning "Archivo .env creado"
        print_warning "⚠️  IMPORTANTE: Edita .env y añade tu token de Hugging Face"
    fi
    
    print_success "Variables de entorno configuradas"
}

# Descargar modelos
download_models() {
    print_status "Descargando modelos..."
    
    # Activar entorno conda
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate radox
    
    python scripts/download_models.py
    
    print_success "Modelos descargados"
}

# Función principal
main() {
    echo "🏥 Instalando RADOX con Conda"
    echo "============================="
    
    check_conda
    create_conda_env
    create_directories
    install_dependencies
    setup_environment
    
    # Verificar token de Hugging Face
    if grep -q "your_hf_token_here" .env; then
        print_warning "⚠️  Configuración requerida:"
        print_warning "1. Edita el archivo .env"
        print_warning "2. Añade tu token de Hugging Face"
        print_warning "3. Ejecuta: ./setup_conda.sh --continue"
        exit 0
    fi
    
    download_models
    
    print_success "🎉 ¡Instalación completada!"
    echo ""
    echo "📋 Próximos pasos:"
    echo "1. Activar entorno: conda activate radox"
    echo "2. Ejecutar backend: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    echo "3. Abrir: http://localhost:8000/docs"
    echo ""
    echo "🏥 ¡Listo para detectar neumonía!"
}

# Verificar argumentos
if [[ "$1" == "--continue" ]]; then
    download_models
    print_success "🎉 ¡Instalación completada!"
else
    main
fi 