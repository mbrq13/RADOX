"""
Rutas de API para Generación de Informes Médicos
Endpoints para generar informes usando MedGemma y gestionar reportes
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from loguru import logger
from backend.dependencies import get_report_service

router = APIRouter()

# Modelos Pydantic para validación
class ReportRequest(BaseModel):
    case_id: str = Field(..., description="ID del caso para generar informe")
    detection_result: Dict[str, Any] = Field(..., description="Resultado de detección de neumonía")
    patient_info: Optional[Dict[str, Any]] = Field(None, description="Información adicional del paciente")
    language: str = Field(default="spanish", pattern="^(spanish|english)$", description="Idioma del informe")
    report_type: str = Field(default="complete", pattern="^(complete|summary|detailed)$", description="Tipo de informe")

class ReportResponse(BaseModel):
    report_id: str
    case_id: str
    timestamp: str
    generated_by: str
    report_sections: Dict[str, str]
    full_report: str
    metadata: Dict[str, Any]
    quality_score: Dict[str, float]



@router.post(
    "/generate",
    response_model=ReportResponse,
    summary="Generar informe médico",
    description="Genera un informe médico completo usando MedGemma",
    tags=["Informes"]
)
async def generate_medical_report(
    request: ReportRequest,
    report_service = Depends(get_report_service)
    # similarity_service: SimilarCasesService = Depends()  # Comentado
):
    try:
        logger.info(f"Generando informe médico para caso: {request.case_id}")
        
        # similar_cases = None
        # if request.include_similar_cases:
        #     try:
        #         case_data = request.detection_result.get('case_data', {})
        #         similar_cases_result = await similarity_service.find_similar_cases(
        #             case_data=case_data,
        #             n_results=5,
        #             similarity_threshold=0.7
        #         )
        #         similar_cases = similar_cases_result.get('similar_cases', [])
        #         logger.info(f"Incluyendo {len(similar_cases)} casos similares en contexto")
        #     except Exception as e:
        #         logger.warning(f"Error al obtener casos similares para informe: {e}")
        #         similar_cases = []
        
        # Generar informe médico SOLO con la predicción
        report_result = await report_service.generate_medical_report(
            detection_result=request.detection_result,
            patient_info=request.patient_info,
            language=request.language
        )
        
        logger.success(f"Informe generado: {report_result.get('report_id')}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=report_result
        )
        
    except Exception as e:
        logger.error(f"Error en generación de informe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar informe: {str(e)}"
        )


#         )
#         
#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content=result
#         )
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error al obtener casos similares para {case_id}: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error en búsqueda: {str(e)}"
#         )

@router.get(
    "/report/{report_id}",
    summary="Obtener informe por ID",
    description="Recupera un informe médico previamente generado",
    tags=["Informes"]
)
async def get_report_by_id(
    report_id: str
):
    """
    Obtener informe médico por ID
    
    - **report_id**: ID único del informe
    
    Retorna el informe médico completo si existe.
    """
    # Nota: En implementación completa, esto requeriría un storage persistente
    # Por ahora retornamos error ya que los informes no se almacenan
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Almacenamiento de informes no implementado en esta versión"
    )

@router.get(
    "/templates",
    summary="Plantillas de informes",
    description="Obtiene plantillas disponibles para informes médicos",
    tags=["Plantillas"]
)
async def get_report_templates():
    """
    Obtener plantillas de informes disponibles
    
    Retorna lista de plantillas y formatos de informes soportados.
    """
    return {
        "templates": [
            {
                "id": "complete",
                "name": "Informe Completo",
                "description": "Informe médico completo con todas las secciones",
                "sections": [
                    "Datos del Paciente",
                    "Técnica de Estudio", 
                    "Hallazgos Radiológicos",
                    "Impresión Diagnóstica",
                    "Recomendaciones Clínicas",
                    "Notas Adicionales"
                ],
                "estimated_length": "500-800 palabras"
            },
            {
                "id": "summary",
                "name": "Resumen Ejecutivo",
                "description": "Resumen conciso con hallazgos principales",
                "sections": [
                    "Hallazgos Principales",
                    "Impresión Diagnóstica",
                    "Recomendaciones"
                ],
                "estimated_length": "200-400 palabras"
            },
            {
                "id": "detailed",
                "name": "Informe Detallado",
                "description": "Informe extenso con análisis profundo",
                "sections": [
                    "Información Completa del Paciente",
                    "Metodología de Análisis",
                    "Hallazgos Detallados",
                    "Análisis Comparativo",
                    "Impresión Diagnóstica Extendida",
                    "Recomendaciones Específicas",
                    "Seguimiento Propuesto"
                ],
                "estimated_length": "800-1200 palabras"
            }
        ],
        "supported_languages": ["spanish", "english"],
        "customization_options": [
            "Incluir casos similares",
            "Nivel de detalle técnico",
            "Formato de presentación",
            "Secciones opcionales"
        ]
    }

@router.get(
    "/export-formats",
    summary="Formatos de exportación",
    description="Lista formatos disponibles para exportar informes",
    tags=["Exportación"]
)
async def get_export_formats():
    """
    Obtener formatos de exportación disponibles
    
    Retorna lista de formatos soportados para exportar informes.
    """
    return {
        "formats": [
            {
                "format": "json",
                "mime_type": "application/json",
                "description": "Formato JSON estructurado",
                "features": ["Datos estructurados", "Fácil integración", "Metadata completa"]
            },
            {
                "format": "pdf",
                "mime_type": "application/pdf",
                "description": "Documento PDF formateado",
                "features": ["Formato profesional", "Listo para imprimir", "Header/Footer personalizable"],
                "status": "planned"
            },
            {
                "format": "html",
                "mime_type": "text/html",
                "description": "Página HTML formateada",
                "features": ["Visualización web", "Estilos personalizables", "Enlaces interactivos"],
                "status": "planned"
            },
            {
                "format": "docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Documento Microsoft Word",
                "features": ["Editable", "Formato profesional", "Compatible con Office"],
                "status": "planned"
            }
        ],
        "current_support": ["json"],
        "planned_features": [
            "Plantillas personalizables",
            "Logos institucionales",
            "Firmas digitales",
            "Exportación batch"
        ]
    }

@router.get(
    "/quality-metrics",
    summary="Métricas de calidad",
    description="Obtiene métricas de calidad para informes generados",
    tags=["Calidad"]
)
async def get_quality_metrics():
    """
    Obtener métricas de calidad del sistema de informes
    
    Retorna estadísticas sobre la calidad de los informes generados.
    """
    return {
        "quality_criteria": {
            "completeness": {
                "description": "Completitud del informe",
                "weight": 0.4,
                "factors": ["Número de palabras", "Secciones incluidas", "Detalle técnico"]
            },
            "structure": {
                "description": "Estructura del informe",
                "weight": 0.3,
                "factors": ["Secciones identificadas", "Formato correcto", "Organización lógica"]
            },
            "accuracy": {
                "description": "Precisión médica",
                "weight": 0.3,
                "factors": ["Consistencia con IA", "Terminología médica", "Recomendaciones apropiadas"]
            }
        },
        "benchmarks": {
            "excellent": "> 0.9",
            "good": "0.7 - 0.9",
            "acceptable": "0.5 - 0.7",
            "needs_review": "< 0.5"
        },
        "improvement_suggestions": [
            "Revisar informes con score < 0.7",
            "Validar terminología médica",
            "Verificar consistencia con detección IA",
            "Incluir más contexto clínico cuando sea necesario"
        ]
    }

@router.post(
    "/validate-report",
    summary="Validar informe médico",
    description="Valida la calidad y consistencia de un informe médico",
    tags=["Validación"]
)
async def validate_medical_report(
    report_content: Dict[str, Any]
):
    """
    Validar calidad de informe médico
    
    - **report_content**: Contenido del informe a validar
    
    Retorna análisis de calidad y sugerencias de mejora.
    """
    try:
        # Validaciones básicas
        validation_results = {
            "is_valid": True,
            "quality_score": 0.0,
            "issues": [],
            "suggestions": [],
            "sections_analysis": {},
            "metadata": {
                "validation_timestamp": "2024-01-01T00:00:00Z",
                "validator_version": "1.0.0"
            }
        }
        
        # Validar estructura
        required_fields = ["report_id", "case_id", "full_report"]
        missing_fields = [field for field in required_fields if field not in report_content]
        
        if missing_fields:
            validation_results["is_valid"] = False
            validation_results["issues"].extend([f"Campo faltante: {field}" for field in missing_fields])
        
        # Validar contenido del informe
        full_report = report_content.get("full_report", "")
        if full_report:
            # Análisis básico de calidad
            word_count = len(full_report.split())
            if word_count < 100:
                validation_results["issues"].append("Informe demasiado corto")
                validation_results["suggestions"].append("Incluir más detalles clínicos")
            elif word_count > 2000:
                validation_results["suggestions"].append("Considerar resumir contenido")
            
            # Verificar secciones
            expected_sections = ["HALLAZGOS", "IMPRESIÓN", "RECOMENDACIONES"]
            found_sections = [section for section in expected_sections if section in full_report.upper()]
            
            validation_results["sections_analysis"] = {
                "expected": expected_sections,
                "found": found_sections,
                "completeness": len(found_sections) / len(expected_sections)
            }
        
        # Calcular score de calidad
        structure_score = len(validation_results["sections_analysis"].get("found", [])) / 3
        length_score = min(len(full_report.split()) / 300, 1.0)
        validation_results["quality_score"] = (structure_score + length_score) / 2
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=validation_results
        )
        
    except Exception as e:
        logger.error(f"Error en validación de informe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en validación: {str(e)}"
        ) 