"""
Rutas de API para Detección de Neumonía
Endpoints para subir imágenes y obtener predicciones de neumonía
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import json
from loguru import logger

from backend.utils.image_processing import validate_medical_image, ImageProcessor
from backend.dependencies import get_detection_service

router = APIRouter()

# Modelos Pydantic para validación
class PatientInfo(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120, description="Edad del paciente")
    gender: Optional[str] = Field(None, pattern="^(M|F|Male|Female|Masculino|Femenino)$", description="Sexo del paciente")
    symptoms: Optional[str] = Field(None, max_length=500, description="Síntomas del paciente")
    clinical_history: Optional[str] = Field(None, max_length=1000, description="Historia clínica relevante")

class DetectionResponse(BaseModel):
    case_id: str
    timestamp: str
    filename: str
    prediction: Dict[str, Any]
    case_data: Dict[str, Any]
    processing_info: Dict[str, Any]

class DetectionRequest(BaseModel):
    patient_info: Optional[PatientInfo] = None
    # include_similar_cases: bool = Field(default=True, description="Incluir casos similares en respuesta")  # Comentado
    # similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Umbral de similaridad")  # Comentado
    # max_similar_cases: int = Field(default=5, ge=1, le=10, description="Máximo número de casos similares")  # Comentado

@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Detectar neumonía en radiografía",
    description="Sube una imagen radiográfica y obtiene predicción de neumonía usando IA",
    tags=["Detección"]
)
async def detect_pneumonia(
    file: UploadFile = File(..., description="Archivo de imagen (JPG, PNG, DICOM)"),
    patient_info: Optional[str] = Form(None, description="Información del paciente en JSON"),
    # include_similar_cases: bool = Form(True, description="Incluir casos similares"),  # Comentado
    # similarity_threshold: float = Form(0.7, description="Umbral de similaridad"),  # Comentado
    # max_similar_cases: int = Form(5, description="Máximo número de casos similares"),  # Comentado
    detection_service = Depends(get_detection_service),
    # similarity_service: SimilarCasesService = Depends()  # Comentado
):
    """
    Detectar neumonía en una radiografía de tórax
    
    - **file**: Archivo de imagen (formatos soportados: JPG, PNG, DICOM)
    - **patient_info**: Información adicional del paciente (JSON opcional)
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo requerido"
            )
        
        # Leer datos del archivo
        file_content = await file.read()
        
        # Validar imagen médica
        validation_result = validate_medical_image(file_content, file.filename)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Imagen no válida: {', '.join(validation_result['errors'])}"
            )
        
        # Procesar información del paciente si se proporciona
        patient_data = None
        if patient_info:
            try:
                patient_data = json.loads(patient_info)
                # Validar con Pydantic
                PatientInfo(**patient_data)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato JSON inválido en patient_info"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Datos de paciente inválidos: {str(e)}"
                )
        
        # Ejecutar detección con CNN
        logger.info(f"Procesando detección para archivo: {file.filename}")
        detection_result = await detection_service.detect_pneumonia(
            image_data=file_content,
            filename=file.filename,
            patient_info=patient_data
        )
        
        # Preparar respuesta (sin casos similares)
        response_data = {
            **detection_result
            # "similar_cases": []  # Si el modelo espera este campo, dejarlo vacío
        }
        
        # Añadir caso a la base de datos para futuras búsquedas
        try:
            case_data = detection_result.get('case_data', {})
            # await similarity_service.add_case_to_database(case_data) # Comentado
        except Exception as e:
            logger.warning(f"Error al añadir caso a la base de datos: {e}")
            # No fallar la respuesta por esto
        
        logger.success(f"Detección completada para caso: {detection_result.get('case_id')}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en detección de neumonía: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )



@router.get(
    "/validate-image",
    summary="Validar imagen médica",
    description="Valida si una imagen es adecuada para análisis",
    tags=["Validación"]
)
async def validate_image_endpoint(
    file: UploadFile = File(..., description="Archivo de imagen a validar")
):
    """
    Validar imagen médica antes del análisis
    
    - **file**: Archivo de imagen a validar
    
    Retorna información sobre la validez de la imagen y posibles problemas.
    """
    try:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo requerido"
            )
        
        file_content = await file.read()
        validation_result = validate_medical_image(file_content, file.filename)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "filename": file.filename,
                "validation": validation_result,
                "recommendations": _get_validation_recommendations(validation_result)
            }
        )
        
    except Exception as e:
        logger.error(f"Error en validación de imagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en validación: {str(e)}"
        )

@router.get(
    "/supported-formats",
    summary="Formatos soportados",
    description="Lista los formatos de imagen soportados",
    tags=["Información"]
)
async def get_supported_formats():
    """
    Obtener lista de formatos de imagen soportados
    
    Retorna información sobre los formatos que acepta el sistema.
    """
    return {
        "supported_formats": [
            {
                "extension": "jpg",
                "mime_type": "image/jpeg",
                "description": "Imagen JPEG estándar",
                "max_size": "10MB"
            },
            {
                "extension": "jpeg", 
                "mime_type": "image/jpeg",
                "description": "Imagen JPEG estándar",
                "max_size": "10MB"
            },
            {
                "extension": "png",
                "mime_type": "image/png", 
                "description": "Imagen PNG",
                "max_size": "10MB"
            },
            {
                "extension": "dicom",
                "mime_type": "application/dicom",
                "description": "Imagen médica DICOM",
                "max_size": "50MB"
            },
            {
                "extension": "dcm",
                "mime_type": "application/dicom",
                "description": "Imagen médica DICOM",
                "max_size": "50MB"
            }
        ],
        "recommendations": [
            "Use imágenes DICOM para mejor precisión diagnóstica",
            "Asegúrese de que las imágenes tengan buena calidad y resolución",
            "Las radiografías de tórax frontales (PA/AP) son las más adecuadas",
            "Evite imágenes con marcas de agua o anotaciones superpuestas"
        ]
    }

@router.get(
    "/statistics",
    summary="Estadísticas del sistema",
    description="Obtiene estadísticas de uso y rendimiento del sistema",
    tags=["Estadísticas"]
)
async def get_system_statistics(
    detection_service = Depends(get_detection_service)
):
    """
    Obtener estadísticas del sistema de detección
    
    Retorna métricas de uso, precisión y estado de los servicios.
    """
    try:
        # Obtener estadísticas de servicios
        detection_stats = detection_service.get_service_info()
        
        return {
            "detection_service": detection_stats,
            "system_status": {
                "api_version": "1.0.0",
                "model_status": detection_stats.get("model_status", "unknown"),
                "services_healthy": detection_stats.get("model_status") == "loaded"
            }
        }
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

def _get_validation_recommendations(validation_result: Dict[str, Any]) -> List[str]:
    """Generar recomendaciones basadas en validación"""
    recommendations = []
    
    if validation_result["errors"]:
        recommendations.append("Corrija los errores antes de proceder con el análisis")
    
    if validation_result["warnings"]:
        recommendations.extend([
            "Revise las advertencias para obtener mejores resultados",
            "Considere usar una imagen de mejor calidad si está disponible"
        ])
    
    dimensions = validation_result.get("dimensions")
    if dimensions:
        height, width = dimensions[:2]
        if height < 512 or width < 512:
            recommendations.append("Para mejores resultados, use imágenes de al menos 512x512 píxeles")
    
    if validation_result["format"] not in ["dicom", "dcm"]:
        recommendations.append("Las imágenes DICOM proporcionan mejor información diagnóstica")
    
    if not recommendations:
        recommendations.append("La imagen es adecuada para análisis")
    
    return recommendations 