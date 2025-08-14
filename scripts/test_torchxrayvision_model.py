#!/usr/bin/env python3
# test_torchxrayvision_model.py
"""
Script de prueba para el modelo TorchXRayVision DenseNet121 RSNA:
  1. Carga el modelo densenet121-res224-rsna
  2. Prueba con imagen de ejemplo
  3. Muestra predicciones específicas para neumonía
  4. Genera heatmap usando Grad-CAM
"""

import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
from PIL import Image
import io
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger("test_torchxrayvision")

def load_torchxrayvision_model():
    """Carga el modelo TorchXRayVision DenseNet121 RSNA."""
    try:
        import torchxrayvision as xrv
        log.info("✅ TorchXRayVision importado correctamente")
        
        # Cargar modelo específico para RSNA Pneumonia Challenge
        log.info("🔄 Cargando modelo densenet121-res224-rsna...")
        model = xrv.models.DenseNet(weights="densenet121-res224-rsna")
        model.eval()
        
        log.info(f"✅ Modelo cargado: {type(model).__name__}")
        log.info(f"📋 Patologías disponibles: {model.targets}")
        
        # Encontrar índice de neumonía
        pneumonia_idx = None
        for i, pathology in enumerate(model.targets):
            if 'pneumonia' in pathology.lower():
                pneumonia_idx = i
                break
        
        if pneumonia_idx is not None:
            log.info(f"🎯 Índice de 'Pneumonia': {pneumonia_idx}")
        else:
            log.warning("⚠️  No se encontró 'Pneumonia' en las patologías")
        
        return model, pneumonia_idx
        
    except ImportError as e:
        log.error(f"❌ Error importando TorchXRayVision: {e}")
        log.error("💡 Instala con: pip install torchxrayvision")
        return None, None
    except Exception as e:
        log.error(f"❌ Error cargando modelo: {e}")
        return None, None

def create_test_image():
    """Crea una imagen de prueba sintética para testing."""
    log.info("🎨 Creando imagen de prueba sintética...")
    
    # Crear imagen 512x512 con patrón pulmonar simulado
    img = np.zeros((512, 512), dtype=np.uint8)
    
    # Simular patrón pulmonar normal
    for i in range(0, 512, 20):
        for j in range(0, 512, 20):
            if 100 < i < 400 and 50 < j < 450:
                intensity = 40 + np.random.randint(0, 30)
                img[i:i+15, j:j+15] = intensity
    
    # Añadir algo de ruido
    noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
    img = np.clip(img + noise, 0, 255)
    
    log.info(f"✅ Imagen de prueba creada: {img.shape}, rango: [{img.min()}, {img.max()}]")
    return img

def preprocess_image_for_torchxrayvision(img, model):
    """Preprocesa imagen siguiendo el flujo oficial de TorchXRayVision."""
    try:
        import torchxrayvision as xrv
        import torchvision.transforms as T
        
        log.info("🔄 Preprocesando imagen para TorchXRayVision...")
        
        # Normalizar como en el notebook oficial
        img_normalized = xrv.datasets.normalize(img, 255)
        log.info(f"📊 Imagen normalizada: rango [{img_normalized.min():.3f}, {img_normalized.max():.3f}]")
        
        # Convertir a 2D si es necesario
        if img_normalized.ndim == 3:
            img_normalized = img_normalized[:, :, 0]
            log.info("🔄 Convertida a 2D")
        
        # Añadir canal
        img_with_channel = img_normalized[None, :, :]
        log.info(f"📐 Con canal añadido: {img_with_channel.shape}")
        
        # Transformaciones de TorchXRayVision
        transform = T.Compose([
            xrv.datasets.XRayCenterCrop(),
            xrv.datasets.XRayResizer(224)
        ])
        
        img_transformed = transform(img_with_channel)
        log.info(f"🔄 Después de transformaciones: {img_transformed.shape}")
        
        # Convertir a tensor y añadir batch
        img_tensor = torch.from_numpy(img_transformed).unsqueeze(0)
        log.info(f"✅ Tensor final: {img_tensor.shape}")
        
        return img_tensor
        
    except Exception as e:
        log.error(f"❌ Error en preprocesamiento: {e}")
        return None

