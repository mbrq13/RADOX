#!/bin/bash

# 🚀 RADOX - Constructor de Ejecutable
# Script principal para crear el paquete ejecutable

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

# Función para mostrar ayuda
show_help() {
    echo "🚀 RADOX - Constructor de Ejecutable"
    echo "====================================="
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help          Mostrar esta ayuda"
    echo "  -b, --backend       Construir solo el backend (recomendado)"
    echo "  -f, --full          Construir backend + frontend completo"
    echo "  -c, --clean         Limpiar archivos de build anteriores"
    echo "  -i, --install       Instalar dependencias antes de construir"
    echo ""
    echo "Ejemplos:"
    echo "  $0 -b              # Construir solo backend (más rápido)"
    echo "  $0 -f              # Construir completo"
    echo "  $0 -c              # Limpiar build anterior"
    echo "  $0 -i -b           # Instalar dependencias y construir backend"
    echo ""
}

# Función para limpiar build anterior
clean_build() {
    print_status "Limpiando directorios de build anteriores..."
    
    if [ -d "build" ]; then
        rm -rf build
        print_success "Directorio build eliminado"
    fi
    
    if [ -d "dist" ]; then
        rm -rf dist
        print_success "Directorio dist eliminado"
    fi
    
    if [ -d "__pycache__" ]; then
        rm -rf __pycache__
        print_success "Cache de Python eliminado"
    fi
    
    print_success "Limpieza completada"
}

# Función para instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias..."
    
    # Verificar si estamos en entorno conda
    if [[ "$CONDA_DEFAULT_ENV" != "radox" ]]; then
        print_warning "No estás en el entorno conda 'radox'"
        print_status "Activando entorno conda..."
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate radox
    fi
    
    # Instalar PyInstaller
    print_status "Instalando PyInstaller..."
    pip install pyinstaller
    
    # Verificar dependencias del proyecto
    print_status "Verificando dependencias del proyecto..."
    pip install -r requirements.txt
    
    print_success "Dependencias instaladas"
}

# Función para construir solo backend
build_backend_only() {
    print_status "Construyendo solo el backend..."
    
    # Ejecutar script de construcción del backend
    python scripts/build_backend_only.py
    
    if [ $? -eq 0 ]; then
        print_success "Backend construido exitosamente!"
        echo ""
        echo "📁 Ejecutable en: dist/RADOX_Backend/"
        echo "🚀 Para ejecutar: dist/RADOX_Backend/RADOX_Backend.sh"
        echo "🌐 API disponible en: http://localhost:8000"
        echo "📚 Documentación en: http://localhost:8000/docs"
    else
        print_error "Error al construir el backend"
        exit 1
    fi
}

# Función para construir completo
build_full() {
    print_status "Construyendo RADOX completo..."
    
    # Ejecutar script de construcción completo
    python scripts/build_executable.py
    
    if [ $? -eq 0 ]; then
        print_success "RADOX completo construido exitosamente!"
        echo ""
        echo "📁 Ejecutable en: dist/RADOX/"
        echo "🚀 Para ejecutar: dist/RADOX/RADOX.sh"
        echo "🌐 Frontend disponible en: http://localhost:3000"
        echo "🔧 API disponible en: http://localhost:8000"
    else
        print_error "Error al construir RADOX completo"
        exit 1
    fi
}

# Función para verificar sistema
check_system() {
    print_status "Verificando sistema..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 no está instalado"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 no está disponible"
        exit 1
    fi
    
    # Verificar conda
    if ! command -v conda &> /dev/null; then
        print_error "conda no está instalado"
        exit 1
    fi
    
    # Verificar Node.js (para build completo)
    if ! command -v npm &> /dev/null; then
        print_warning "npm no está disponible (necesario para build completo)"
    fi
    
    print_success "Sistema verificado"
}

# Función para crear paquete de distribución
create_distribution_package() {
    print_status "Creando paquete de distribución..."
    
    # Crear nombre del paquete con fecha
    DATE=$(date +%Y%m%d_%H%M%S)
    PACKAGE_NAME="RADOX_Backend_${DATE}.tar.gz"
    
    if [ -d "dist/RADOX_Backend" ]; then
        cd dist
        tar -czf "../${PACKAGE_NAME}" RADOX_Backend/
        cd ..
        
        print_success "Paquete creado: ${PACKAGE_NAME}"
        print_status "Tamaño: $(du -h ${PACKAGE_NAME} | cut -f1)"
    else
        print_error "Directorio de distribución no encontrado"
        exit 1
    fi
}

# Función principal
main() {
    echo "🚀 RADOX - Constructor de Ejecutable"
    echo "====================================="
    echo ""
    
    # Verificar argumentos
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # Variables de control
    CLEAN_BUILD=false
    INSTALL_DEPS=false
    BUILD_BACKEND=false
    BUILD_FULL=false
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--clean)
                CLEAN_BUILD=true
                shift
                ;;
            -i|--install)
                INSTALL_DEPS=true
                shift
                ;;
            -b|--backend)
                BUILD_BACKEND=true
                shift
                ;;
            -f|--full)
                BUILD_FULL=true
                shift
                ;;
            *)
                print_error "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Verificar que se especifique un tipo de build
    if [ "$BUILD_BACKEND" = false ] && [ "$BUILD_FULL" = false ]; then
        print_error "Debes especificar un tipo de build (-b o -f)"
        show_help
        exit 1
    fi
    
    # Verificar sistema
    check_system
    
    # Limpiar build anterior si se solicita
    if [ "$CLEAN_BUILD" = true ]; then
        clean_build
    fi
    
    # Instalar dependencias si se solicita
    if [ "$INSTALL_DEPS" = true ]; then
        install_dependencies
    fi
    
    # Construir según la opción seleccionada
    if [ "$BUILD_BACKEND" = true ]; then
        build_backend_only
        create_distribution_package
    elif [ "$BUILD_FULL" = true ]; then
        build_full
    fi
    
    echo ""
    print_success "¡Construcción completada exitosamente! 🎉"
    echo ""
    echo "📦 Para distribuir:"
    echo "   - Copia la carpeta dist/ a otra máquina"
    echo "   - Ejecuta el script .sh o .bat correspondiente"
    echo "   - No requiere instalación adicional"
    echo ""
    echo "🔧 Para desarrollo:"
    echo "   - Usa: conda activate radox && ./run_dev_all.sh"
    echo ""
}

# Ejecutar función principal
main "$@"
