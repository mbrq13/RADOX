#!/usr/bin/env python3
"""
Puente Python para Modelo CNN
Script que permite a Node.js usar el modelo CNN existente de Python
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import numpy as np
    import cv2
    from PIL import Image
    import pydicom
    import tensorflow as tf
    from tensorflow import keras

    # Registrar métricas personalizadas antes de cargar el modelo
    def precision(y_true, y_pred):
        true_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true * y_pred, 0, 1)))
        predicted_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_pred, 0, 1)))
        return true_positives / (predicted_positives + tf.keras.backend.epsilon())

    def recall(y_true, y_pred):
        true_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true * y_pred, 0, 1)))
        possible_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true, 0, 1)))
        return true_positives / (possible_positives + tf.keras.backend.epsilon())

    tf.keras.utils.get_custom_objects()['precision'] = precision
    tf.keras.utils.get_custom_objects()['recall'] = recall

    from backend.models.cnn_model import CNNModel
    from backend.services.pneumonia_detection import PneumoniaDetectionService
    from backend.utils.image_processing import ImageProcessor

except ImportError as e:
    print(json.dumps({
        "success": False,
        "error": f"Error importing dependencies: {e}",
        "message": "Please ensure all Python dependencies are installed"
    }))
    sys.exit(1)


class CNNBridge:
    """Puente para ejecutar el modelo CNN desde Node.js"""

    def __init__(self, model_path="./data/models/pneumonia_resnet50.h5"):
        """
        Inicializar el puente CNN

        Args:
            model_path: Ruta completa al archivo del modelo
        """
        self.model_path = model_path
        self.cnn_model = None
        self.detection_service = None
        self.image_processor = ImageProcessor()

    async def initialize(self):
        """Inicializar el modelo CNN"""
        try:
            # Crear instancia del modelo CNN
            self.cnn_model = CNNModel(self.model_path)

            # Cargar el modelo
            success = await self.cnn_model.load_model()
            if not success:
                raise Exception("Failed to load CNN model")

            # Crear servicio de detección
            self.detection_service = PneumoniaDetectionService(self.cnn_model)

            return {
                "success": True,
                "message": "CNN model initialized successfully",
                "model_info": self.cnn_model.get_model_info()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize CNN model"
            }

    async def predict(self, image_path):
        """
        Realizar predicción de neumonía

        Args:
            image_path: Ruta a la imagen a analizar

        Returns:
            Dict con resultados de predicción
        """
        try:
            if not self.detection_service:
                raise Exception("CNN model not initialized")

            # Verificar que el archivo existe
            if not os.path.exists(image_path):
                raise Exception(f"Image file not found: {image_path}")

            # Leer archivo de imagen
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Obtener nombre del archivo
            filename = os.path.basename(image_path)

            # Ejecutar detección
            detection_result = await self.detection_service.detect_pneumonia(
                image_data=image_data,
                filename=filename,
                patient_info=None
            )

            # Extraer información de predicción
            prediction = detection_result.get("prediction", {})

            # Preparar respuesta compatible con Node.js
            result = {
                "success": True,
                "prediction": {
                    "label":               prediction.get("predicted_class", "Unknown"),
                    "confidence":          float(prediction.get("confidence", 0.0)),
                    "prob_neumonia":       prediction.get("prob_neumonia", float(prediction.get("confidence", 0.0))),
                    "has_pneumonia":       prediction.get("has_pneumonia", False),
                    "confidence_level":    prediction.get("confidence_level", "Unknown"),
                    "recommendation":      prediction.get("recommendation", ""),
                    "class_probabilities": prediction.get("class_probabilities", {}),
                    "heatmap":             prediction.get("heatmap", None),
                    "raw_predictions":     prediction.get("raw_predictions", None)
                },
                "case_id":        detection_result.get("case_id"),
                "timestamp":      detection_result.get("timestamp"),
                "processing_info": detection_result.get("processing_info", {}),
                "model_info":     self.cnn_model.get_model_info() if self.cnn_model else {}
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Prediction failed for image: {image_path}"
            }

    def process_image_file(self, image_path, output_path=None):
        """
        Procesar archivo de imagen para prepararlo para predicción

        Args:
            image_path: Ruta de imagen de entrada
            output_path: Ruta de imagen de salida (opcional)

        Returns:
            Dict con información del procesamiento
        """
        try:
            file_extension = os.path.splitext(image_path)[1].lower()

            if file_extension in ['.dcm', '.dicom']:
                dicom_file = pydicom.dcmread(image_path)
                pixel_array = dicom_file.pixel_array
                if pixel_array.dtype != np.uint8:
                    pixel_array = pixel_array.astype(np.float64)
                    pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())
                    pixel_array = (pixel_array * 255).astype(np.uint8)
                image_array = pixel_array
            else:
                image_array = cv2.imread(image_path)
                if image_array is None:
                    raise Exception(f"Could not read image: {image_path}")
                if len(image_array.shape) == 3:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            # Redimensionar a 224x224
            if image_array.shape[:2] != (224, 224):
                image_array = cv2.resize(image_array, (224, 224))

            if output_path:
                if len(image_array.shape) == 3:
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(output_path, image_bgr)
                else:
                    cv2.imwrite(output_path, image_array)

            return {
                "success": True,
                "original_shape": image_array.shape,
                "processed_shape": (224, 224, 3) if len(image_array.shape) == 3 else (224, 224),
                "file_type": file_extension,
                "output_path": output_path
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Image processing failed for: {image_path}"
            }


async def main():
    """Función principal para ejecutar desde línea de comandos"""
    parser = argparse.ArgumentParser(description="Puente Python para modelo CNN")
    parser.add_argument("--action", choices=["init", "predict", "process"], required=True,
                        help="Acción a realizar")
    parser.add_argument("--image", help="Ruta a la imagen para predicción")
    parser.add_argument("--model-path", default="./data/models/pneumonia_resnet50.h5",
                        help="Ruta completa al archivo del modelo CNN")
    parser.add_argument("--output", help="Ruta de salida para imagen procesada")

    args = parser.parse_args()

    bridge = CNNBridge(args.model_path)

    if args.action == "init":
        result = await bridge.initialize()
        print(json.dumps(result, indent=2))

    elif args.action == "predict":
        if not args.image:
            print(json.dumps({
                "success": False,
                "error": "Image path required for prediction"
            }))
            sys.exit(1)

        init_result = await bridge.initialize()
        if not init_result["success"]:
            print(json.dumps(init_result))
            sys.exit(1)

        result = await bridge.predict(args.image)
        print(json.dumps(result, indent=2))

    elif args.action == "process":
        if not args.image:
            print(json.dumps({
                "success": False,
                "error": "Image path required for processing"
            }))
            sys.exit(1)

        result = bridge.process_image_file(args.image, args.output)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
    