"""
Utilidades para Procesamiento de Imágenes Médicas
Funciones auxiliares para manipular y procesar imágenes DICOM y estándar
"""

import os
import io
import numpy as np
import cv2
from PIL import Image, ImageEnhance
import pydicom
from typing import Tuple, Optional, Dict, Any, Union
from loguru import logger
import base64

class ImageProcessor:
    """Clase para procesamiento de imágenes médicas"""
    
    @staticmethod
    def load_image_from_bytes(image_data: bytes, filename: str) -> np.ndarray:
        """
        Cargar imagen desde bytes
        
        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo para determinar formato
            
        Returns:
            np.ndarray: Array de imagen
        """
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension in ['dcm', 'dicom']:
            return ImageProcessor._load_dicom_from_bytes(image_data)
        else:
            return ImageProcessor._load_standard_image_from_bytes(image_data)
    
    @staticmethod
    def _load_dicom_from_bytes(image_data: bytes) -> np.ndarray:
        """Cargar imagen DICOM desde bytes"""
        try:
            dicom_file = pydicom.dcmread(io.BytesIO(image_data))
            pixel_array = dicom_file.pixel_array
            
            # Normalizar si es necesario
            if pixel_array.dtype != np.uint8:
                pixel_array = ImageProcessor.normalize_to_uint8(pixel_array)
            
            return pixel_array
            
        except Exception as e:
            logger.error(f"Error al cargar DICOM: {e}")
            raise
    
    @staticmethod
    def _load_standard_image_from_bytes(image_data: bytes) -> np.ndarray:
        """Cargar imagen estándar desde bytes"""
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                raise ValueError("No se pudo decodificar la imagen")
            
            return image
            
        except Exception as e:
            logger.error(f"Error al cargar imagen estándar: {e}")
            raise
    
    @staticmethod
    def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
        """
        Normalizar imagen a uint8 (0-255)
        
        Args:
            image: Array de imagen
            
        Returns:
            np.ndarray: Imagen normalizada
        """
        # Normalizar a rango 0-1
        normalized = (image - image.min()) / (image.max() - image.min())
        
        # Convertir a 0-255
        return (normalized * 255).astype(np.uint8)
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Redimensionar imagen manteniendo proporción
        
        Args:
            image: Array de imagen
            target_size: Tamaño objetivo (width, height)
            
        Returns:
            np.ndarray: Imagen redimensionada
        """
        return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def enhance_contrast(image: np.ndarray, factor: float = 1.5) -> np.ndarray:
        """
        Mejorar contraste de la imagen
        
        Args:
            image: Array de imagen
            factor: Factor de mejora del contraste
            
        Returns:
            np.ndarray: Imagen con contraste mejorado
        """
        # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=factor, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        return enhanced
    
    @staticmethod
    def apply_window_level(
        image: np.ndarray, 
        window_center: float, 
        window_width: float
    ) -> np.ndarray:
        """
        Aplicar windowing (ventana) a imagen médica
        
        Args:
            image: Array de imagen
            window_center: Centro de la ventana
            window_width: Ancho de la ventana
            
        Returns:
            np.ndarray: Imagen con windowing aplicado
        """
        min_val = window_center - window_width / 2
        max_val = window_center + window_width / 2
        
        # Aplicar ventana
        windowed = np.clip(image, min_val, max_val)
        
        # Normalizar a 0-255
        windowed = ((windowed - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        return windowed
    
    @staticmethod
    def detect_lung_region(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detectar región pulmonar en radiografía de tórax
        
        Args:
            image: Array de imagen
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (imagen_segmentada, máscara)
        """
        try:
            # Normalizar imagen
            normalized = ImageProcessor.normalize_to_uint8(image)
            
            # Aplicar filtro gaussiano para suavizar
            blurred = cv2.GaussianBlur(normalized, (5, 5), 0)
            
            # Umbralización adaptativa
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Operaciones morfológicas para limpiar
            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Crear máscara con los contornos más grandes (probablemente pulmones)
            mask = np.zeros_like(image)
            if contours:
                # Seleccionar los 2 contornos más grandes
                largest_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
                cv2.fillPoly(mask, largest_contours, 255)
            
            # Aplicar máscara a la imagen original
            segmented = cv2.bitwise_and(image, image, mask=mask.astype(np.uint8))
            
            return segmented, mask
            
        except Exception as e:
            logger.warning(f"Error en segmentación pulmonar: {e}")
            return image, np.ones_like(image) * 255
    
    @staticmethod
    def extract_texture_features(image: np.ndarray) -> Dict[str, float]:
        """
        Extraer características de textura de la imagen
        
        Args:
            image: Array de imagen
            
        Returns:
            Dict con características extraídas
        """
        try:
            # Asegurar que la imagen esté en uint8
            if image.dtype != np.uint8:
                image = ImageProcessor.normalize_to_uint8(image)
            
            # Características básicas
            mean_intensity = float(np.mean(image))
            std_intensity = float(np.std(image))
            
            # Calcular gradientes
            grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Características de textura
            features = {
                "mean_intensity": mean_intensity,
                "std_intensity": std_intensity,
                "gradient_magnitude": float(np.mean(magnitude)),
                "gradient_std": float(np.std(magnitude)),
                "contrast": float(np.std(image)),
                "entropy": ImageProcessor._calculate_entropy(image),
                "energy": float(np.sum(image**2) / (image.shape[0] * image.shape[1]))
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error al extraer características de textura: {e}")
            return {}
    
    @staticmethod
    def _calculate_entropy(image: np.ndarray) -> float:
        """Calcular entropía de la imagen"""
        histogram, _ = np.histogram(image, bins=256, range=(0, 256))
        histogram = histogram / histogram.sum()
        
        # Evitar log(0)
        histogram = histogram[histogram > 0]
        
        entropy = -np.sum(histogram * np.log2(histogram))
        return float(entropy)
    
    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        """
        Convertir imagen a base64 para visualización web
        
        Args:
            image: Array de imagen
            
        Returns:
            str: Imagen codificada en base64
        """
        try:
            # Asegurar que está en uint8
            if image.dtype != np.uint8:
                image = ImageProcessor.normalize_to_uint8(image)
            
            # Convertir a PIL Image
            pil_image = Image.fromarray(image)
            
            # Convertir a bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            
            # Codificar en base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error al convertir imagen a base64: {e}")
            return ""
    
    @staticmethod
    def create_thumbnail(image: np.ndarray, max_size: int = 256) -> np.ndarray:
        """
        Crear miniatura de la imagen
        
        Args:
            image: Array de imagen
            max_size: Tamaño máximo de la miniatura
            
        Returns:
            np.ndarray: Miniatura
        """
        height, width = image.shape[:2]
        
        # Calcular nuevo tamaño manteniendo proporción
        if width > height:
            new_width = max_size
            new_height = int((height * max_size) / width)
        else:
            new_height = max_size
            new_width = int((width * max_size) / height)
        
        thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return thumbnail
    
    @staticmethod
    def add_annotations(
        image: np.ndarray, 
        annotations: Dict[str, Any]
    ) -> np.ndarray:
        """
        Añadir anotaciones a la imagen
        
        Args:
            image: Array de imagen
            annotations: Diccionario con anotaciones
            
        Returns:
            np.ndarray: Imagen con anotaciones
        """
        try:
            # Convertir a color para anotaciones
            if len(image.shape) == 2:
                annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            else:
                annotated = image.copy()
            
            # Añadir texto con resultados
            prediction = annotations.get('prediction', '')
            confidence = annotations.get('confidence', 0)
            
            # Texto principal
            text = f"{prediction} ({confidence:.1%})"
            cv2.putText(
                annotated, text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
            )
            
            # Añadir marcos si hay regiones de interés
            if 'regions' in annotations:
                for region in annotations['regions']:
                    x, y, w, h = region.get('bbox', [0, 0, 0, 0])
                    cv2.rectangle(annotated, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    label = region.get('label', '')
                    if label:
                        cv2.putText(
                            annotated, label, (x, y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1
                        )
            
            return annotated
            
        except Exception as e:
            logger.error(f"Error al añadir anotaciones: {e}")
            return image

class DICOMProcessor:
    """Procesador especializado para archivos DICOM"""
    
    @staticmethod
    def extract_dicom_metadata(dicom_file: pydicom.Dataset) -> Dict[str, Any]:
        """
        Extraer metadata completa de archivo DICOM
        
        Args:
            dicom_file: Dataset DICOM
            
        Returns:
            Dict con metadata extraída
        """
        metadata = {}
        
        # Información del paciente
        patient_info = {
            "patient_id": getattr(dicom_file, 'PatientID', ''),
            "patient_name": str(getattr(dicom_file, 'PatientName', '')),
            "patient_birth_date": getattr(dicom_file, 'PatientBirthDate', ''),
            "patient_age": getattr(dicom_file, 'PatientAge', ''),
            "patient_sex": getattr(dicom_file, 'PatientSex', ''),
            "patient_weight": getattr(dicom_file, 'PatientWeight', ''),
            "patient_size": getattr(dicom_file, 'PatientSize', '')
        }
        
        # Información del estudio
        study_info = {
            "study_instance_uid": getattr(dicom_file, 'StudyInstanceUID', ''),
            "study_date": getattr(dicom_file, 'StudyDate', ''),
            "study_time": getattr(dicom_file, 'StudyTime', ''),
            "study_description": getattr(dicom_file, 'StudyDescription', ''),
            "accession_number": getattr(dicom_file, 'AccessionNumber', '')
        }
        
        # Información de la serie
        series_info = {
            "series_instance_uid": getattr(dicom_file, 'SeriesInstanceUID', ''),
            "series_number": getattr(dicom_file, 'SeriesNumber', ''),
            "series_description": getattr(dicom_file, 'SeriesDescription', ''),
            "modality": getattr(dicom_file, 'Modality', ''),
            "body_part_examined": getattr(dicom_file, 'BodyPartExamined', ''),
            "view_position": getattr(dicom_file, 'ViewPosition', '')
        }
        
        # Información de la imagen
        image_info = {
            "sop_instance_uid": getattr(dicom_file, 'SOPInstanceUID', ''),
            "instance_number": getattr(dicom_file, 'InstanceNumber', ''),
            "rows": getattr(dicom_file, 'Rows', 0),
            "columns": getattr(dicom_file, 'Columns', 0),
            "pixel_spacing": getattr(dicom_file, 'PixelSpacing', []),
            "slice_thickness": getattr(dicom_file, 'SliceThickness', ''),
            "bits_allocated": getattr(dicom_file, 'BitsAllocated', 0),
            "bits_stored": getattr(dicom_file, 'BitsStored', 0)
        }
        
        # Información del equipo
        equipment_info = {
            "manufacturer": getattr(dicom_file, 'Manufacturer', ''),
            "manufacturer_model_name": getattr(dicom_file, 'ManufacturerModelName', ''),
            "device_serial_number": getattr(dicom_file, 'DeviceSerialNumber', ''),
            "software_versions": getattr(dicom_file, 'SoftwareVersions', ''),
            "institution_name": getattr(dicom_file, 'InstitutionName', ''),
            "station_name": getattr(dicom_file, 'StationName', '')
        }
        
        # Parámetros de adquisición
        acquisition_info = {
            "kvp": getattr(dicom_file, 'KVP', ''),
            "exposure_time": getattr(dicom_file, 'ExposureTime', ''),
            "x_ray_tube_current": getattr(dicom_file, 'XRayTubeCurrent', ''),
            "exposure": getattr(dicom_file, 'Exposure', ''),
            "filter_material": getattr(dicom_file, 'FilterMaterial', ''),
            "collimator_shape": getattr(dicom_file, 'CollimatorShape', '')
        }
        
        # Información de display
        display_info = {
            "window_center": getattr(dicom_file, 'WindowCenter', ''),
            "window_width": getattr(dicom_file, 'WindowWidth', ''),
            "rescale_intercept": getattr(dicom_file, 'RescaleIntercept', 0),
            "rescale_slope": getattr(dicom_file, 'RescaleSlope', 1),
            "photometric_interpretation": getattr(dicom_file, 'PhotometricInterpretation', '')
        }
        
        metadata.update({
            "patient": patient_info,
            "study": study_info,
            "series": series_info,
            "image": image_info,
            "equipment": equipment_info,
            "acquisition": acquisition_info,
            "display": display_info
        })
        
        # Limpiar valores vacíos
        return DICOMProcessor._clean_metadata(metadata)
    
    @staticmethod
    def _clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Limpiar metadata eliminando valores vacíos"""
        cleaned = {}
        
        for key, value in metadata.items():
            if isinstance(value, dict):
                cleaned_sub = {k: v for k, v in value.items() if v != '' and v != [] and v != 0}
                if cleaned_sub:
                    cleaned[key] = cleaned_sub
            elif value != '' and value != [] and value != 0:
                cleaned[key] = value
        
        return cleaned
    
    @staticmethod
    def apply_dicom_windowing(
        pixel_array: np.ndarray, 
        window_center: Union[int, float, list], 
        window_width: Union[int, float, list]
    ) -> np.ndarray:
        """
        Aplicar windowing específico de DICOM
        
        Args:
            pixel_array: Array de píxeles
            window_center: Centro de ventana DICOM
            window_width: Ancho de ventana DICOM
            
        Returns:
            np.ndarray: Array con windowing aplicado
        """
        # Manejar múltiples ventanas
        if isinstance(window_center, list):
            window_center = window_center[0]
        if isinstance(window_width, list):
            window_width = window_width[0]
        
        # Aplicar windowing
        min_val = window_center - window_width / 2
        max_val = window_center + window_width / 2
        
        windowed = np.clip(pixel_array, min_val, max_val)
        windowed = ((windowed - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        return windowed

def validate_medical_image(image_data: bytes, filename: str) -> Dict[str, Any]:
    """
    Validar imagen médica
    
    Args:
        image_data: Datos binarios de la imagen
        filename: Nombre del archivo
        
    Returns:
        Dict con resultados de validación
    """
    validation_result = {
        "is_valid": False,
        "format": "",
        "size": len(image_data),
        "dimensions": None,
        "errors": [],
        "warnings": []
    }
    
    try:
        file_extension = filename.lower().split('.')[-1]
        validation_result["format"] = file_extension
        
        # Validar tamaño mínimo
        if len(image_data) < 1024:  # 1KB mínimo
            validation_result["errors"].append("Archivo demasiado pequeño")
            return validation_result
        
        # Validar tamaño máximo (50MB)
        if len(image_data) > 50 * 1024 * 1024:
            validation_result["errors"].append("Archivo demasiado grande")
            return validation_result
        
        # Validar formato y cargar imagen
        if file_extension in ['dcm', 'dicom']:
            dicom_file = pydicom.dcmread(io.BytesIO(image_data))
            pixel_array = dicom_file.pixel_array
            validation_result["dimensions"] = pixel_array.shape
            
            # Validaciones específicas DICOM
            if not hasattr(dicom_file, 'Modality'):
                validation_result["warnings"].append("Sin información de modalidad")
            elif dicom_file.Modality not in ['CR', 'DX', 'CT', 'MR']:
                validation_result["warnings"].append(f"Modalidad no típica para radiología: {dicom_file.Modality}")
                
        else:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            if image is None:
                validation_result["errors"].append("No se pudo decodificar la imagen")
                return validation_result
            
            validation_result["dimensions"] = image.shape
        
        # Validar dimensiones mínimas
        if validation_result["dimensions"]:
            height, width = validation_result["dimensions"][:2]
            if height < 100 or width < 100:
                validation_result["errors"].append("Dimensiones demasiado pequeñas")
            elif height > 5000 or width > 5000:
                validation_result["warnings"].append("Dimensiones muy grandes")
        
        # Si no hay errores, la imagen es válida
        if not validation_result["errors"]:
            validation_result["is_valid"] = True
        
    except Exception as e:
        validation_result["errors"].append(f"Error al procesar imagen: {str(e)}")
    
    return validation_result 