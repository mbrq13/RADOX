#!/bin/bash

# RADOX - Script de Instalación Automática
# Sistema de Detección de Neumonía con IA

set -e  # Salir en cualquier error

echo "🚀 RADOX - Iniciando instalación automática..."
echo "============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
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

# Verificar prerrequisitos
check_prerequisites() {
    print_status "Verificando prerrequisitos..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 no está instalado"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 no está instalado"
        exit 1
    fi
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker no está instalado. Instalando..."
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose no está instalado. Instalando..."
        sudo apt-get install -y docker-compose
    fi
    
    print_success "Prerrequisitos verificados"
}

# Crear estructura de directorios
create_directories() {
    print_status "Creando estructura de directorios..."
    
    # Backend
    mkdir -p backend/{api/{routes},models,services,config,utils}
    
    # Frontend
    mkdir -p frontend/static/{css,js,images}
    
    # Data
    mkdir -p data/{models,uploads}
    
    # Scripts
    mkdir -p scripts
    
    # Tests
    mkdir -p tests/{unit,integration}
    
    # Logs
    mkdir -p logs
    
    print_success "Estructura de directorios creada"
}

# Instalar dependencias Python
install_python_deps() {
    print_status "Instalando dependencias Python..."
    
    print_warning "⚠️  IMPORTANTE: Asegúrate de tener activado tu entorno conda"
    print_warning "Ejecuta: conda activate radox"
    read -p "¿Tienes activado el entorno conda? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Por favor activa tu entorno conda primero"
        exit 1
    fi
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias
    pip install -r requirements.txt
    
    print_success "Dependencias Python instaladas"
}

# Configurar variables de entorno
setup_environment() {
    print_status "Configurando variables de entorno..."
    
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_warning "Archivo .env creado desde ejemplo"
        print_warning "¡IMPORTANTE! Edita .env y añade tu token de Hugging Face"
    fi
    
    print_success "Variables de entorno configuradas"
}

# Descargar modelos pre-entrenados
download_models() {
    print_status "Descargando modelos pre-entrenados..."
    
    python scripts/download_models.py
    
    print_success "Modelos descargados"
}

# Construir imágenes Docker
build_docker_images() {
    print_status "Construyendo imágenes Docker..."
    
    docker-compose build
    
    print_success "Imágenes Docker construidas"
}

# Función principal
main() {
    echo "🏥 Instalando RADOX - Sistema de Detección de Neumonía"
    echo "======================================================"
    
    check_prerequisites
    create_directories
    install_python_deps
    setup_environment
    
    # Solo proceder si existe el token de HF
    if grep -q "your_hf_token_here" .env; then
        print_warning "⚠️  Configuración requerida:"
        print_warning "1. Edita el archivo .env"
        print_warning "2. Añade tu token de Hugging Face"
        print_warning "3. Ejecuta: ./setup.sh --continue"
        exit 0
    fi
    
    download_models
    build_docker_images
    
    print_success "🎉 ¡Instalación completada!"
    echo ""
    echo "📋 Próximos pasos:"
    echo "1. Ejecutar: ./run.sh"
    echo "2. Abrir: http://localhost:8000/docs"
    echo "3. ¡Comenzar a detectar neumonía!"
}

# Verificar argumentos
if [[ "$1" == "--continue" ]]; then
    download_models
    build_docker_images
    print_success "🎉 ¡Instalación completada!"
else
    main
fi 