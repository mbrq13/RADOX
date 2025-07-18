"""
Modelo CNN para Detección de Neumonía
Implementación usando TensorFlow/Keras con ResNet50
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from loguru import logger
from typing import Optional, Tuple, Dict, Any
import cv2
from PIL import Image
import asyncio

class CNNModel:
    """Modelo CNN para detección de neumonía en radiografías de tórax"""
    
    def __init__(self, model_path: str):
        """
        Inicializar el modelo CNN
        
        Args:
            model_path: Ruta completa al archivo del modelo (incluyendo el nombre)
        """
        self.model_path = model_path  # Ahora es la ruta completa al archivo .h5
        self.model: Optional[Model] = None
        self.is_loaded = False
        self.input_shape = (224, 224, 3)
        self.class_names = ["Normal", "Neumonía"]
        
    async def load_model(self) -> bool:
        """
        Cargar el modelo CNN pre-entrenado
        
        Returns:
            bool: True si el modelo se cargó correctamente
        """
        try:
            model_file = self.model_path  # Usar la ruta completa
            
            if os.path.exists(model_file):
                logger.info(f"Cargando modelo desde: {model_file}")
                self.model = keras.models.load_model(model_file)
            else:
                logger.warning("Modelo no encontrado, creando y entrenando nuevo modelo...")
                self.model = await self._create_model()
                await self._save_model()
            
            self.is_loaded = True
            logger.success("Modelo CNN cargado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar modelo CNN: {e}")
            return False
    
    async def _create_model(self) -> Model:
        """
        Crear arquitectura del modelo CNN basada en ResNet50
        
        Returns:
            Model: Modelo de Keras compilado
        """
        logger.info("Creando nueva arquitectura de modelo CNN...")
        
        # Base model ResNet50 pre-entrenado
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=self.input_shape
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Añadir capas de clasificación
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu', name='dense_1')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu', name='dense_2')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(2, activation='softmax', name='predictions')(x)
        
        # Crear modelo completo
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compilar modelo
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        logger.info("Arquitectura del modelo creada")
        return model
    
    async def _save_model(self) -> None:
        """Guardar el modelo entrenado"""
        if self.model is not None:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model.save(self.model_path)
            logger.info(f"Modelo guardado en: {self.model_path}")
    
    def preprocess_image(self, image_data: np.ndarray) -> np.ndarray:
        """
        Preprocesar imagen para inferencia
        
        Args:
            image_data: Array de imagen
            
        Returns:
            np.ndarray: Imagen preprocesada
        """
        try:
            # Redimensionar a 224x224
            if len(image_data.shape) == 3:
                image_resized = cv2.resize(image_data, (224, 224))
            else:
                # Convertir escala de grises a RGB
                image_gray = cv2.resize(image_data, (224, 224))
                image_resized = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2RGB)
            
            # Normalizar
            image_array = np.array(image_resized, dtype=np.float32)
            image_array = np.expand_dims(image_array, axis=0)
            image_array = preprocess_input(image_array)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento: {e}")
            raise
    
    async def predict(self, image_data: np.ndarray) -> Dict[str, Any]:
        """
        Realizar predicción de neumonía
        
        Args:
            image_data: Array de imagen
            
        Returns:
            Dict con resultados de predicción
        """
        if not self.is_loaded or self.model is None:
            raise ValueError("Modelo no está cargado")
        
        try:
            # Preprocesar imagen
            processed_image = self.preprocess_image(image_data)
            
            # Realizar predicción
            predictions = self.model.predict(processed_image, verbose=0)
            prediction_probs = predictions[0]
            
            # Interpretar resultados
            predicted_class_idx = np.argmax(prediction_probs)
            predicted_class = self.class_names[predicted_class_idx]
            confidence = float(prediction_probs[predicted_class_idx])
            
            # Probabilidades por clase
            class_probabilities = {
                self.class_names[i]: float(prediction_probs[i])
                for i in range(len(self.class_names))
            }
            
            # Determinar nivel de confianza
            confidence_level = self._get_confidence_level(confidence)
            
            result = {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "confidence_level": confidence_level,
                "class_probabilities": class_probabilities,
                "has_pneumonia": predicted_class == "Neumonía",
                "recommendation": self._get_recommendation(predicted_class, confidence)
            }
            
            logger.info(f"Predicción: {predicted_class} (confianza: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Determinar nivel de confianza textual"""
        if confidence >= 0.9:
            return "Muy Alta"
        elif confidence >= 0.8:
            return "Alta"
        elif confidence >= 0.7:
            return "Media"
        elif confidence >= 0.6:
            return "Baja"
        else:
            return "Muy Baja"
    
    def _get_recommendation(self, predicted_class: str, confidence: float) -> str:
        """Generar recomendación basada en predicción"""
        if predicted_class == "Neumonía":
            if confidence >= 0.8:
                return "Se recomienda evaluación médica inmediata. Los hallazgos sugieren presencia de neumonía."
            else:
                return "Se recomienda evaluación médica. Posibles signos de neumonía requieren confirmación."
        else:
            if confidence >= 0.8:
                return "Radiografía aparenta normalidad. Considerar evaluación clínica si hay síntomas."
            else:
                return "Resultado incierto. Se recomienda evaluación médica adicional."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo"""
        if not self.is_loaded or self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "architecture": "ResNet50",
            "input_shape": self.input_shape,
            "classes": self.class_names,
            "parameters": self.model.count_params() if hasattr(self.model, 'count_params') else None,
            "model_path": self.model_path
        } 