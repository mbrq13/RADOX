#!/usr/bin/env python3
"""
Script para construir solo el backend de RADOX como ejecutable
Versión simplificada para distribución
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

class RADOXBackendBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.backend_dir = self.project_root / "backend"
        
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
        
    def create_main_script(self):
        """Crear script principal simplificado"""
        print("📝 Creando script principal...")
        
        main_script = self.build_dir / "radox_backend.py"
        
        script_content = '''#!/usr/bin/env python3
"""
RADOX Backend - Sistema de Detección de Neumonía con IA
Script principal para ejecutable standalone
"""

import os
import sys
import webbrowser
import time
from pathlib import Path
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar variables de entorno"""
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)
    os.environ["RADOX_ENV"] = "standalone"
    
    # Crear directorios necesarios
    project_root = Path(__file__).parent
    (project_root / "data" / "uploads").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "models").mkdir(parents=True, exist_ok=True)
    (project_root / "logs").mkdir(exist_ok=True)
    
    # Crear archivo .env si no existe
    env_file = project_root / ".env"
    if not env_file.exists():
        env_content = """# Configuración de RADOX
HUGGINGFACE_TOKEN=tu_token_aqui
MEDGEMMA_ENDPOINT=https://tu-endpoint.huggingface.cloud
SECRET_KEY=clave_secreta_para_produccion
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=false
"""
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        logger.info("📝 Archivo .env creado. Por favor configúralo con tus tokens.")

def main():
    """Función principal"""
    print("🚀 Iniciando RADOX Backend...")
    print("=" * 50)
    
    try:
        # Configurar entorno
        setup_environment()
        
        # Importar y configurar la app
        from backend.main import app
        
        # Configurar CORS para standalone
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Configurar archivos estáticos
        from fastapi.staticfiles import StaticFiles
        project_root = Path(__file__).parent
        app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")
        
        # Configurar puerto
        port = int(os.environ.get("API_PORT", 8000))
        host = os.environ.get("API_HOST", "127.0.0.1")
        
        print(f"🔧 Iniciando API en http://{host}:{port}")
        print(f"📚 Documentación: http://{host}:{port}/docs")
        print(f"🔍 ReDoc: http://{host}:{port}/redoc")
        print("=" * 50)
        print("✅ RADOX Backend iniciado correctamente!")
        print("🌐 Para usar el frontend, abre http://localhost:3000")
        print("🛑 Presiona Ctrl+C para detener...")
        print("=" * 50)
        
        # Abrir navegador después de un delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f"http://{host}:{port}/docs")
            except:
                logger.info(f"🌐 Abre tu navegador en: http://{host}:{port}/docs")
        
        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Iniciar servidor
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        logger.error("💡 Asegúrate de que todas las dependencias estén instaladas")
        input("Presiona Enter para continuar...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error al iniciar RADOX: {e}")
        input("Presiona Enter para continuar...")
        sys.exit(1)

if __name__ == "__main__":
    main()
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
    ['{self.build_dir}/radox_backend.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[
        # Incluir directorios completos
        ('{self.backend_dir}', 'backend'),
        ('{self.project_root}/models', 'models'),
        ('{self.project_root}/data', 'data'),
        ('{self.project_root}/config.env', '.'),
        ('{self.project_root}/env.example', '.'),
        ('{self.project_root}/README.md', '.'),
        ('{self.project_root}/LICENSE', '.'),
        ('{self.project_root}/requirements.txt', '.'),
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
        'pydicom',
        'matplotlib',
        'cv2',
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
    name='RADOX_Backend',
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
    name='RADOX_Backend',
)
'''
        
        spec_file = self.build_dir / "RADOX_Backend.spec"
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
        
    def create_launcher(self):
        """Crear script launcher para el ejecutable"""
        print("🚀 Creando launcher...")
        
        if platform.system() == "Windows":
            launcher = self.dist_dir / "RADOX_Backend.bat"
            content = '''@echo off
echo 🚀 Iniciando RADOX Backend...
echo.
echo 📋 Verificando archivos...

if not exist "RADOX_Backend.exe" (
    echo ❌ RADOX_Backend.exe no encontrado
    echo Por favor ejecuta install_radox.bat primero
    pause
    exit /b 1
)

echo ✅ Archivos verificados
echo.
echo 🌐 Iniciando RADOX Backend...
echo.
echo 📱 Abriendo navegador automáticamente...
echo 🔧 API disponible en: http://localhost:8000
echo 📚 Documentación: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener RADOX
echo.

