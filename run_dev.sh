#!/bin/bash

# RADOX - Script de Ejecución en Desarrollo
# Ejecuta el backend sin Docker

set -e

echo "🏥 RADOX - Iniciando en modo desarrollo..."
echo "=========================================="

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

# Verificar entorno conda
check_conda() {
    if [[ "$CONDA_DEFAULT_ENV" != "radox" ]]; then
        print_warning "Entorno conda 'radox' no está activado"
        print_status "Activando entorno conda..."
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate radox
    fi
    
    print_success "Entorno conda activado: $CONDA_DEFAULT_ENV"
}

# Verificar archivo .env
check_env() {
    if [ ! -f ".env" ]; then
        print_error "Archivo .env no encontrado"
        print_warning "Ejecuta ./setup_conda.sh primero"
        exit 1
    fi
    
    if grep -q "your_hf_token_here" .env; then
        print_warning "⚠️  Token de Hugging Face no configurado"
        print_warning "Edita el archivo .env y añade tu token"
    fi
    
    print_success "Archivo .env encontrado"
}

# Verificar modelos
check_models() {
    if [ ! -d "data/models" ] || [ -z "$(ls -A data/models 2>/dev/null)" ]; then
        print_warning "Modelos no encontrados"
        print_status "Descargando modelos..."
        python scripts/download_models.py
    fi
    
    print_success "Modelos verificados"
}

# Función principal
main() {
    check_conda
    check_env
    check_models
    
    print_status "Iniciando servidor de desarrollo..."
    print_status "API estará disponible en: http://localhost:8000"
    print_status "Documentación en: http://localhost:8000/docs"
    print_status "Presiona Ctrl+C para detener"
    echo ""
    
    # Ejecutar uvicorn desde el directorio raíz
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
}

# Capturar Ctrl+C para parada limpia
trap 'echo ""; print_status "Deteniendo servidor..."; exit 0' SIGINT SIGTERM

main 