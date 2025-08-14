#!/usr/bin/env python3
"""
Script para construir el ejecutable completo de RADOX
Incluye backend, frontend y todas las dependencias
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
import platform

class RADOXBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "Front_guide" / "ai-pneumonia-assistant"
        
    def clean_build(self):
        """Limpiar directorios de build anteriores"""
        print("🧹 Limpiando directorios de build...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
    def install_dependencies(self):
        """Instalar dependencias Python"""
        print("📦 Instalando dependencias Python...")
        
        # Instalar PyInstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Instalar dependencias del proyecto
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(self.project_root / "requirements.txt")], check=True)
        
    def build_frontend(self):
        """Construir el frontend Next.js"""
        print("🌐 Construyendo frontend...")
        
        if not self.frontend_dir.exists():
            print("❌ Directorio del frontend no encontrado")
            return False
            
        # Instalar dependencias Node.js
        subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
        
        # Construir para producción
        subprocess.run(["npm", "run", "build"], cwd=self.frontend_dir, check=True)
        
        return True
        
    def create_main_script(self):
        """Crear script principal que ejecute todo"""
        print("📝 Creando script principal...")
        
        main_script = self.build_dir / "radox_main.py"
        
        script_content = '''#!/usr/bin/env python3
"""
RADOX - Sistema de Detección de Neumonía con IA
Script principal para ejecutable standalone
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RADOXRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_port = 8000
        self.frontend_port = 3000
        self.backend_process = None
        self.frontend_process = None
        
    def setup_environment(self):
        """Configurar variables de entorno"""
        os.environ["PYTHONPATH"] = str(self.project_root)
        os.environ["RADOX_ENV"] = "standalone"
        
        # Crear directorios necesarios
        (self.project_root / "data" / "uploads").mkdir(parents=True, exist_ok=True)
        (self.project_root / "data" / "models").mkdir(parents=True, exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        
    def start_backend(self):
        """Iniciar backend FastAPI"""
        try:
            from backend.main import app
            
            # Configurar CORS para standalone
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Montar archivos estáticos
            app.mount("/static", StaticFiles(directory=str(self.project_root / "static")), name="static")
            
            logger.info(f"🚀 Iniciando backend en puerto {self.backend_port}")
            uvicorn.run(app, host="127.0.0.1", port=self.backend_port, log_level="info")
            
        except Exception as e:
            logger.error(f"❌ Error al iniciar backend: {e}")
            
    def start_frontend(self):
        """Iniciar frontend Next.js"""
        try:
            frontend_dir = self.project_root / "frontend"
            if frontend_dir.exists():
                logger.info(f"🌐 Iniciando frontend en puerto {self.frontend_port}")
                subprocess.run([
                    "npm", "start", "--", "--port", str(self.frontend_port)
                ], cwd=frontend_dir, check=True)
            else:
                logger.warning("⚠️ Frontend no encontrado, solo backend disponible")
                
        except Exception as e:
            logger.error(f"❌ Error al iniciar frontend: {e}")
            
    def open_browser(self):
        """Abrir navegador después de un delay"""
        time.sleep(3)
        try:
            webbrowser.open(f"http://localhost:{self.frontend_port}")
        except:
            logger.info(f"🌐 Abre tu navegador en: http://localhost:{self.frontend_port}")
            
    def run(self):
        """Ejecutar RADOX completo"""
        print("🚀 Iniciando RADOX...")
        
        self.setup_environment()
        
        # Iniciar backend en thread separado
        backend_thread = threading.Thread(target=self.start_backend, daemon=True)
        backend_thread.start()
        
        # Iniciar frontend en thread separado
        frontend_thread = threading.Thread(target=self.start_frontend, daemon=True)
        frontend_thread.start()
        
        # Abrir navegador
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        try:
            print("✅ RADOX iniciado correctamente!")
            print(f"🌐 Frontend: http://localhost:{self.frontend_port}")
            print(f"🔧 API: http://localhost:{self.backend_port}")
            print("Presiona Ctrl+C para detener...")
            
            # Mantener el programa corriendo
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\\n🛑 Deteniendo RADOX...")
            sys.exit(0)

if __name__ == "__main__":
    runner = RADOXRunner()
    runner.run()
'''
        
        with open(main_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        return main_script
        
    def create_spec_file(self):
        """Crear archivo .spec para PyInstaller"""
        print("📋 Creando archivo .spec...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Archivos y directorios a incluir
a = Analysis(
    ['{self.build_dir}/radox_main.py'],
    pathex=[str(self.project_root)],
    binaries=[],
    datas=[
        # Incluir directorios completos
        (str(self.backend_dir), 'backend'),
        (str(self.frontend_dir / '.next'), 'frontend/.next'),
        (str(self.frontend_dir / 'public'), 'frontend/public'),
        (str(self.project_root / 'models'), 'models'),
        (str(self.project_root / 'data'), 'data'),
        (str(self.project_root / 'config.env'), '.'),
        (str(self.project_root / 'env.example'), '.'),
        (str(self.project_root / 'README.md'), '.'),
        (str(self.project_root / 'LICENSE'), '.'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'fastapi.middleware.cors',
        'fastapi.staticfiles',
        'pydantic',
        'pydantic_settings',
        'torch',
        'torchvision',
        'torchxrayvision',
        'opencv-python',
        'PIL',
        'numpy',
        'pandas',
        'scikit-image',
        'transformers',
        'huggingface_hub',
        'loguru',
        'python-multipart',
        'aiofiles',
        'requests',
        'tqdm',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RADOX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RADOX',
)
'''
        
        spec_file = self.build_dir / "RADOX.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
        return spec_file
        
    def build_executable(self):
        """Construir el ejecutable usando PyInstaller"""
        print("🔨 Construyendo ejecutable...")
        
        spec_file = self.create_spec_file()
        
        # Ejecutar PyInstaller
        subprocess.run([
            "pyinstaller",
            "--clean",
            str(spec_file)
        ], check=True)
        
    def create_installer_script(self):
        """Crear script de instalación"""
        print("📜 Creando script de instalación...")
        
        if platform.system() == "Windows":
            installer = self.dist_dir / "install_radox.bat"
            content = '''@echo off
echo 🚀 Instalando RADOX...
echo.
echo 📦 Verificando dependencias...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instala Python 3.11+
    pause
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está disponible. Por favor instala pip
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas
echo.
echo 🔧 Instalando RADOX...

REM Instalar dependencias
pip install -r requirements.txt

echo.
echo ✅ RADOX instalado correctamente!
echo.
echo 🚀 Para ejecutar RADOX:
echo 1. Activa el entorno: conda activate radox
echo 2. Ejecuta: python scripts/run_dev_all.sh
echo.
pause
'''
        else:
            installer = self.dist_dir / "install_radox.sh"
            content = '''#!/bin/bash

echo "🚀 Instalando RADOX..."
echo ""
echo "📦 Verificando dependencias..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python 3.11+"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está disponible. Por favor instala pip"
    exit 1
fi

echo "✅ Dependencias verificadas"
echo ""
echo "🔧 Instalando RADOX..."

# Instalar dependencias
pip3 install -r requirements.txt

echo ""
echo "✅ RADOX instalado correctamente!"
echo ""
echo "🚀 Para ejecutar RADOX:"
echo "1. Activa el entorno: conda activate radox"
echo "2. Ejecuta: ./run_dev_all.sh"
echo ""
'''
        
        with open(installer, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Hacer ejecutable en Unix
        if platform.system() != "Windows":
            os.chmod(installer, 0o755)
            
    def create_readme(self):
        """Crear README para el ejecutable"""
        print("📖 Creando README...")
        
        readme_content = '''# 🚀 RADOX - Sistema de Detección de Neumonía con IA

## 📋 Descripción
RADOX es un sistema completo de detección de neumonía usando inteligencia artificial, que combina:
- **Backend FastAPI** con modelo CNN TorchXRayVision
- **Frontend Next.js** con interfaz moderna
- **Modelo MedGemma** para generación de informes médicos

## 🎯 Características
- ✅ Detección automática de neumonía en radiografías
- ✅ Generación de mapas de calor (heatmaps)
- ✅ Chat con IA para análisis médico
- ✅ Interfaz web responsive y moderna
- ✅ API REST completa
- ✅ Soporte para múltiples formatos de imagen

## 🚀 Instalación Rápida

### Opción 1: Ejecutable Standalone (Recomendado)
1. Descarga el archivo RADOX.exe (Windows) o RADOX (Linux/Mac)
2. Ejecuta directamente - no requiere instalación
3. Abre tu navegador en http://localhost:3000

### Opción 2: Instalación Manual
1. Ejecuta `install_radox.bat` (Windows) o `./install_radox.sh` (Linux/Mac)
2. Sigue las instrucciones en pantalla
3. Ejecuta `python scripts/run_dev_all.sh`

## 🔧 Requisitos del Sistema
- **RAM**: 4GB mínimo, 8GB recomendado
- **Almacenamiento**: 10GB espacio libre
- **Sistema**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Navegador**: Chrome, Firefox, Safari, Edge (últimas versiones)

## 📁 Estructura del Proyecto
```
RADOX/
├── backend/           # API FastAPI
├── frontend/          # Interfaz Next.js
├── models/            # Modelos de IA
├── data/              # Datos y uploads
├── scripts/           # Scripts de utilidad
└── docs/              # Documentación
```

## 🌐 Uso
1. **Iniciar**: Ejecuta RADOX.exe o `./RADOX`
2. **Acceder**: Abre http://localhost:3000 en tu navegador
3. **Subir imagen**: Arrastra una radiografía de tórax
4. **Analizar**: Haz clic en "Analizar" para detección de neumonía
5. **Chat**: Usa el chat para consultas adicionales con MedGemma

## 🔑 Configuración
Crea un archivo `.env` con:
```env
HUGGINGFACE_TOKEN=tu_token_aqui
MEDGEMMA_ENDPOINT=https://tu-endpoint.huggingface.cloud
SECRET_KEY=clave_secreta_aqui
```

## 🆘 Soporte
- **Documentación**: README.md
- **Issues**: GitHub Issues
- **Email**: soporte@radox.com

## 📄 Licencia
MIT License - Ver LICENSE para más detalles

---
**RADOX Team** - Sistema de IA para Medicina 🏥✨
'''
        
        readme_file = self.dist_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
    def copy_essential_files(self):
        """Copiar archivos esenciales al directorio de distribución"""
        print("📁 Copiando archivos esenciales...")
        
        # Archivos de configuración
        essential_files = [
            "requirements.txt",
            "config.env",
            "env.example",
            "README.md",
            "LICENSE",
            "run_dev_all.sh",
            "run_dev.sh"
        ]
        
        for file_name in essential_files:
            src = self.project_root / file_name
            if src.exists():
                shutil.copy2(src, self.dist_dir)
                
        # Copiar directorio de scripts
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            shutil.copytree(scripts_dir, self.dist_dir / "scripts")
            
        # Copiar directorio de modelos
        models_dir = self.project_root / "models"
        if models_dir.exists():
            shutil.copytree(models_dir, self.dist_dir / "models")
            
    def create_launcher(self):
        """Crear script launcher para el ejecutable"""
        print("🚀 Creando launcher...")
        
        if platform.system() == "Windows":
            launcher = self.dist_dir / "RADOX.bat"
            content = '''@echo off
echo 🚀 Iniciando RADOX...
echo.
echo 📋 Verificando archivos...

if not exist "RADOX.exe" (
    echo ❌ RADOX.exe no encontrado
    echo Por favor ejecuta install_radox.bat primero
    pause
    exit /b 1
)

echo ✅ Archivos verificados
echo.
echo 🌐 Iniciando RADOX...
echo.
echo 📱 Abriendo navegador automáticamente...
echo 🔧 API disponible en: http://localhost:8000
echo 🌐 Frontend disponible en: http://localhost:3000
echo.
echo Presiona Ctrl+C para detener RADOX
echo.

RADOX.exe
pause
'''
        else:
            launcher = self.dist_dir / "RADOX.sh"
            content = '''#!/bin/bash

echo "🚀 Iniciando RADOX..."
echo ""
echo "📋 Verificando archivos..."

if [ ! -f "./RADOX" ]; then
    echo "❌ RADOX no encontrado"
    echo "Por favor ejecuta ./install_radox.sh primero"
    exit 1
fi

echo "✅ Archivos verificados"
echo ""
echo "🌐 Iniciando RADOX..."
echo ""
echo "📱 Abriendo navegador automáticamente..."
echo "🔧 API disponible en: http://localhost:8000"
echo "🌐 Frontend disponible en: http://localhost:3000"
echo ""
echo "Presiona Ctrl+C para detener RADOX"
echo ""

./RADOX
'''
            
        with open(launcher, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Hacer ejecutable en Unix
        if platform.system() != "Windows":
            os.chmod(launcher, 0o755)
            
    def build(self):
        """Proceso completo de build"""
        print("🚀 Iniciando build de RADOX...")
        print("=" * 50)
        
        try:
            # 1. Limpiar build anterior
            self.clean_build()
            
            # 2. Instalar dependencias
            self.install_dependencies()
            
            # 3. Construir frontend
            if not self.build_frontend():
                print("⚠️ Frontend no construido, continuando solo con backend...")
                
            # 4. Crear script principal
            self.create_main_script()
            
            # 5. Construir ejecutable
            self.build_executable()
            
            # 6. Crear archivos adicionales
            self.create_installer_script()
            self.create_readme()
            self.copy_essential_files()
            self.create_launcher()
            
            print("=" * 50)
            print("✅ Build completado exitosamente!")
            print(f"📁 Ejecutable en: {self.dist_dir}")
            print(f"🚀 Para ejecutar: {self.dist_dir / 'RADOX.bat' if platform.system() == 'Windows' else self.dist_dir / 'RADOX.sh'}")
            
        except Exception as e:
            print(f"❌ Error durante el build: {e}")
            raise

def main():
    """Función principal"""
    builder = RADOXBuilder()
    builder.build()

if __name__ == "__main__":
    main()