RADOX_Backend.exe
pause
'''
        else:
            launcher = self.dist_dir / "RADOX_Backend.sh"
            content = '''#!/bin/bash

echo "🚀 Iniciando RADOX Backend..."
echo ""
echo "📋 Verificando archivos..."

if [ ! -f "./RADOX_Backend" ]; then
    echo "❌ RADOX_Backend no encontrado"
    echo "Por favor ejecuta ./install_radox.sh primero"
    exit 1
fi

echo "✅ Archivos verificados"
echo ""
echo "🌐 Iniciando RADOX Backend..."
echo ""
echo "📱 Abriendo navegador automáticamente..."
echo "🔧 API disponible en: http://localhost:8000"
echo "📚 Documentación: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener RADOX"
echo ""

./RADOX_Backend
'''
            
        with open(launcher, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Hacer ejecutable en Unix
        if platform.system() != "Windows":
            os.chmod(launcher, 0o755)
            
    def create_readme(self):
        """Crear README para el ejecutable"""
        print("📖 Creando README...")
        
        readme_content = '''# 🚀 RADOX Backend - Sistema de Detección de Neumonía con IA

## 📋 Descripción
RADOX Backend es la API principal del sistema de detección de neumonía usando inteligencia artificial.

## 🎯 Características
- ✅ API FastAPI completa y documentada
- ✅ Modelo CNN TorchXRayVision para detección
- ✅ Generación de mapas de calor (heatmaps)
- ✅ Integración con MedGemma para informes
- ✅ Soporte para múltiples formatos de imagen
- ✅ API REST con documentación automática

## 🚀 Instalación Rápida

### Opción 1: Ejecutable Standalone (Recomendado)
1. Descarga el archivo RADOX_Backend.exe (Windows) o RADOX_Backend (Linux/Mac)
2. Ejecuta directamente - no requiere instalación
3. Abre tu navegador en http://localhost:8000/docs

### Opción 2: Instalación Manual
1. Ejecuta `install_radox.bat` (Windows) o `./install_radox.sh` (Linux/Mac)
2. Sigue las instrucciones en pantalla
3. Ejecuta `python scripts/run_dev.sh`

## 🔧 Requisitos del Sistema
- **RAM**: 4GB mínimo, 8GB recomendado
- **Almacenamiento**: 10GB espacio libre
- **Sistema**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## 🌐 Uso
1. **Iniciar**: Ejecuta RADOX_Backend.exe o `./RADOX_Backend`
2. **Acceder**: Abre http://localhost:8000/docs en tu navegador
3. **API**: Usa los endpoints para análisis de imágenes
4. **Documentación**: ReDoc disponible en http://localhost:8000/redoc

## 🔑 Configuración
Crea un archivo `.env` con:
```env
HUGGINGFACE_TOKEN=tu_token_aqui
MEDGEMMA_ENDPOINT=https://tu-endpoint.huggingface.cloud
SECRET_KEY=clave_secreta_aqui
```

## 📚 Endpoints Principales
- `POST /api/v1/detect` - Detección de neumonía
- `GET /api/v1/patients` - Lista de pacientes
- `GET /api/v1/studies` - Estudios médicos
- `POST /api/v1/reports` - Generación de informes

## 🆘 Soporte
- **Documentación**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Issues**: GitHub Issues

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
            "LICENSE"
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
            
    def build(self):
        """Proceso completo de build"""
        print("🚀 Iniciando build de RADOX Backend...")
        print("=" * 50)
        
        try:
            # 1. Limpiar build anterior
            self.clean_build()
            
            # 2. Instalar dependencias
            self.install_dependencies()
            
            # 3. Crear script principal
            self.create_main_script()
            
            # 4. Construir ejecutable
            self.build_executable()
            
            # 5. Crear archivos adicionales
            self.create_launcher()
            self.create_readme()
            self.copy_essential_files()
            
            print("=" * 50)
            print("✅ Build completado exitosamente!")
            print(f"📁 Ejecutable en: {self.dist_dir}")
            print(f"🚀 Para ejecutar: {self.dist_dir / 'RADOX_Backend.bat' if platform.system() == 'Windows' else self.dist_dir / 'RADOX_Backend.sh'}")
            print("🌐 API disponible en: http://localhost:8000")
            print("📚 Documentación en: http://localhost:8000/docs")
            
        except Exception as e:
            print(f"❌ Error durante el build: {e}")
            raise

def main():
    """Función principal"""
    builder = RADOXBackendBuilder()
    builder.build()

if __name__ == "__main__":
    main()
