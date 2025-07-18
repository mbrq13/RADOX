"""
Configuración de RADOX
Gestión de configuración usando Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
import os
import json

class Settings(BaseSettings):
    """Configuración principal de RADOX"""
    
    # Configuración de la API
    api_host: str = Field(default="0.0.0.0", description="Host de la API")
    api_port: int = Field(default=8000, description="Puerto de la API")
    web_port: int = Field(default=8080, description="Puerto del frontend")
    debug: bool = Field(default=False, description="Modo debug")
    log_level: str = Field(default="INFO", description="Nivel de logging")
    
    # Configuración de Hugging Face
    huggingface_token: str = Field(..., description="Token de Hugging Face", env="HUGGINGFACE_TOKEN")
    medgemma_model: str = Field(
        default="google/medgemma-7b", 
        description="Modelo MedGemma a usar"
    )
    
    # Rutas de modelos y datos
    model_path: str = Field(default="./data/models/", description="Ruta de modelos")
    cnn_model_name: str = Field(
        default="pneumonia_resnet50.h5", 
        description="Nombre del modelo CNN"
    )
    
    # Configuración médica
    confidence_threshold: float = Field(
        default=0.8, 
        description="Umbral de confianza para diagnóstico"
    )
    report_language: str = Field(
        default="spanish", 
        description="Idioma para los informes"
    )
    
    # Configuración de archivos
    max_file_size: int = Field(
        default=10485760,  # 10MB
        description="Tamaño máximo de archivo en bytes"
    )
    allowed_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "dicom", "dcm"],
        description="Extensiones de archivo permitidas"
    )
    
    @field_validator('allowed_extensions', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            else:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v
    upload_path: str = Field(
        default="./data/uploads/", 
        description="Ruta de archivos subidos"
    )
    
    # Configuración de seguridad
    secret_key: str = Field(..., description="Clave secreta para JWT", env="SECRET_KEY")
    cors_origins: List[str] = Field(
        default=["http://localhost:8080", "http://127.0.0.1:8080"],
        description="Orígenes permitidos para CORS"
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            else:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    # Configuración de rendimiento
    max_workers: int = Field(default=4, description="Máximo número de workers")
    batch_size: int = Field(default=1, description="Tamaño de lote para inferencia")
    gpu_enabled: bool = Field(default=False, description="Habilitar GPU")
    
    class Config:
        """Configuración de Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @property
    def cnn_model_path(self) -> str:
        """Ruta completa al modelo CNN"""
        return os.path.join(self.model_path, self.cnn_model_name)
    
    @property
    def is_production(self) -> bool:
        """Verifica si está en modo producción"""
        return not self.debug and self.log_level == "INFO"
    
    def validate_paths(self) -> bool:
        """Valida que las rutas necesarias existan"""
        paths_to_check = [
            self.model_path,
            self.upload_path
        ]
        
        for path in paths_to_check:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        
        return True
    
    def get_allowed_mime_types(self) -> List[str]:
        """Obtiene los tipos MIME permitidos"""
        mime_mapping = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg", 
            "png": "image/png",
            "dicom": "application/dicom",
            "dcm": "application/dicom"
        }
        
        return [mime_mapping.get(ext, "application/octet-stream") 
                for ext in self.allowed_extensions]

# Instancia global de configuración
settings = Settings() 