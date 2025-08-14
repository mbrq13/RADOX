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
import matplotlib.pyplot as plt
import io
import base64

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
        
        # No necesitamos transform personalizado, usamos el de TorchXRayVision
        self.model: torch.nn.Module = None
        self.is_loaded = False
        
    async def load_model(self) -> bool:
        """Carga el DenseNet121 preentrenado de TorchXRayVision RSNA."""
        try:
            with contextlib.redirect_stdout(sys.stderr):
                # Usar específicamente el modelo RSNA Pneumonia Challenge
                self.model = xrv.models.DenseNet(
                    weights="densenet121-res224-rsna"  # RSNA Pneumonia Challenge
                ).to(self.device).eval()
                
                # Actualizar la lista de patologías del modelo cargado
                self.pathology_list = self.model.targets
                self.pneumonia_idx = self.pathology_list.index("Pneumonia")
                
                print(f"✅ Modelo RSNA cargado: {len(self.pathology_list)} patologías")
                print(f"🎯 Índice de Pneumonia: {self.pneumonia_idx}")
                
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Error cargando TorchXRayVision model: {e}")
            return False
    
    def _preprocess(self, img: np.ndarray) -> torch.Tensor:
        """
        Preprocesa la imagen siguiendo el flujo oficial de TorchXRayVision:
        - Normaliza con xrv.datasets.normalize
        - Convierte a 2D si es necesario
        - Añade canal
        - Aplica XRayCenterCrop y XRayResizer(224)
        - Convierte a tensor y añade batch
        """
        try:
            # Normalizar como en el notebook oficial
            img_normalized = xrv.datasets.normalize(img, 255)
            
            # Convertir a 2D si es necesario
            if img_normalized.ndim == 3:
                img_normalized = img_normalized[:, :, 0]
            
            if img_normalized.ndim < 2:
                raise ValueError("Imagen con menos de 2 dimensiones")
            
            # Añadir canal
            img_with_channel = img_normalized[None, :, :]
            
            # Transformaciones de TorchXRayVision
            transform = T.Compose([
                xrv.datasets.XRayCenterCrop(),
                xrv.datasets.XRayResizer(224)
            ])
            
            img_transformed = transform(img_with_channel)
            
            # Convertir a tensor y añadir batch
            img_tensor = torch.from_numpy(img_transformed).unsqueeze(0)
            
            print(f"[DEBUG] Preprocesamiento: entrada {img.shape} -> salida {img_tensor.shape}")
            return img_tensor
            
        except Exception as e:
            print(f"❌ Error en preprocesamiento: {e}")
            raise

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

        # Obtener probabilidad de neumonía
        p = float(probs[self.pneumonia_idx])
        label = "Neumonía" if p >= 0.5 else "Normal"
        confidence = p if label == "Neumonía" else (1 - p)

        # Mostrar información de debug
        print(f"[DEBUG] Predicciones RSNA:")
        print(f"  🎯 Pneumonia: {p:.4f} ({p*100:.2f}%)")
        print(f"  📊 Total patologías: {len(probs)}")
        print(f"  🏥 Diagnóstico: {label}")

        return {
            "predicted_class":      label,
            "prob_neumonia":        p,
            "confidence":           confidence,
            "class_probabilities": {
                "Neumonía": p,
                "Normal":   1.0 - p
            },
            "raw_predictions": logits.cpu().numpy().tolist(),
            "all_pathologies": dict(zip(self.pathology_list, probs.cpu().numpy().tolist()))
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "status":       "loaded" if self.is_loaded else "not_loaded",
            "architecture": "densenet121-rsna-txrv",
            "weights":      "densenet121-res224-rsna",
            "device":       str(self.device),
            "num_classes":  len(self.pathology_list),
            "pathologies":  self.pathology_list,
            "pneumonia_idx": self.pneumonia_idx
        }

    def get_gradcam_heatmap(self, image_array: np.ndarray) -> str:
        """
        Genera un heatmap Grad-CAM para la clase Neumonía y lo devuelve como imagen base64.
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado")

        # Mostrar rango de la imagen de entrada antes del preprocesamiento
        print(f"[DEBUG] Rango imagen original: min={image_array.min()}, max={image_array.max()}")

        x = self._preprocess(image_array)
        x.requires_grad = True
        self.model.zero_grad()

        # Forward
        logits = self.model(x)
        probs = torch.sigmoid(logits)[0]
        score = probs[self.pneumonia_idx]
        print(f"[DEBUG] Probabilidad de neumonía (prob_neumonia): {float(score):.4f}")

        # Backward para Grad-CAM - MEJORADO para mostrar zonas de enfoque reales
        # Buscar la mejor capa convolucional para Grad-CAM
        target_layer = None
        for i in range(len(self.model.features) - 1, -1, -1):
            if hasattr(self.model.features[i], 'conv'):
                target_layer = self.model.features[i].conv
                break
        if target_layer is None:
            target_layer = self.model.features[-1]  # Fallback a la última capa
        
        print(f"[DEBUG] Usando capa objetivo: {type(target_layer).__name__}")
        
        activations = None
        gradients = None

        def forward_hook(module, input, output):
            nonlocal activations
            activations = output.detach()
        def backward_hook(module, grad_in, grad_out):
            nonlocal gradients
            gradients = grad_out[0].detach()

        handle_fwd = target_layer.register_forward_hook(forward_hook)
        handle_bwd = target_layer.register_backward_hook(backward_hook)

        # Forward y backward
        logits = self.model(x)
        probs = torch.sigmoid(logits)[0]
        score = probs[self.pneumonia_idx]
        self.model.zero_grad()
        score.backward(retain_graph=True)

        handle_fwd.remove()
        handle_bwd.remove()

        # Calcular Grad-CAM MEJORADO para mostrar zonas de enfoque
        if activations is not None and gradients is not None:
            # Calcular pesos de importancia para cada canal
            weights = gradients.mean(dim=[2, 3], keepdim=True)  # [1, C, 1, 1]
            
            # Aplicar pesos a las activaciones para mostrar zonas importantes
            gradcam = (weights * activations).sum(dim=1, keepdim=True)  # [1, 1, H, W]
            
            # Aplicar ReLU para enfatizar solo contribuciones positivas
            gradcam = torch.relu(gradcam)
            
            # Convertir a numpy
            gradcam = gradcam.squeeze().cpu().detach().numpy()
            
            print(f"[DEBUG] gradcam original min: {gradcam.min()}, max: {gradcam.max()}")
            
            # Normalizar de manera más robusta
            gradcam_range = gradcam.max() - gradcam.min()
            if gradcam_range > 1e-8:
                gradcam = (gradcam - gradcam.min()) / gradcam_range
                use_grad_input = False
                print(f"[DEBUG] Grad-CAM normalizado: min={gradcam.min():.6f}, max={gradcam.max():.6f}")
            else:
                print("[DEBUG] Grad-CAM muy pequeño, usando método alternativo")
                use_grad_input = True
        else:
            print("[DEBUG] No se pudieron obtener activaciones/gradientes, usando método alternativo")
            use_grad_input = True

        import cv2
        import matplotlib.pyplot as plt
        import io, base64
        if use_grad_input:
            # --- MÉTODO ALTERNATIVO MEJORADO: gradiente respecto a la entrada ---
            print("[DEBUG] Generando heatmap por gradiente de entrada (método alternativo)")
            x_input = self._preprocess(image_array)
            x_input.requires_grad_()
            out = self.model(x_input)
            score = torch.sigmoid(out)[0][self.pneumonia_idx]
            
            # Calcular gradiente de la salida respecto a la entrada
            grad_input = torch.autograd.grad(score, x_input)[0][0][0]
            grad_input_np = grad_input.detach().cpu().numpy()
            
            # Aplicar valor absoluto para mostrar tanto contribuciones positivas como negativas
            grad_input_abs = np.abs(grad_input_np)
            
            # Aplicar suavizado gaussiano para mejorar la visualización
            from skimage.filters import gaussian
            blurred = gaussian(grad_input_abs, sigma=(3, 3), truncate=2.0)
            
            # Redimensionar a 224x224
            gradcam_resized = cv2.resize(blurred, (224, 224))
            
            # Normalizar de manera más robusta
            if gradcam_resized.max() > gradcam_resized.min():
                gradcam_resized = (gradcam_resized - gradcam_resized.min()) / (gradcam_resized.max() - gradcam_resized.min() + 1e-8)
                print(f"[DEBUG] Heatmap alternativo normalizado: min={gradcam_resized.min():.6f}, max={gradcam_resized.max():.6f}")
            else:
                gradcam_resized = np.zeros_like(gradcam_resized)
                print("[DEBUG] Heatmap alternativo: valores uniformes")
            # DEBUG: Guardar heatmap puro alternativo
            fig2, ax2 = plt.subplots(figsize=(3, 3))
            ax2.axis('off')
            ax2.imshow(gradcam_resized, cmap='jet')
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', bbox_inches='tight', pad_inches=0)
            plt.close(fig2)
            buf2.seek(0)
            heatmap_puro_base64 = base64.b64encode(buf2.read()).decode('utf-8')
            print(f"[DEBUG] heatmap puro grad_input base64: data:image/png;base64,{heatmap_puro_base64[:80]}...")
        else:
            # --- GRAD-CAM CLÁSICO MEJORADO ---
            print("[DEBUG] Usando Grad-CAM clásico mejorado")
            gradcam_resized = cv2.resize(gradcam, (224, 224))
            
            # Aplicar suavizado adicional para mejorar la visualización
            from skimage.filters import gaussian
            gradcam_resized = gaussian(gradcam_resized, sigma=(1, 1), truncate=1.0)
            
            # DEBUG: Guardar heatmap puro clásico
            fig2, ax2 = plt.subplots(figsize=(3, 3))
            ax2.axis('off')
            ax2.imshow(gradcam_resized, cmap='jet')
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', bbox_inches='tight', pad_inches=0)
            plt.close(fig2)
            buf2.seek(0)
            heatmap_puro_base64 = base64.b64encode(buf2.read()).decode('utf-8')
            print(f"[DEBUG] Grad-CAM clásico base64: data:image/png;base64,{heatmap_puro_base64[:80]}...")

        # DEBUG: Mostrar índice y lista de patologías
        print("Índice de Pneumonia:", self.pneumonia_idx)
        print("Lista de patologías:", self.pathology_list)

        # Superponer heatmap sobre la imagen original
        img = x.cpu().squeeze().detach().numpy()
        if img.ndim == 3:
            img = img[0]  # Si tiene forma (1,224,224), tomar solo la imagen
        img = (img * self.std[0] + self.mean[0]) * 255.0
        img = np.clip(img, 0, 255).astype(np.uint8)
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        heatmap = cv2.applyColorMap(np.uint8(255 * gradcam_resized), cv2.COLORMAP_JET)

        # DEPURACIÓN: imprimir shapes
        print(f"[DEBUG] img shape: {img.shape}")
        print(f"[DEBUG] gradcam_resized shape: {gradcam_resized.shape}")
        print(f"[DEBUG] img_color shape: {img_color.shape}")
        print(f"[DEBUG] heatmap shape: {heatmap.shape}")

        # Usar alpha menor para que el heatmap no cubra toda la imagen
        overlay = cv2.addWeighted(img_color, 0.8, heatmap, 0.2, 0)

        # Guardar como base64
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.axis('off')
        ax.imshow(overlay)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    def generate_demo_image_and_report(self, image_type="normal"):
        """
        Genera una imagen de rayos X sintética y un informe simulado.
        image_type: "normal" o "pneumonia"
        Devuelve: (imagen_base64, reporte_texto)
        """
        from PIL import Image, ImageDraw
        import numpy as np
        import io, base64
        # Crear imagen base 512x512
        img = Image.new('L', (512, 512), color=0)
        draw = ImageDraw.Draw(img)
        # Simular patrón pulmonar
        if image_type == "normal":
            for i in range(0, 512, 20):
                for j in range(0, 512, 20):
                    if 100 < i < 400 and 50 < j < 450:
                        intensity = 40 + np.random.randint(0, 30)
                        draw.rectangle([i, j, i+15, j+15], fill=int(intensity))
        elif image_type == "pneumonia":
            for i in range(0, 512, 20):
                for j in range(0, 512, 20):
                    if 100 < i < 400 and 50 < j < 450:
                        if 200 < i < 350 and 200 < j < 350:
                            intensity = 120 + np.random.randint(0, 40)
                        else:
                            intensity = 40 + np.random.randint(0, 30)
                        draw.rectangle([i, j, i+15, j+15], fill=int(intensity))
        # Convertir a base64
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        # Informe simulado
        if image_type == "normal":
            report = "Informe IA: No se detectan signos radiológicos de neumonía."
        else:
            report = "Informe IA: Se detectan opacidades pulmonares compatibles con neumonía."
        return f"data:image/png;base64,{img_base64}", report
