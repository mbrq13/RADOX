# backend/models/cnn_model.py

"""
Modelo CNN para Detección de Neumonía usando TorchXRayVision
------------------------------------------------------------
- Usa DenseNet121 preentrenado de torchxrayvision.
- Clasifica “Pneumonia” vs “Normal”.
"""

import os
import numpy as np
import torch
import torchvision.transforms as T
import torchxrayvision as xrv
from typing import Dict, Any
import contextlib
import sys

# Respetar variable de entorno para CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "")

class CNNModel:
    def __init__(self, model_path: str = None):
        """
        model_path se ignora: usamos pesos preentrenados de torchxrayvision.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pathology_list = xrv.datasets.default_pathologies
        self.pneumonia_idx = self.pathology_list.index("Pneumonia")

        # Media y std que usa TorchXRayVision (valores estándar para imágenes de tórax)
        self.mean, self.std = [0.485], [0.229]
        self.transform = T.Compose([
            T.ToPILImage(),
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(self.mean, self.std)
        ])

        self.model: torch.nn.Module = None
        self.is_loaded = False

    async def load_model(self) -> bool:
        """Carga el DenseNet121 preentrenado de TorchXRayVision."""
        try:
            with contextlib.redirect_stdout(sys.stderr):
                self.model = xrv.models.DenseNet(
                    num_classes=len(self.pathology_list),
                    weights="densenet121-res224-all",  # cadena exacta dependiente de la versión de xrv
                    in_channels=1
                ).to(self.device).eval()
            self.is_loaded = True
            return True

        except Exception as e:
            print(f"❌ Error cargando TorchXRayVision model: {e}")
            return False

    def _preprocess(self, img: np.ndarray) -> torch.Tensor:
        """
        Convierte H×W×C numpy array a 1×1×224×224 tensor normalizado.
        Si viene RGB, lo convierte a gris.
        """
        if img.ndim == 3 and img.shape[2] == 3:
            # luminancia estándar
            img = (0.2989 * img[..., 0]
                   + 0.5870 * img[..., 1]
                   + 0.1140 * img[..., 2]).astype(np.uint8)

        x = self.transform(img)             # [1,224,224]
        return x.unsqueeze(0).to(self.device)  # [1,1,224,224]

    async def predict(self, image_array: np.ndarray) -> Dict[str, Any]:
        """
        Devuelve:
          - predicted_class: "Neumonía"|"Normal"
          - prob_neumonia: probabilidad directa
          - confidence: prob ajustada (>=0.5)
          - class_probabilities: dict con ambas
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado")

        x = self._preprocess(image_array)
        with torch.no_grad():
            logits = self.model(x)            # [1, num_pathologies]
            probs = torch.sigmoid(logits)[0]  # [num_pathologies]

        p = float(probs[self.pneumonia_idx])
        label = "Neumonía" if p >= 0.5 else "Normal"
        confidence = p if label == "Neumonía" else (1 - p)

        return {
            "predicted_class":      label,
            "prob_neumonia":        p,
            "confidence":           confidence,
            "class_probabilities": {
                "Neumonía": p,
                "Normal":   1.0 - p
            },
            "raw_predictions": logits.cpu().numpy().tolist()
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "status":       "loaded" if self.is_loaded else "not_loaded",
            "architecture": "densenet121-txrv",
            "device":       str(self.device),
            "num_classes":  len(self.pathology_list)
        }
