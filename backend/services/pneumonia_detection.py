"""
Servicio de Detección de Neumonía
Lógica de negocio para la detección de neumonía usando CNN
"""

import os
import uuid
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import cv2
from PIL import Image
import pydicom
import asyncio

from backend.models.cnn_model import CNNModel

class PneumoniaDetectionService:
    """Servicio para la detección de neumonía en radiografías"""
    
    def __init__(self, cnn_model: CNNModel):
        """
        Inicializar el servicio de detección
        
        Args:
            cnn_model: Instancia del modelo CNN
        """
        self.cnn_model = cnn_model
        self.supported_formats = ['jpg', 'jpeg', 'png', 'dicom', 'dcm']
    
    async def detect_pneumonia(
        self, 
        image_data: bytes, 
        filename: str,
        patient_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detectar neumonía en una radiografía
        
        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo
            patient_info: Información adicional del paciente
            
        Returns:
            Dict con resultados de detección
        """
        try:
            logger.info(f"Iniciando detección de neumonía para: {filename}")
            
            # Generar ID único para el caso
            case_id = f"case_{uuid.uuid4().hex[:8]}"
            
            # Validar formato de archivo
            file_extension = filename.lower().split('.')[-1]
            if file_extension not in self.supported_formats:
                raise ValueError(f"Formato no soportado: {file_extension}")
            
            # Procesar imagen según su tipo
            image_array = await self._process_image(image_data, file_extension)
            
            # Realizar predicción con el modelo CNN
            prediction_result = await self.cnn_model.predict(image_array)

            # Generar heatmap Grad-CAM
            heatmap_base64 = self.cnn_model.get_gradcam_heatmap(image_array)
            prediction_result["heatmap"] = heatmap_base64
            
            # Extraer información médica de la imagen si es DICOM
            dicom_metadata = None
            if file_extension in ['dicom', 'dcm']:
                dicom_metadata = self._extract_dicom_metadata(image_data)
            
            # Generar datos del caso para almacenamiento
            case_data = self._create_case_data(
                case_id=case_id,
                prediction_result=prediction_result,
                patient_info=patient_info,
                dicom_metadata=dicom_metadata,
                filename=filename
            )
            
            # Preparar respuesta
            response = {
                "case_id": case_id,
                "timestamp": datetime.now().isoformat(),
                "filename": filename,
                "prediction": prediction_result,
                "case_data": case_data,
                "processing_info": {
                    "image_format": file_extension,
                    "has_dicom_metadata": dicom_metadata is not None,
                    "model_version": "ResNet50-v1.0"
                }
            }
            
            logger.success(f"Detección completada para caso: {case_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error en detección de neumonía: {e}")
            raise
    
    async def _process_image(self, image_data: bytes, file_extension: str) -> np.ndarray:
        """
        Procesar imagen según su formato
        
        Args:
            image_data: Datos binarios de la imagen
            file_extension: Extensión del archivo
            
        Returns:
            np.ndarray: Array de imagen procesada
        """
        try:
            if file_extension in ['dicom', 'dcm']:
                return self._process_dicom_image(image_data)
            else:
                return self._process_standard_image(image_data)
                
        except Exception as e:
            logger.error(f"Error al procesar imagen: {e}")
            raise
    
    def _process_dicom_image(self, image_data: bytes) -> np.ndarray:
        """
        Procesar imagen DICOM
        
        Args:
            image_data: Datos binarios del DICOM
            
        Returns:
            np.ndarray: Array de imagen
        """
        try:
            # Leer DICOM desde bytes
            import io
            dicom_file = pydicom.dcmread(io.BytesIO(image_data))
            
            # Extraer array de píxeles
            pixel_array = dicom_file.pixel_array
            
            # Normalizar valores de píxeles
            if pixel_array.dtype != np.uint8:
                # Normalizar a rango 0-255
                pixel_array = pixel_array.astype(np.float64)
                pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())
                pixel_array = (pixel_array * 255).astype(np.uint8)
            
            # Aplicar windowing si está disponible
            if hasattr(dicom_file, 'WindowCenter') and hasattr(dicom_file, 'WindowWidth'):
                center = float(dicom_file.WindowCenter[0] if isinstance(dicom_file.WindowCenter, list) else dicom_file.WindowCenter)
                width = float(dicom_file.WindowWidth[0] if isinstance(dicom_file.WindowWidth, list) else dicom_file.WindowWidth)
                
                min_val = center - width / 2
                max_val = center + width / 2
                
                pixel_array = np.clip(pixel_array, min_val, max_val)
                pixel_array = ((pixel_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            
            logger.info(f"Imagen DICOM procesada: {pixel_array.shape}")
            return pixel_array
            
        except Exception as e:
            logger.error(f"Error al procesar imagen DICOM: {e}")
            raise
    
    def _process_standard_image(self, image_data: bytes) -> np.ndarray:
        """
        Procesar imagen estándar (JPG, PNG)
        
        Args:
            image_data: Datos binarios de la imagen
            
        Returns:
            np.ndarray: Array de imagen
        """
        try:
            # Convertir bytes a array numpy
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Decodificar imagen con OpenCV
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                raise ValueError("No se pudo decodificar la imagen")
            
            logger.info(f"Imagen estándar procesada: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"Error al procesar imagen estándar: {e}")
            raise
    
    def _extract_dicom_metadata(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Extraer metadata de imagen DICOM
        
        Args:
            image_data: Datos binarios del DICOM
            
        Returns:
            Dict con metadata extraída
        """
        try:
            import io
            dicom_file = pydicom.dcmread(io.BytesIO(image_data))
            
            metadata = {
                "patient_id": getattr(dicom_file, 'PatientID', ''),
                "patient_name": str(getattr(dicom_file, 'PatientName', '')),
                "patient_age": getattr(dicom_file, 'PatientAge', ''),
                "patient_sex": getattr(dicom_file, 'PatientSex', ''),
                "study_date": getattr(dicom_file, 'StudyDate', ''),
                "study_time": getattr(dicom_file, 'StudyTime', ''),
                "modality": getattr(dicom_file, 'Modality', ''),
                "institution": getattr(dicom_file, 'InstitutionName', ''),
                "manufacturer": getattr(dicom_file, 'Manufacturer', ''),
                "model": getattr(dicom_file, 'ManufacturerModelName', ''),
                "body_part": getattr(dicom_file, 'BodyPartExamined', ''),
                "view_position": getattr(dicom_file, 'ViewPosition', ''),
                "image_size": f"{dicom_file.Rows}x{dicom_file.Columns}",
                "pixel_spacing": getattr(dicom_file, 'PixelSpacing', []),
                "slice_thickness": getattr(dicom_file, 'SliceThickness', ''),
                "kvp": getattr(dicom_file, 'KVP', ''),
                "exposure_time": getattr(dicom_file, 'ExposureTime', ''),
                "window_center": getattr(dicom_file, 'WindowCenter', ''),
                "window_width": getattr(dicom_file, 'WindowWidth', '')
            }
            
            # Limpiar valores vacíos
            metadata = {k: v for k, v in metadata.items() if v != ''}
            
            logger.info("Metadata DICOM extraída correctamente")
            return metadata
            
        except Exception as e:
            logger.warning(f"Error al extraer metadata DICOM: {e}")
            return None
    
    def _create_case_data(
        self, 
        case_id: str,
        prediction_result: Dict[str, Any],
        patient_info: Optional[Dict[str, Any]] = None,
        dicom_metadata: Optional[Dict[str, Any]] = None,
        filename: str = ""
    ) -> Dict[str, Any]:
        """
        Crear datos del caso para almacenamiento en vector store
        
        Args:
            case_id: ID del caso
            prediction_result: Resultado de la predicción
            patient_info: Información del paciente
            dicom_metadata: Metadata DICOM
            filename: Nombre del archivo
            
        Returns:
            Dict con datos del caso
        """
        # Determinar diagnosis basado en predicción
        has_pneumonia = prediction_result.get('has_pneumonia', False)
        confidence = prediction_result.get('confidence', 0)
        
        diagnosis = "Neumonía" if has_pneumonia else "Normal"
        if has_pneumonia and confidence >= 0.9:
            diagnosis = "Neumonía probable"
        elif has_pneumonia and confidence < 0.7:
            diagnosis = "Neumonía posible"
        
        # Determinar severidad
        severity = "ninguna"
        if has_pneumonia:
            if confidence >= 0.9:
                severity = "alta"
            elif confidence >= 0.8:
                severity = "moderada"
            else:
                severity = "leve"
        
        # Crear datos del caso
        case_data = {
            "case_id": case_id,
            "diagnosis": diagnosis,
            "confidence": confidence,
            "confidence_level": prediction_result.get('confidence_level', ''),
            "predicted_class": prediction_result.get('predicted_class', ''),
            "has_pneumonia": has_pneumonia,
            "severity": severity,
            "recommendation": prediction_result.get('recommendation', ''),
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "processing_method": "CNN_ResNet50"
        }
        
        # Añadir información del paciente si está disponible
        if patient_info:
            case_data.update({
                "patient_age": patient_info.get('age', ''),
                "patient_gender": patient_info.get('gender', ''),
                "symptoms": patient_info.get('symptoms', ''),
                "clinical_history": patient_info.get('clinical_history', '')
            })
        
        # Añadir metadata DICOM si está disponible
        if dicom_metadata:
            case_data.update({
                "dicom_patient_id": dicom_metadata.get('patient_id', ''),
                "dicom_patient_age": dicom_metadata.get('patient_age', ''),
                "dicom_patient_sex": dicom_metadata.get('patient_sex', ''),
                "study_date": dicom_metadata.get('study_date', ''),
                "modality": dicom_metadata.get('modality', ''),
                "view_position": dicom_metadata.get('view_position', ''),
                "body_part": dicom_metadata.get('body_part', ''),
                "institution": dicom_metadata.get('institution', '')
            })
        
        # Generar hallazgos basados en predicción
        if has_pneumonia:
            case_data["findings"] = self._generate_findings(confidence, severity)
        else:
            case_data["findings"] = "Campos pulmonares limpios, sin signos de consolidación o infiltrados"
        
        return case_data
    
    def _generate_findings(self, confidence: float, severity: str) -> str:
        """
        Generar descripción de hallazgos basada en confianza y severidad
        
        Args:
            confidence: Nivel de confianza
            severity: Severidad detectada
            
        Returns:
            str: Descripción de hallazgos
        """
        base_findings = [
            "Presencia de opacidades pulmonares",
            "Signos sugestivos de proceso inflamatorio",
            "Alteración del patrón pulmonar normal"
        ]
        
        if severity == "alta":
            findings = [
                "Consolidación pulmonar evidente",
                "Broncograma aéreo visible", 
                "Opacidades densas con límites definidos",
                "Probable derrame pleural asociado"
            ]
        elif severity == "moderada":
            findings = [
                "Infiltrados pulmonares parcheados",
                "Opacidades de densidad intermedia",
                "Patrón alveolar focal",
                "Engrosamiento intersticial"
            ]
        else:  # leve
            findings = [
                "Opacidades sutiles en vidrio esmerilado",
                "Infiltrados intersticiales mínimos",
                "Cambios inflamatorios incipientes",
                "Patrón reticular fino"
            ]
        
        if confidence < 0.8:
            findings.append("Hallazgos requieren correlación clínica")
        
        return ". ".join(findings) + "."
    
    def get_service_info(self) -> Dict[str, Any]:
        """Obtener información del servicio"""
        return {
            "service": "PneumoniaDetectionService",
            "version": "1.0.0",
            "supported_formats": self.supported_formats,
            "model_status": "loaded" if self.cnn_model.is_loaded else "not_loaded",
            "model_info": self.cnn_model.get_model_info()
        } 