@echo off
REM 🚀 RADOX - Instalador Automático para Windows
REM Sistema de Detección de Neumonía con IA

setlocal enabledelayedexpansion

REM Configurar colores
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Función para imprimir con colores
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Función para verificar comandos
:check_command
where %1 >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "%1 no está instalado. Por favor instálalo primero."
    exit /b 1
)
exit /b 0

REM Función para verificar versión de Python
:check_python_version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Python no está instalado. Por favor instala Python 3.11+"
    exit /b 1
)

REM Obtener versión de Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
for /f "tokens=1,2 delims=." %%a in ("%python_version%") do set "major_minor=%%a.%%b"

REM Verificar versión mínima (3.11)
if "%major_minor%" lss "3.11" (
    call :print_error "Python 3.11 o superior es requerido. Versión actual: %python_version%"
    exit /b 1
)

call :print_success "Python %python_version% detectado"
exit /b 0

REM Función para crear entorno conda
:create_conda_env
call :print_status "Creando entorno conda 'radox'..."

conda env list | findstr "radox" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_warning "El entorno 'radox' ya existe. ¿Quieres recrearlo? (y/N)"
    set /p response=
    if /i "!response!"=="y" (
        conda env remove -n radox -y
    ) else (
        call :print_status "Usando entorno existente"
        goto :eof
    )
)

conda create -n radox python=3.11 -y
if %errorlevel% neq 0 (
    call :print_error "Error al crear entorno conda"
    exit /b 1
)

call :print_success "Entorno conda 'radox' creado"
goto :eof

REM Función para instalar dependencias Python
:install_python_deps
call :print_status "Activando entorno conda..."

REM Activar entorno conda
call conda activate radox
if %errorlevel% neq 0 (
    call :print_error "Error al activar entorno conda"
    exit /b 1
)

call :print_status "Instalando dependencias Python..."
python -m pip install --upgrade pip

REM Instalar PyTorch primero
call :print_status "Instalando PyTorch..."
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
if %errorlevel% neq 0 (
    call :print_warning "Error al instalar PyTorch con CUDA, intentando sin CUDA..."
    conda install pytorch torchvision torchaudio cpuonly -c pytorch -y
)

REM Instalar otras dependencias
call :print_status "Instalando otras dependencias..."
pip install -r requirements.txt
if %errorlevel% neq 0 (
    call :print_error "Error al instalar dependencias Python"
    exit /b 1
)

call :print_success "Dependencias Python instaladas"
goto :eof

REM Función para instalar TorchXRayVision
:install_torchxrayvision
call :print_status "Instalando TorchXRayVision..."

REM Activar entorno
call conda activate radox

REM Instalar dependencias adicionales
conda install -c conda-forge matplotlib pillow scikit-image opencv -y

REM Instalar TorchXRayVision
pip install torchxrayvision
if %errorlevel% neq 0 (
    call :print_error "Error al instalar TorchXRayVision"
    exit /b 1
)

call :print_success "TorchXRayVision instalado"
goto :eof

REM Función para configurar frontend
:setup_frontend
call :print_status "Configurando frontend..."

if exist "Front_guide\ai-pneumonia-assistant" (
    cd Front_guide\ai-pneumonia-assistant
    
    call :print_status "Instalando dependencias Node.js..."
    npm install
    if %errorlevel% neq 0 (
        call :print_error "Error al instalar dependencias Node.js"
        exit /b 1
    )
    
    call :print_status "Construyendo frontend..."
    npm run build
    if %errorlevel% neq 0 (
        call :print_warning "Error al construir frontend"
    )
    
    cd ..\..
    call :print_success "Frontend configurado"
) else (
    call :print_warning "Directorio del frontend no encontrado, saltando..."
)
goto :eof

REM Función para crear archivo de configuración
:create_config
call :print_status "Creando archivo de configuración..."

if not exist ".env" (
    (
        echo # Configuración de RADOX
        echo HUGGINGFACE_TOKEN=tu_token_aqui
        echo MEDGEMMA_ENDPOINT=https://tu-endpoint.huggingface.cloud
        echo SECRET_KEY=clave_secreta_para_produccion_cambia_esto
        echo API_HOST=127.0.0.1
        echo API_PORT=8000
        echo DEBUG=false
    ) > .env
    
    call :print_success "Archivo .env creado"
    call :print_warning "IMPORTANTE: Edita el archivo .env con tus tokens reales"
) else (
    call :print_status "Archivo .env ya existe"
)
goto :eof

REM Función para crear directorios necesarios
:create_directories
call :print_status "Creando directorios necesarios..."

if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\models" mkdir "data\models"
if not exist "logs" mkdir "logs"
if not exist "static" mkdir "static"

call :print_success "Directorios creados"
goto :eof

REM Función para verificar instalación
:verify_installation
call :print_status "Verificando instalación..."

REM Activar entorno
call conda activate radox

REM Verificar Python
python -c "import torch, torchvision, torchxrayvision, fastapi, uvicorn" 2>nul
if %errorlevel% equ 0 (
    call :print_success "Todas las dependencias Python están instaladas"
) else (
    call :print_error "Algunas dependencias Python no están instaladas correctamente"
    exit /b 1
)

REM Verificar Node.js
if exist "Front_guide\ai-pneumonia-assistant\node_modules" (
    call :print_success "Dependencias Node.js están instaladas"
) else (
    call :print_warning "Dependencias Node.js no están instaladas"
)

exit /b 0

REM Función principal
:main
echo 🚀 RADOX - Instalador Automático para Windows
echo ================================================
echo.

REM Verificar sistema
call :print_status "Verificando sistema..."

REM Verificar comandos básicos
call :check_command "python" || exit /b 1
call :check_command "pip" || exit /b 1
call :check_command "conda" || exit /b 1
call :check_command "npm" || exit /b 1

REM Verificar versión de Python
call :check_python_version || exit /b 1

call :print_success "Sistema verificado correctamente"
echo.

REM Instalación
call :create_conda_env
call :install_python_deps
call :install_torchxrayvision
call :setup_frontend
call :create_config
call :create_directories

echo.

REM Verificación final
call :verify_installation
if %errorlevel% equ 0 (
    echo 🎉 ¡Instalación completada exitosamente!
    echo.
    echo 🚀 Para ejecutar RADOX:
    echo    1. Activa el entorno: conda activate radox
    echo    2. Ejecuta: run_dev_all.bat
    echo.
    echo 🔧 Para solo el backend:
    echo    run_dev.bat
    echo.
    echo 📚 Documentación disponible en:
    echo    - README.md
    echo    - GUIA_INSTALACION.md
    echo.
    echo ⚠️  IMPORTANTE: Edita el archivo .env con tus tokens reales
    echo.
    call :print_success "¡RADOX está listo para usar! 🏥✨"
    
    echo.
    echo Presiona cualquier tecla para continuar...
    pause >nul
) else (
    call :print_error "La instalación no se completó correctamente"
    echo.
    echo Presiona cualquier tecla para continuar...
    pause >nul
    exit /b 1
)

goto :eof

REM Ejecutar función principal
call :main
