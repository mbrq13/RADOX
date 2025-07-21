#!/usr/bin/env python3
"""
Puente Python para Modelo CNN con TorchXRayVision
"""

import sys, os, json, argparse, asyncio, traceback
import warnings
import contextlib

# ruta raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.cnn_model import CNNModel
from backend.services.pneumonia_detection import PneumoniaDetectionService
from backend.utils.image_processing import ImageProcessor

# Redirigir warnings a stderr

def warn_with_stderr(message, category, filename, lineno, file=None, line=None):
    sys.stderr.write(warnings.formatwarning(message, category, filename, lineno, line))

warnings.showwarning = warn_with_stderr

# Context manager para redirigir stdout a stderr
class OnlyFinalJsonToStdout(contextlib.ContextDecorator):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = sys.stderr
    def __exit__(self, exc_type, exc, tb):
        sys.stdout = self._stdout

class CNNBridge:
    def __init__(self, model_path="./data/models/pneumonia_resnet50.h5"):
        self.model_path = model_path
        self.cnn_model = None
        self.detection_service = None
        self.image_processor = ImageProcessor()

    async def initialize(self):
        try:
            self.cnn_model = CNNModel(self.model_path)
            ok = await self.cnn_model.load_model()
            if not ok:
                raise RuntimeError("load_model() devolvió False")
            self.detection_service = PneumoniaDetectionService(self.cnn_model)
            return {"success": True, "model_info": self.cnn_model.get_model_info()}
        except Exception as e:
            # enviar traza a stderr y JSON de error a stdout
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    async def predict(self, image_path):
        try:
            init = await self.initialize()
            if not init["success"]:
                return init
            # Leer archivo de imagen como bytes
            import os
            if not os.path.exists(image_path):
                raise RuntimeError(f"No existe el archivo: {image_path}")
            with open(image_path, 'rb') as f:
                image_data = f.read()
            filename = os.path.basename(image_path)
            res = await self.detection_service.detect_pneumonia(
                image_data=image_data,
                filename=filename,
                patient_info=None
            )
            return {"success": True, "prediction": res["prediction"], "case_id": res["case_id"], "timestamp": res["timestamp"], "model_info": init["model_info"]}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

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

    with OnlyFinalJsonToStdout():
        if args.action == "init":
            result = await bridge.initialize()
        elif args.action == "predict":
            if not args.image:
                result = {
                    "success": False,
                    "error": "Image path required for prediction"
                }
            else:
                init_result = await bridge.initialize()
                if not init_result["success"]:
                    result = init_result
                else:
                    result = await bridge.predict(args.image)
        elif args.action == "process":
            if not args.image:
                result = {
                    "success": False,
                    "error": "Image path required for processing"
                }
            else:
                result = bridge.process_image_file(args.image, args.output)
    # Solo el JSON final va a stdout real
    print(json.dumps(result, indent=2))

if __name__=="__main__":
    asyncio.run(main())
 