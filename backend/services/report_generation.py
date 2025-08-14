"""
Servicio de Generación de Informes Médicos
Integración con MedGemma via Hugging Face para generación de informes
"""

import requests
import json
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
import asyncio
import aiohttp

class ReportGenerationService:
    """Servicio para generación de informes médicos usando MedGemma"""
    
    def __init__(self, huggingface_token: str, model_name: str):
        """
        Inicializar el servicio de generación de informes
        
        Args:
            huggingface_token: Token de Hugging Face
            model_name: Nombre del modelo MedGemma
        """
        self.hf_token = huggingface_token
        self.model_name = model_name
        # Usar el endpoint específico de MedGemma
        self.api_url = "https://t911ok4t5x994zcu.us-east-1.aws.endpoints.huggingface.cloud"
        self.headers = {
            "Authorization": f"Bearer {huggingface_token}",
            "Content-Type": "application/json"
        }
        self.max_retries = 3
        self.timeout = 60
        
    async def generate_medical_report(
        self,
        detection_result: Dict[str, Any],
        patient_info: Optional[Dict[str, Any]] = None,
        language: str = "spanish"
    ) -> Dict[str, Any]:
        """
        Generar informe médico completo
        
        Args:
            detection_result: Resultado de la detección de neumonía
            similar_cases: Casos similares para contexto
            patient_info: Información adicional del paciente
            language: Idioma del informe
            
        Returns:
            Dict con el informe médico generado
        """
        try:
            logger.info(f"Generando informe médico para caso: {detection_result.get('case_id', 'unknown')}")
            
            # Construir prompt contextual
            prompt = self._build_medical_prompt(
                detection_result, patient_info, language
            )
            
            # Generar informe usando MedGemma
            generated_text = await self._call_medgemma_api(prompt)
            
            # Procesar y estructurar el informe
            structured_report = self._structure_medical_report(
                generated_text, detection_result, patient_info
            )
            
            # Validar y enriquecer el informe
            final_report = self._validate_and_enrich_report(structured_report, detection_result)
            
            logger.success("Informe médico generado correctamente")
            return final_report
            
        except Exception as e:
            logger.error(f"Error en generación de informe médico: {e}")
            # Generar informe de fallback
            return self._generate_fallback_report(detection_result, patient_info)
    
    def _build_medical_prompt(
        self,
        detection_result: Dict[str, Any],
        patient_info: Optional[Dict[str, Any]],
        language: str
    ) -> str:
        """
        Construir prompt médico contextual para MedGemma
        
        Args:
            detection_result: Resultado de detección
            similar_cases: Casos similares
            patient_info: Información del paciente
            language: Idioma
            
        Returns:
            str: Prompt estructurado
        """
        # Información básica del caso
        case_id = detection_result.get('case_id', '')
        prediction = detection_result.get('prediction', {})
        case_data = detection_result.get('case_data', {})
        
        # Construir contexto del paciente
        patient_context = ""
        if patient_info:
            age = patient_info.get('age', 'No especificada')
            gender = patient_info.get('gender', 'No especificado')
            symptoms = patient_info.get('symptoms', 'No especificados')
            patient_context = f"""
Información del Paciente:
- Edad: {age}
- Sexo: {gender}
- Síntomas: {symptoms}
"""
        
        # Información de la detección
        has_pneumonia = prediction.get('has_pneumonia', False)
        confidence = prediction.get('confidence', 0)
        predicted_class = prediction.get('predicted_class', '')
        recommendation = prediction.get('recommendation', '')
        findings = case_data.get('findings', '')
        
        detection_context = f"""
Resultados de Análisis por IA:
- Clasificación: {predicted_class}
- Confianza: {confidence:.2%}
- Diagnóstico IA: {'Neumonía detectada' if has_pneumonia else 'Sin signos de neumonía'}
- Hallazgos radiológicos: {findings}
- Recomendación inicial: {recommendation}
"""
        
        # Contexto de casos similares (eliminado)
        similar_context = ""
        
        # Prompt principal según idioma
        if language.lower() == "spanish":
            prompt = f"""Como médico radiólogo especialista, genera un informe médico completo y profesional basado en la siguiente información:

{patient_context}

{detection_context}

{similar_context}

Por favor, proporciona un informe médico estructurado que incluya:

1. DATOS DEL PACIENTE
2. TÉCNICA DE ESTUDIO
3. HALLAZGOS RADIOLÓGICOS
4. IMPRESIÓN DIAGNÓSTICA
5. RECOMENDACIONES CLÍNICAS
6. NOTAS ADICIONALES

El informe debe ser:
- Profesional y técnicamente preciso
- Basado en evidencia médica
- Apropiado para uso clínico
- En español médico formal
- Incluir correlación con casos similares cuando sea relevante

Caso ID: {case_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

INFORME RADIOLÓGICO:"""
        else:
            prompt = f"""As a specialist radiologist, generate a complete and professional medical report based on the following information:

{patient_context}

{detection_context}

{similar_context}

Please provide a structured medical report including:

1. PATIENT DATA
2. STUDY TECHNIQUE
3. RADIOLOGICAL FINDINGS
4. DIAGNOSTIC IMPRESSION
5. CLINICAL RECOMMENDATIONS
6. ADDITIONAL NOTES

Case ID: {case_id}
Date: {datetime.now().strftime('%m/%d/%Y %H:%M')}

RADIOLOGICAL REPORT:"""
        
        return prompt
    
    async def _call_medgemma_api(self, prompt: str) -> str:
        """
        Llamar a la API de MedGemma en Hugging Face
        
        Args:
            prompt: Prompt médico
            
        Returns:
            str: Texto generado por MedGemma
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.3,
                "do_sample": True,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "return_full_text": False
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            if isinstance(result, list) and len(result) > 0:
                                generated_text = result[0].get('generated_text', '')
                                if generated_text:
                                    logger.info("Texto generado exitosamente por MedGemma")
                                    return generated_text
                        
                        elif response.status == 503:
                            # Modelo cargándose
                            wait_time = min(20 * (attempt + 1), 60)
                            logger.warning(f"Modelo cargándose, esperando {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        
                        else:
                            error_text = await response.text()
                            logger.error(f"Error en API HuggingFace: {response.status} - {error_text}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout en intento {attempt + 1}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(5)
                    continue
            except Exception as e:
                logger.error(f"Error en llamada a MedGemma (intento {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(5)
                    continue
        
        raise Exception("No se pudo generar informe con MedGemma después de varios intentos")
    
    def _structure_medical_report(
        self,
        generated_text: str,
        detection_result: Dict[str, Any],
        patient_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Estructurar el informe médico generado
        
        Args:
            generated_text: Texto generado por MedGemma
            detection_result: Resultado de detección
            patient_info: Información del paciente
            
        Returns:
            Dict con informe estructurado
        """
        # Limpiar y procesar el texto generado
        cleaned_text = generated_text.strip()
        
        # Extraer secciones del informe
        sections = self._extract_report_sections(cleaned_text)
        
        # Información básica
        case_id = detection_result.get('case_id', '')
        prediction = detection_result.get('prediction', {})
        
        structured_report = {
            "report_id": f"RPT_{case_id}",
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "generated_by": self.model_name,
            "patient_info": patient_info or {},
            "ai_analysis": {
                "predicted_class": prediction.get('predicted_class', ''),
                "confidence": prediction.get('confidence', 0),
                "has_pneumonia": prediction.get('has_pneumonia', False),
                "confidence_level": prediction.get('confidence_level', '')
            },
            "report_sections": sections,
            "full_report": cleaned_text,
            "quality_metrics": self._assess_report_quality(cleaned_text)
        }
        
        return structured_report
    
    def _extract_report_sections(self, report_text: str) -> Dict[str, str]:
        """
        Extraer secciones específicas del informe
        
        Args:
            report_text: Texto completo del informe
            
        Returns:
            Dict con secciones extraídas
        """
        sections = {}
        
        # Patrones para identificar secciones
        section_patterns = {
            "datos_paciente": ["DATOS DEL PACIENTE", "PATIENT DATA"],
            "tecnica": ["TÉCNICA", "TECHNIQUE", "STUDY TECHNIQUE"],
            "hallazgos": ["HALLAZGOS", "FINDINGS", "RADIOLOGICAL FINDINGS"],
            "impresion": ["IMPRESIÓN", "IMPRESSION", "DIAGNOSTIC IMPRESSION"],
            "recomendaciones": ["RECOMENDACIONES", "RECOMMENDATIONS", "CLINICAL RECOMMENDATIONS"],
            "notas": ["NOTAS", "NOTES", "ADDITIONAL NOTES"]
        }
        
        lines = report_text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verificar si es una nueva sección
            found_section = None
            for section_key, patterns in section_patterns.items():
                for pattern in patterns:
                    if pattern in line.upper():
                        found_section = section_key
                        break
                if found_section:
                    break
            
            if found_section:
                # Guardar sección anterior
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                
                # Iniciar nueva sección
                current_section = found_section
                section_content = []
            else:
                # Añadir contenido a la sección actual
                if current_section:
                    section_content.append(line)
        
        # Guardar última sección
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()
        
        # Si no se encontraron secciones, usar el texto completo
        if not sections:
            sections["contenido_completo"] = report_text
        
        return sections
    
    def _validate_and_enrich_report(
        self,
        structured_report: Dict[str, Any],
        detection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validar y enriquecer el informe generado
        
        Args:
            structured_report: Informe estructurado
            detection_result: Resultado de detección original
            
        Returns:
            Dict con informe validado y enriquecido
        """
        # Añadir metadata adicional
        structured_report["metadata"] = {
            "generation_timestamp": datetime.now().isoformat(),
            "model_version": self.model_name,
            "ai_confidence": detection_result.get('prediction', {}).get('confidence', 0),
            "processing_method": "CNN + LLM",
            "language": "spanish",
            "validation_status": "generated"
        }
        
        # Añadir disclaimer médico
        structured_report["medical_disclaimer"] = (
            "Este informe ha sido generado con asistencia de inteligencia artificial. "
            "Debe ser revisado y validado por un médico especialista antes de su uso clínico. "
            "No reemplaza el juicio médico profesional."
        )
        
        # Evaluar calidad del informe
        quality_score = self._calculate_report_quality_score(structured_report)
        structured_report["quality_score"] = quality_score
        
        # Añadir recomendaciones de seguimiento
        structured_report["follow_up"] = self._generate_follow_up_recommendations(detection_result)
        
        return structured_report
    
    def _generate_fallback_report(
        self,
        detection_result: Dict[str, Any],
        patient_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generar informe de respaldo cuando falla MedGemma
        
        Args:
            detection_result: Resultado de detección
            patient_info: Información del paciente
            
        Returns:
            Dict con informe de respaldo
        """
        logger.warning("Generando informe de respaldo")
        
        case_id = detection_result.get('case_id', '')
        prediction = detection_result.get('prediction', {})
        case_data = detection_result.get('case_data', {})
        
        has_pneumonia = prediction.get('has_pneumonia', False)
        confidence = prediction.get('confidence', 0)
        findings = case_data.get('findings', '')
        recommendation = prediction.get('recommendation', '')
        
        # Generar informe básico estructurado
        if has_pneumonia:
            impression = f"Hallazgos compatibles con neumonía (confianza: {confidence:.1%})"
            clinical_recs = [
                "Evaluación médica urgente recomendada",
                "Considerar tratamiento antibiótico según juicio clínico",
                "Seguimiento radiológico en 48-72 horas"
            ]
        else:
            impression = f"Sin evidencia radiológica de neumonía (confianza: {confidence:.1%})"
            clinical_recs = [
                "Correlación clínica recomendada",
                "Seguimiento según sintomatología del paciente"
            ]
        
        fallback_report = {
            "report_id": f"RPT_{case_id}",
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "generated_by": "RADOX-Fallback",
            "patient_info": patient_info or {},
            "ai_analysis": {
                "predicted_class": prediction.get('predicted_class', ''),
                "confidence": confidence,
                "has_pneumonia": has_pneumonia,
                "confidence_level": prediction.get('confidence_level', '')
            },
            "report_sections": {
                "hallazgos": findings,
                "impresion": impression,
                "recomendaciones": "; ".join(clinical_recs)
            },
            "full_report": self._generate_basic_report_text(
                case_id, patient_info, findings, impression, clinical_recs
            ),
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "model_version": "Fallback-v1.0",
                "ai_confidence": confidence,
                "processing_method": "CNN + Template",
                "language": "spanish",
                "validation_status": "fallback"
            },
            "medical_disclaimer": (
                "Este informe ha sido generado automáticamente. "
                "Debe ser revisado por un médico especialista."
            ),
            "quality_score": {"overall": 0.6, "completeness": 0.5, "accuracy": 0.8}
        }
        
        return fallback_report
    
    def _generate_basic_report_text(
        self,
        case_id: str,
        patient_info: Optional[Dict[str, Any]],
        findings: str,
        impression: str,
        recommendations: List[str]
    ) -> str:
        """Generar texto básico del informe"""
        age = patient_info.get('age', 'No especificada') if patient_info else 'No especificada'
        gender = patient_info.get('gender', 'No especificado') if patient_info else 'No especificado'
        
        report_text = f"""INFORME RADIOLÓGICO

DATOS DEL PACIENTE:
- Edad: {age}
- Sexo: {gender}
- Caso ID: {case_id}
- Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

TÉCNICA:
Radiografía de tórax analizada mediante inteligencia artificial

HALLAZGOS RADIOLÓGICOS:
{findings}

IMPRESIÓN DIAGNÓSTICA:
{impression}

RECOMENDACIONES CLÍNICAS:
{chr(10).join([f"- {rec}" for rec in recommendations])}

NOTAS:
Estudio interpretado con asistencia de IA. Requiere validación médica.
"""
        return report_text
    
    def _assess_report_quality(self, report_text: str) -> Dict[str, float]:
        """Evaluar calidad del informe generado"""
        # Métricas básicas de calidad
        word_count = len(report_text.split())
        has_sections = any(keyword in report_text.upper() for keyword in 
                          ["HALLAZGOS", "IMPRESIÓN", "RECOMENDACIONES"])
        
        completeness = min(word_count / 200, 1.0)  # Normalizar a longitud esperada
        structure_score = 1.0 if has_sections else 0.5
        
        return {
            "completeness": completeness,
            "structure": structure_score,
            "word_count": word_count
        }
    
    def _calculate_report_quality_score(self, structured_report: Dict[str, Any]) -> Dict[str, float]:
        """Calcular score de calidad del informe"""
        sections = structured_report.get("report_sections", {})
        quality_metrics = structured_report.get("quality_metrics", {})
        
        # Evaluar completitud de secciones
        expected_sections = ["hallazgos", "impresion", "recomendaciones"]
        section_completeness = sum(1 for section in expected_sections if section in sections) / len(expected_sections)
        
        # Score general
        overall_score = (
            quality_metrics.get("completeness", 0) * 0.4 +
            quality_metrics.get("structure", 0) * 0.3 +
            section_completeness * 0.3
        )
        
        return {
            "overall": overall_score,
            "completeness": quality_metrics.get("completeness", 0),
            "structure": quality_metrics.get("structure", 0),
            "section_completeness": section_completeness
        }
    
    def _generate_follow_up_recommendations(self, detection_result: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones de seguimiento"""
        prediction = detection_result.get('prediction', {})
        has_pneumonia = prediction.get('has_pneumonia', False)
        confidence = prediction.get('confidence', 0)
        
        recommendations = []
        
        if has_pneumonia:
            if confidence > 0.8:
                recommendations.extend([
                    "Control radiológico en 48-72 horas",
                    "Evaluación clínica inmediata",
                    "Considerar hemograma y biomarcadores"
                ])
            else:
                recommendations.extend([
                    "Correlación clínica necesaria",
                    "Evaluación médica recomendada",
                    "Seguimiento según evolución clínica"
                ])
        else:
            recommendations.extend([
                "Seguimiento clínico de rutina",
                "Control radiológico solo si empeora sintomatología"
            ])
        
        return recommendations
    
    def get_service_info(self) -> Dict[str, Any]:
        """Obtener información del servicio"""
        return {
            "service": "ReportGenerationService",
            "version": "1.0.0",
            "model": self.model_name,
            "api_endpoint": self.api_url,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "status": "ready"
        } 