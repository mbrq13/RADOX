"""
RADOX - Sistema de Detección de Neumonía con IA
Archivo principal de la API FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from loguru import logger

from backend.config.settings import Settings
from backend.api.routes import pneumonia, reports
from backend.models.cnn_model import CNNModel
from backend.services.pneumonia_detection import PneumoniaDetectionService
from backend.services.report_generation import ReportGenerationService
from backend.dependencies import set_services

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/radox.log", rotation="1 day", retention="30 days")

# Variables globales para servicios (importadas desde dependencies.py)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    
    logger.info("🚀 Iniciando RADOX API...")
    
    try:
        # Inicializar configuración
        settings = Settings()
        
        # Inicializar modelos
        logger.info("📦 Cargando modelo CNN...")
        cnn_model_instance = CNNModel(settings.model_path)
        await cnn_model_instance.load_model()
        
        # Inicializar servicios
        logger.info("🔧 Inicializando servicios...")
        detection_service_instance = PneumoniaDetectionService(cnn_model_instance)
        report_service_instance = ReportGenerationService(settings.huggingface_token, settings.medgemma_model)
        
        # Establecer servicios en dependencies
        set_services(cnn_model_instance, detection_service_instance, report_service_instance)
        
        logger.success("✅ RADOX API iniciada correctamente")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar RADOX API: {e}")
        raise
    finally:
        logger.info("🛑 Cerrando RADOX API...")

# Crear aplicación FastAPI
app = FastAPI(
    title="RADOX API",
    description="Sistema de Detección de Neumonía con IA y Generación de Informes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de seguridad
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Permitir todos los hosts en desarrollo
)

# Montar archivos estáticos
os.makedirs("data/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")

# Incluir rutas
app.include_router(pneumonia.router, prefix="/api/v1", tags=["Pneumonia Detection"])
app.include_router(reports.router, prefix="/api/v1", tags=["Medical Reports"])

# Las dependencias están definidas en backend/dependencies.py

# Rutas básicas
@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "🏥 RADOX API - Sistema de Detección de Neumonía",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificación de salud del sistema"""
    try:
        from backend.dependencies import cnn_model, detection_service, report_service
        
        health_status = {
            "status": "healthy",
            "services": {
                "api": "running",
                "cnn_model": "loaded" if cnn_model and cnn_model.is_loaded else "not_loaded",
                "detection_service": "available" if detection_service else "unavailable",
                "report_service": "available" if report_service else "unavailable"
            }
        }
        
        # Verificar si todos los servicios están funcionando
        all_healthy = all([
            cnn_model and cnn_model.is_loaded,
            detection_service,
            report_service
        ])
        
        if not all_healthy:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=503, detail="Servicio no disponible")

@app.get("/api/v1/info")
async def api_info():
    """Información detallada de la API"""
    return {
        "name": "RADOX",
        "description": "Sistema de Detección de Neumonía con IA",
        "version": "1.0.0",
        "features": [
            "Detección de neumonía con CNN",
            "Generación de informes médicos con MedGemma",
            "Procesamiento de imágenes DICOM/PNG/JPG"
        ],
        "endpoints": {
            "detection": "/api/v1/detect",
            "generate_report": "/api/v1/report",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    # Configuración para desarrollo
    settings = Settings()
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 