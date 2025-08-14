#!/bin/bash

# 🚀 RADOX - Instalador Automático
# Sistema de Detección de Neumonía con IA

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
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

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 no está instalado. Por favor instálalo primero."
        return 1
    fi
    return 0
}

# Función para verificar versión de Python
check_python_version() {
    local python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    local required_version="3.11"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python $required_version o superior es requerido. Versión actual: $python_version"
        return 1
    fi
    
    print_success "Python $python_version detectado"
    return 0
}

# Función para crear entorno conda
create_conda_env() {
    print_status "Creando entorno conda 'radox'..."
    
    if conda env list | grep -q "radox"; then
        print_warning "El entorno 'radox' ya existe. ¿Quieres recrearlo? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            conda env remove -n radox -y
        else
            print_status "Usando entorno existente"
            return 0
        fi
    fi
    
    conda create -n radox python=3.11 -y
    print_success "Entorno conda 'radox' creado"
}

# Función para instalar dependencias Python
install_python_deps() {
    print_status "Activando entorno conda..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate radox
    
    print_status "Instalando dependencias Python..."
    pip install --upgrade pip
    
    # Instalar PyTorch primero
    print_status "Instalando PyTorch..."
    conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
    
    # Instalar otras dependencias
    print_status "Instalando otras dependencias..."
    pip install -r requirements.txt
    
    print_success "Dependencias Python instaladas"
}

# Función para instalar TorchXRayVision
install_torchxrayvision() {
    print_status "Instalando TorchXRayVision..."
    
    # Activar entorno
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate radox
    
    # Instalar dependencias adicionales
    conda install -c conda-forge matplotlib pillow scikit-image opencv -y
    
    # Instalar TorchXRayVision
    pip install torchxrayvision
    
    print_success "TorchXRayVision instalado"
}

# Función para configurar frontend
setup_frontend() {
    print_status "Configurando frontend..."
    
    if [ -d "Front_guide/ai-pneumonia-assistant" ]; then
        cd Front_guide/ai-pneumonia-assistant
        
        print_status "Instalando dependencias Node.js..."
        npm install
        
        print_status "Construyendo frontend..."
        npm run build
        
        cd ../..
        print_success "Frontend configurado"
    else
        print_warning "Directorio del frontend no encontrado, saltando..."
    fi
}

# Función para crear archivo de configuración
create_config() {
    print_status "Creando archivo de configuración..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Configuración de RADOX
HUGGINGFACE_TOKEN=tu_token_aqui
MEDGEMMA_ENDPOINT=https://tu-endpoint.huggingface.cloud
SECRET_KEY=clave_secreta_para_produccion_cambia_esto
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=false
EOF
        print_success "Archivo .env creado"
        print_warning "IMPORTANTE: Edita el archivo .env con tus tokens reales"
    else
        print_status "Archivo .env ya existe"
    fi
}

# Función para crear directorios necesarios
create_directories() {
    print_status "Creando directorios necesarios..."
    
    mkdir -p data/uploads
    mkdir -p data/models
    mkdir -p logs
    mkdir -p static
    
    print_success "Directorios creados"
}

# Función para hacer scripts ejecutables
make_executable() {
    print_status "Haciendo scripts ejecutables..."
    
    chmod +x run_dev_all.sh
    chmod +x run_dev.sh
    chmod +x scripts/*.sh
    
    print_success "Scripts hechos ejecutables"
}

# Función para verificar instalación
verify_installation() {
    print_status "Verificando instalación..."
    
    # Activar entorno
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate radox
    
    # Verificar Python
    if python3 -c "import torch, torchvision, torchxrayvision, fastapi, uvicorn" 2>/dev/null; then
        print_success "Todas las dependencias Python están instaladas"
    else
        print_error "Algunas dependencias Python no están instaladas correctamente"
        return 1
    fi
    
    # Verificar Node.js
    if [ -d "Front_guide/ai-pneumonia-assistant/node_modules" ]; then
        print_success "Dependencias Node.js están instaladas"
    else
        print_warning "Dependencias Node.js no están instaladas"
    fi
    
    return 0
}

# Función principal
main() {
    echo "🚀 RADOX - Instalador Automático"
    echo "=================================="
    echo ""
    
    # Verificar sistema
    print_status "Verificando sistema..."
    
    # Verificar comandos básicos
    check_command "python3" || exit 1
    check_command "pip3" || exit 1
    check_command "conda" || exit 1
    check_command "npm" || exit 1
    
    # Verificar versión de Python
    check_python_version || exit 1
    
    print_success "Sistema verificado correctamente"
    echo ""
    
    # Instalación
    create_conda_env
    install_python_deps
    install_torchxrayvision
    setup_frontend
    create_config
    create_directories
    make_executable
    
    echo ""
    
    # Verificación final
    if verify_installation; then
        echo "🎉 ¡Instalación completada exitosamente!"
        echo ""
        echo "🚀 Para ejecutar RADOX:"
        echo "   1. Activa el entorno: conda activate radox"
        echo "   2. Ejecuta: ./run_dev_all.sh"
        echo ""
        echo "🔧 Para solo el backend:"
        echo "   ./run_dev.sh"
        echo ""
        echo "📚 Documentación disponible en:"
        echo "   - README.md"
        echo "   - GUIA_INSTALACION.md"
        echo ""
        echo "⚠️  IMPORTANTE: Edita el archivo .env con tus tokens reales"
        echo ""
        print_success "¡RADOX está listo para usar! 🏥✨"
    else
        print_error "La instalación no se completó correctamente"
        exit 1
    fi
}

# Ejecutar función principal
main "$@"
