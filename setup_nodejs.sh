#!/bin/bash

# RADOX Node.js - Script de Instalación
# Sistema de Detección de Neumonía con IA en Node.js

set -e

echo "🚀 RADOX Node.js - Iniciando instalación..."
echo "============================================="

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

# Verificar prerrequisitos
check_prerequisites() {
    print_status "Verificando prerrequisitos..."
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js no está instalado"
        print_status "Instalando Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    local node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 16 ]; then
        print_error "Se requiere Node.js 16 o superior. Versión actual: $(node --version)"
        exit 1
    fi
    
    # Verificar npm
    if ! command -v npm &> /dev/null; then
        print_error "npm no está instalado"
        exit 1
    fi
    
    print_success "Node.js $(node --version) y npm $(npm --version) están instalados"
}

# Crear estructura de directorios
create_directories() {
    print_status "Creando estructura de directorios..."
    
    # Directorios principales
    mkdir -p src/{services,utils}
    mkdir -p public/js
    mkdir -p uploads
    mkdir -p models
    mkdir -p logs
    mkdir -p scripts
    
    print_success "Estructura de directorios creada"
}

# Instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias de Node.js..."
    
    # Verificar si package.json existe
    if [ ! -f "package.json" ]; then
        print_error "package.json no encontrado"
        exit 1
    fi
    
    # Instalar dependencias
    npm install
    
    print_success "Dependencias instaladas correctamente"
}

# Configurar variables de entorno
setup_environment() {
    print_status "Configurando variables de entorno..."
    
    if [ ! -f "config.env" ]; then
        print_error "Archivo config.env no encontrado"
        exit 1
    fi
    
    # Verificar token de Hugging Face
    if grep -q "your_hf_token_here" config.env; then
        print_warning "⚠️  CONFIGURACIÓN REQUERIDA:"
        print_warning "1. Edita el archivo config.env"
        print_warning "2. Añade tu token de Hugging Face"
        print_warning "3. Ejecuta: ./setup_nodejs.sh --continue"
        exit 0
    fi
    
    print_success "Variables de entorno configuradas"
}

# Crear archivo de modelo mock (para demostración)
create_mock_model() {
    print_status "Creando modelo mock para demostración..."
    
    mkdir -p models
    touch models/pneumonia_resnet50.h5
    
    print_warning "⚠️  Usando modelo mock para demostración"
    print_warning "Para usar un modelo real, coloca tu archivo .h5 en ./models/"
    print_warning "Y convierte a TensorFlow.js con: tensorflowjs_converter"
    
    print_success "Modelo mock creado"
}

# Verificar configuración final
verify_setup() {
    print_status "Verificando configuración final..."
    
    # Verificar archivos principales
    local required_files=("server.js" "package.json" "config.env" "public/index.html")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Archivo requerido no encontrado: $file"
            exit 1
        fi
    done
    
    # Verificar directorios
    local required_dirs=("src/services" "src/utils" "public/js" "uploads" "models")
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "Directorio requerido no encontrado: $dir"
            exit 1
        fi
    done
    
    print_success "Configuración verificada correctamente"
}

# Función principal
main() {
    echo "🏥 Instalando RADOX Node.js - Sistema de Detección de Neumonía"
    echo "=============================================================="
    
    check_prerequisites
    create_directories
    install_dependencies
    setup_environment
    create_mock_model
    verify_setup
    
    print_success "🎉 ¡Instalación completada!"
    echo ""
    echo "📋 Próximos pasos:"
    echo "1. Ejecutar: npm start"
    echo "2. Abrir: http://localhost:3000"
    echo "3. ¡Comenzar a detectar neumonía!"
    echo ""
    echo "💡 Comandos útiles:"
    echo "   • npm start      - Iniciar servidor"
    echo "   • npm run dev    - Modo desarrollo"
    echo "   • npm test       - Ejecutar pruebas"
}

# Verificar argumentos
if [[ "$1" == "--continue" ]]; then
    setup_environment
    create_mock_model
    verify_setup
    print_success "🎉 ¡Configuración completada!"
elif [[ "$1" == "--help" ]]; then
    echo "RADOX Node.js - Script de Instalación"
    echo ""
    echo "Uso: ./setup_nodejs.sh [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --continue   Continuar después de configurar token HF"
    echo "  --help       Mostrar esta ayuda"
    echo ""
else
    main
fi 