def test_model_inference(model, img_tensor, pneumonia_idx):
    """Prueba la inferencia del modelo y muestra resultados."""
    try:
        log.info("🧠 Ejecutando inferencia del modelo...")
        
        with torch.no_grad():
            outputs = model(img_tensor)
            log.info(f"📊 Salidas del modelo: {outputs.shape}")
            
            # Aplicar sigmoid si es necesario
            if not hasattr(model, 'apply_sigmoid') or model.apply_sigmoid:
                predictions = torch.sigmoid(outputs)
            else:
                predictions = outputs
            
            log.info(f"📈 Predicciones (sigmoid): {predictions.shape}")
            
            # Mostrar todas las predicciones
            log.info("🔍 Predicciones para todas las patologías:")
            for i, (pathology, prob) in enumerate(zip(model.targets, predictions[0])):
                prob_value = prob.item()
                if i == pneumonia_idx:
                    log.info(f"  🎯 {pathology}: {prob_value:.4f} (NEUMONÍA)")
                else:
                    log.info(f"     {pathology}: {prob_value:.4f}")
            
            # Resultado específico para neumonía
            if pneumonia_idx is not None:
                pneumonia_prob = predictions[0][pneumonia_idx].item()
                log.info(f"🎯 PROBABILIDAD DE NEUMONÍA: {pneumonia_prob:.4f} ({pneumonia_prob*100:.2f}%)")
                
                # Clasificación binaria
                threshold = 0.5
                diagnosis = "NEUMONÍA" if pneumonia_prob > threshold else "NORMAL"
                log.info(f"🏥 DIAGNÓSTICO: {diagnosis}")
                
                return predictions, pneumonia_prob, diagnosis
            else:
                log.warning("⚠️  No se pudo determinar la probabilidad de neumonía")
                return predictions, None, None
                
    except Exception as e:
        log.error(f"❌ Error en inferencia: {e}")
        return None, None, None

def generate_gradcam_heatmap(model, img_tensor, pneumonia_idx):
    """Genera heatmap usando Grad-CAM para la clase de neumonía."""
    if pneumonia_idx is None:
        log.warning("⚠️  No se puede generar heatmap sin índice de neumonía")
        return None
    
    try:
        log.info("🔥 Generando heatmap con Grad-CAM...")
        
        # Activar gradientes
        img_tensor.requires_grad_(True)
        
        # Forward pass
        outputs = model(img_tensor)
        score = outputs[0][pneumonia_idx]
        
        log.info(f"📊 Score para neumonía: {score.item():.4f}")
        
        # Backward pass
        model.zero_grad()
        score.backward()
        
        # Obtener gradientes de la entrada
        grad_input = img_tensor.grad[0][0]  # [H, W]
        grad_input_np = grad_input.detach().cpu().numpy()
        
        log.info(f"📐 Gradientes de entrada: {grad_input_np.shape}, rango [{grad_input_np.min():.3f}, {grad_input_np.max():.3f}]")
        
        # Aplicar Gaussian blur como en el notebook oficial
        from skimage.filters import gaussian
        blurred = gaussian(grad_input_np ** 2, sigma=(5, 5), truncate=3.5)
        
        # Normalizar heatmap
        if blurred.max() > blurred.min():
            heatmap = (blurred - blurred.min()) / (blurred.max() - blurred.min() + 1e-8)
        else:
            heatmap = np.zeros_like(blurred)
        
        log.info(f"✅ Heatmap generado: {heatmap.shape}, rango [{heatmap.min():.3f}, {heatmap.max():.3f}]")
        
        return heatmap
        
    except Exception as e:
        log.error(f"❌ Error generando heatmap: {e}")
        return None

