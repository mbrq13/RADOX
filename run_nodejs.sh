#!/bin/bash

# RADOX Node.js - Script de Ejecución
# Iniciar sistema de detección de neumonía

set -e

echo "🏥 RADOX Node.js - Iniciando sistema..."
echo "====================================="

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

# Verificar configuración
check_setup() {
    print_status "Verificando configuración del sistema..."
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js no está instalado. Ejecuta ./setup_nodejs.sh primero"
        exit 1
    fi
    
    # Verificar archivos principales
    if [ ! -f "server.js" ]; then
        print_error "server.js no encontrado. Ejecuta ./setup_nodejs.sh primero"
        exit 1
    fi
    
    if [ ! -f "package.json" ]; then
        print_error "package.json no encontrado. Ejecuta ./setup_nodejs.sh primero"
        exit 1
    fi
    
    if [ ! -f "config.env" ]; then
        print_error "config.env no encontrado. Ejecuta ./setup_nodejs.sh primero"
        exit 1
    fi
    
    # Verificar node_modules
    if [ ! -d "node_modules" ]; then
        print_warning "Dependencias no instaladas. Instalando..."
        npm install
    fi
    
    # Verificar token de Hugging Face
    if grep -q "your_hf_token_here" config.env; then
        print_warning "⚠️  Token de Hugging Face no configurado"
        print_warning "Edita config.env y añade tu token de Hugging Face"
        print_warning "El sistema funcionará con informes básicos sin el token"
    fi
    
    print_success "Sistema configurado correctamente"
}

# Verificar puertos disponibles
check_ports() {
    local port=3000
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Puerto $port está en uso. Intentando detener proceso existente..."
        
        # Intentar matar proceso en el puerto
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        if [ ! -z "$pid" ]; then
            kill -9 $pid 2>/dev/null || true
            sleep 2
        fi
        
        # Verificar nuevamente
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_error "No se pudo liberar el puerto $port"
            exit 1
        fi
    fi
    
    print_success "Puerto $port disponible"
}

# Iniciar servidor en modo desarrollo
start_dev() {
    print_status "Iniciando RADOX en modo desarrollo..."
    
    check_setup
    check_ports
    
    print_status "Iniciando servidor con nodemon..."
    
    # Establecer variables de entorno para desarrollo
    export NODE_ENV=development
    
    # Iniciar con nodemon para recarga automática
    if command -v nodemon &> /dev/null; then
        nodemon server.js
    else
        print_warning "nodemon no encontrado, instalando..."
        npm install -g nodemon
        nodemon server.js
    fi
}

# Iniciar servidor en modo producción
start_prod() {
    print_status "Iniciando RADOX en modo producción..."
    
    check_setup
    check_ports
    
    print_status "Iniciando servidor..."
    
    # Establecer variables de entorno para producción
    export NODE_ENV=production
    
    # Iniciar servidor
    node server.js
}

# Mostrar estado del sistema
show_status() {
    print_status "Estado del sistema RADOX..."
    
    local port=3000
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        print_success "RADOX ejecutándose en puerto $port (PID: $pid)"
        print_status "URLs disponibles:"
        echo "   🌐 Interfaz web: http://localhost:$port"
        echo "   🔧 Health check: http://localhost:$port/health"
        echo "   📊 API docs: Disponible en el frontend"
    else
        print_warning "RADOX no está ejecutándose en puerto $port"
    fi
}

# Detener servidor
stop_server() {
    print_status "Deteniendo RADOX..."
    
    local port=3000
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        print_status "Deteniendo proceso $pid..."
        kill -15 $pid 2>/dev/null || true
        
        # Esperar a que termine gracefully
        sleep 3
        
        # Forzar si es necesario
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Forzando terminación..."
            kill -9 $pid 2>/dev/null || true
        fi
        
        print_success "RADOX detenido"
    else
        print_warning "RADOX no estaba ejecutándose"
    fi
}

# Reiniciar servidor
restart_server() {
    print_status "Reiniciando RADOX..."
    stop_server
    sleep 2
    start_prod
}

# Mostrar logs
show_logs() {
    print_status "Mostrando logs de RADOX..."
    
    if [ -d "logs" ]; then
        tail -f logs/*.log 2>/dev/null || print_warning "No hay archivos de log disponibles"
    else
        print_warning "Directorio de logs no encontrado"
    fi
}

# Ejecutar pruebas
run_tests() {
    print_status "Ejecutando pruebas..."
    
    if command -v npm &> /dev/null; then
        npm test
    else
        print_error "npm no está disponible"
        exit 1
    fi
}

# Mostrar información del sistema
show_info() {
    echo "🏥 RADOX Node.js - Sistema de Detección de Neumonía"
    echo "=================================================="
    echo ""
    echo "📊 Información del sistema:"
    echo "   • Node.js: $(node --version 2>/dev/null || echo 'No instalado')"
    echo "   • npm: $(npm --version 2>/dev/null || echo 'No instalado')"
    echo "   • Directorio: $(pwd)"
    echo ""
    echo "📁 Archivos principales:"
    [ -f "server.js" ] && echo "   ✅ server.js" || echo "   ❌ server.js"
    [ -f "package.json" ] && echo "   ✅ package.json" || echo "   ❌ package.json"
    [ -f "config.env" ] && echo "   ✅ config.env" || echo "   ❌ config.env"
    [ -d "node_modules" ] && echo "   ✅ node_modules" || echo "   ❌ node_modules"
    echo ""
}

# Función principal
main() {
    case "$1" in
        --dev|-d)
            start_dev
            ;;
        --prod|-p|"")
            start_prod
            ;;
        --status|-s)
            show_status
            ;;
        --stop)
            stop_server
            ;;
        --restart|-r)
            restart_server
            ;;
        --logs|-l)
            show_logs
            ;;
        --test|-t)
            run_tests
            ;;
        --info|-i)
            show_info
            ;;
        --help|-h)
            echo "RADOX Node.js - Script de Ejecución"
            echo ""
            echo "Uso: ./run_nodejs.sh [OPCIÓN]"
            echo ""
            echo "Opciones:"
            echo "  --dev, -d        Iniciar en modo desarrollo (con nodemon)"
            echo "  --prod, -p       Iniciar en modo producción (por defecto)"
            echo "  --status, -s     Mostrar estado del sistema"
            echo "  --stop           Detener el servidor"
            echo "  --restart, -r    Reiniciar el servidor"
            echo "  --logs, -l       Mostrar logs en tiempo real"
            echo "  --test, -t       Ejecutar pruebas"
            echo "  --info, -i       Mostrar información del sistema"
            echo "  --help, -h       Mostrar esta ayuda"
            echo ""
            echo "Ejemplos:"
            echo "  ./run_nodejs.sh              # Iniciar en producción"
            echo "  ./run_nodejs.sh --dev        # Iniciar en desarrollo"
            echo "  ./run_nodejs.sh --status     # Ver estado"
            echo ""
            ;;
        *)
            print_error "Opción desconocida: $1"
            echo "Usa --help para ver las opciones disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@" 