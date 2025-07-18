#!/bin/bash

# RADOX - Script de Ejecución
# Iniciar sistema de detección de neumonía

set -e

echo "🏥 RADOX - Iniciando sistema..."
echo "==============================="

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

# Verificar si el sistema está configurado
check_setup() {
    print_status "Verificando configuración del sistema..."
    
    if [ ! -f ".env" ]; then
        print_error "Archivo .env no encontrado. Ejecuta ./setup.sh primero"
        exit 1
    fi
    
    if [ ! -d "data/models" ]; then
        print_error "Modelos no encontrados. Ejecuta ./setup.sh primero"
        exit 1
    fi
    
    print_success "Sistema configurado correctamente"
}

# Mostrar estado de Docker
check_docker_status() {
    print_status "Verificando Docker..."
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker no está funcionando. Iniciando Docker..."
        sudo systemctl start docker
        sleep 3
    fi
    
    print_success "Docker está funcionando"
}

# Detener servicios existentes
stop_existing_services() {
    print_status "Deteniendo servicios existentes..."
    
    docker-compose down 2>/dev/null || true
    
    # Matar procesos que puedan estar usando el puerto
    sudo fuser -k 8000/tcp 2>/dev/null || true
    
    print_success "Servicios existentes detenidos"
}

# Iniciar servicios Docker
start_docker_services() {
    print_status "Iniciando servicios Docker..."
    
    # Cargar variables de entorno
    export $(cat .env | xargs)
    
    # Iniciar servicios principales
    docker-compose up -d
    
    print_success "Servicios Docker iniciados"
}

# Verificar salud de los servicios
check_service_health() {
    print_status "Verificando salud de los servicios..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "API está funcionando"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "API no responde después de $max_attempts intentos"
            print_status "Mostrando logs del API..."
            docker-compose logs radox-api
            exit 1
        fi
        
        print_status "Esperando API... (intento $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Mostrar información del sistema
show_system_info() {
    echo ""
    echo "🎉 ¡RADOX está funcionando!"
    echo "=========================="
    echo ""
    echo "📍 URLs del sistema:"
    echo "   🔧 API: http://localhost:8000"
    echo "   📊 API Docs: http://localhost:8000/docs"
    echo ""
    echo "📋 Comandos útiles:"
    echo "   📜 Ver logs: docker-compose logs -f"
    echo "   ⏹️  Detener: docker-compose down"
    echo "   🔄 Reiniciar: ./run.sh"
    echo ""
    echo "🏥 ¡Listo para detectar neumonía!"
}

# Función para parada limpia
cleanup() {
    print_status "Deteniendo servicios..."
    docker-compose down
    exit 0
}

# Función principal
main() {
    # Capturar Ctrl+C para parada limpia
    trap cleanup SIGINT SIGTERM
    
    check_setup
    check_docker_status
    stop_existing_services
    start_docker_services
    check_service_health
    show_system_info
    
    # Modo monitoring
    if [[ "$1" == "--monitor" ]]; then
        print_status "Modo monitoring activado. Presiona Ctrl+C para salir."
        docker-compose logs -f
    else
        print_status "Sistema iniciado. Usa --monitor para ver logs en tiempo real."
    fi
}

# Verificar argumentos
case "$1" in
    --stop)
        print_status "Deteniendo RADOX..."
        docker-compose down
        print_success "RADOX detenido"
        ;;
    --restart)
        print_status "Reiniciando RADOX..."
        docker-compose down
        docker-compose up -d
        check_service_health
        print_success "RADOX reiniciado"
        ;;
    --logs)
        docker-compose logs -f
        ;;
    --status)
        docker-compose ps
        ;;
    --help)
        echo "RADOX - Sistema de Detección de Neumonía"
        echo ""
        echo "Uso: ./run.sh [OPCIÓN]"
        echo ""
        echo "Opciones:"
        echo "  --stop     Detener el sistema"
        echo "  --restart  Reiniciar el sistema"
        echo "  --logs     Mostrar logs en tiempo real"
        echo "  --status   Mostrar estado de los servicios"
        echo "  --monitor  Iniciar con monitoreo de logs"
        echo "  --help     Mostrar esta ayuda"
        echo ""
        ;;
    *)
        main "$@"
        ;;
esac 