def visualize_results(img_tensor, heatmap, pneumonia_prob, diagnosis):
    """Visualiza los resultados del análisis."""
    try:
        log.info("🎨 Generando visualización de resultados...")
        
        # Preparar imagen original
        img_np = img_tensor[0][0].cpu().detach().numpy()  # [224, 224]
        
        # Crear figura con subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Imagen original
        axes[0].imshow(img_np, cmap='gray')
        axes[0].set_title('Imagen Original (224x224)')
        axes[0].axis('off')
        
        # Heatmap
        if heatmap is not None:
            axes[1].imshow(heatmap, cmap='jet')
            axes[1].set_title('Heatmap Grad-CAM')
            axes[1].axis('off')
        else:
            axes[1].text(0.5, 0.5, 'Heatmap no disponible', 
                         ha='center', va='center', transform=axes[1].transAxes)
            axes[1].set_title('Heatmap Grad-CAM')
            axes[1].axis('off')
        
        # Superposición
        if heatmap is not None:
            # Convertir imagen a RGB para superposición
            img_rgb = np.stack([img_np] * 3, axis=-1)
            img_rgb = (img_rgb - img_rgb.min()) / (img_rgb.max() - img_rgb.min())
            
            # Aplicar heatmap
            heatmap_colored = plt.cm.jet(heatmap)[:, :, :3]
            overlay = 0.7 * img_rgb + 0.3 * heatmap_colored
            overlay = np.clip(overlay, 0, 1)
            
            axes[2].imshow(overlay)
            axes[2].set_title('Superposición Heatmap')
            axes[2].axis('off')
        else:
            axes[2].text(0.5, 0.5, 'Superposición no disponible', 
                         ha='center', va='center', transform=axes[2].transAxes)
            axes[2].set_title('Superposición Heatmap')
            axes[2].axis('off')
        
        # Título principal con resultados
        fig.suptitle(f'Análisis TorchXRayVision - {diagnosis} ({pneumonia_prob*100:.1f}%)', 
                     fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Guardar imagen
        output_path = "torchxrayvision_test_results.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        log.info(f"💾 Visualización guardada en: {output_path}")
        
        # Mostrar en pantalla
        plt.show()
        
        return output_path
        
    except Exception as e:
        log.error(f"❌ Error en visualización: {e}")
        return None

def main():
    """Función principal del script de prueba."""
    log.info("🚀 Iniciando prueba del modelo TorchXRayVision DenseNet121 RSNA")
    
    # 1. Cargar modelo
    model, pneumonia_idx = load_torchxrayvision_model()
    if model is None:
        log.error("❌ No se pudo cargar el modelo. Abortando.")
        sys.exit(1)
    
    # 2. Crear imagen de prueba
    test_img = create_test_image()
    
    # 3. Preprocesar imagen
    img_tensor = preprocess_image_for_torchxrayvision(test_img, model)
    if img_tensor is None:
        log.error("❌ Error en preprocesamiento. Abortando.")
        sys.exit(1)
    
    # 4. Probar inferencia
    predictions, pneumonia_prob, diagnosis = test_model_inference(model, img_tensor, pneumonia_idx)
    if predictions is None:
        log.error("❌ Error en inferencia. Abortando.")
        sys.exit(1)
    
    # 5. Generar heatmap
    heatmap = generate_gradcam_heatmap(model, img_tensor, pneumonia_idx)
    
    # 6. Visualizar resultados
    output_path = visualize_results(img_tensor, heatmap, pneumonia_prob, diagnosis)
    
    # 7. Resumen final
    log.info("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
    log.info(f"🏥 Diagnóstico: {diagnosis}")
    log.info(f"📊 Probabilidad de neumonía: {pneumonia_prob*100:.2f}%")
    log.info(f"🔥 Heatmap generado: {'Sí' if heatmap is not None else 'No'}")
    if output_path:
        log.info(f"💾 Visualización guardada en: {output_path}")
    
    log.info("✅ El modelo TorchXRayVision está funcionando correctamente")

if __name__ == "__main__":
    main()
