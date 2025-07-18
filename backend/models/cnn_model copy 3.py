# backend/models/cnn_model.py

"""
Modelo CNN para Detección de Neumonía
-------------------------------------
- Fuerza ejecución en CPU para evitar JIT/GPU errors.
- Soporta tanto modelos con 2 salidas (softmax) como 1 salida (sigmoid).
- Incluye Grad‑CAM heatmap.
"""

import os
# 1) Desactivar GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf
tf.config.optimizer.set_jit(False)
tf.config.run_functions_eagerly(True)

import json
import logging
import h5py
import numpy as np
from tensorflow import keras

logger = logging.getLogger(__name__)


class CNNModel:
    """Modelo CNN para detección de neumonía en radiografías de tórax."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        self.input_shape = (150, 150, 3)
        # Nota: asumimos index 0 = Normal, 1 = Neumonía
        self.class_names = ["Normal", "Neumonía"]

    async def load_model(self) -> bool:
        """Carga tu model.h5 (o reconstruye desde model_config)."""
        try:
            logger.info(f"Cargando modelo con keras.models.load_model: {self.model_path}")
            self.model = keras.models.load_model(self.model_path)
            self.input_shape = tuple(self.model.input_shape[1:])
            self.is_loaded = True
            logger.info(f"✅ Modelo cargado. Input shape = {self.input_shape}")
            return True
        except Exception as e:
            logger.warning(f"❌ load_model() falló: {e}")
            logger.info("🔄 Intentando reconstruir arquitectura desde model_config…")

        try:
            with h5py.File(self.model_path, 'r') as f:
                raw = f.attrs.get('model_config')
            if raw is None:
                raise ValueError("No existe 'model_config' en el HDF5")
            cfg = raw.decode('utf-8') if isinstance(raw, (bytes, bytearray)) else raw
            config = json.loads(cfg)
            self.model = keras.models.model_from_config(config['config'])
            self.model.load_weights(self.model_path)
            self.input_shape = tuple(self.model.input_shape[1:])
            self.is_loaded = True
            logger.info(f"✅ Arquitectura restaurada. Input shape = {self.input_shape}")
            return True
        except Exception as e2:
            logger.error(f"❌ No se pudo reconstruir el modelo: {e2}")
            return False

    def preprocess(self, image_array: np.ndarray) -> np.ndarray:
        """Redimensiona a input_shape, normaliza y añade batch."""
        if image_array.ndim == 2:
            image_array = np.stack([image_array]*3, axis=-1)
        h, w, _ = self.input_shape
        img = tf.image.resize(image_array, [h, w]).numpy()
        img = img.astype('float32') / 255.0
        return np.expand_dims(img, axis=0)

    async def predict(self, image_array: np.ndarray) -> dict:
        """
        Predict + Grad‑CAM.
        Devuelve:
          - predicted_class, confidence, class_probabilities,
            heatmap (2D [0–1]), raw_predictions, has_pneumonia, prob_neumonia
        """
        if not self.is_loaded or self.model is None:
            raise ValueError("Modelo no está cargado")

        batch = self.preprocess(image_array)

        # Forzar CPU
        with tf.device('/CPU:0'):
            raw_preds = self.model.predict(batch, verbose=0)

        preds = np.array(raw_preds).reshape(-1).astype(float)
        # Guarda salida cruda
        raw_list = preds.tolist()

        # Determinar etiqueta y probabilidades
        if preds.size == 1:
            # Sigmoid single-output
            p = preds[0]
            class_probs = {
                "Normal": 1 - p,
                "Neumonía": p
            }
            idx = 1 if p >= 0.5 else 0
            confidence = p if idx == 1 else 1 - p
            has_pneumonia = (idx == 1)
            prob_neumonia = p
            grad_index = 0   # **SIEMPRE 0** en salida única
        else:
            # Softmax 2-output
            idx = int(np.argmax(preds))
            confidence = float(preds[idx])
            class_probs = {
                self.class_names[i]: float(preds[i]) for i in range(len(self.class_names))
            }
            has_pneumonia = (idx == 1)
            prob_neumonia = float(preds[1])
            grad_index = idx

        # Grad‑CAM
        heatmap = self._make_gradcam_heatmap(batch, grad_index)

        return {
            "predicted_class": self.class_names[idx],
            "confidence": confidence,
            "class_probabilities": class_probs,
            "heatmap": heatmap.tolist(),
            "raw_predictions": raw_list,
            "has_pneumonia": has_pneumonia,
            "prob_neumonia": prob_neumonia
        }

    def _make_gradcam_heatmap(self, img_array: np.ndarray, class_index: int) -> np.ndarray:
        """Grad‑CAM sobre la última capa conv."""
        last_conv_name = None
        for layer in reversed(self.model.layers):
            if len(layer.output_shape) == 4:
                last_conv_name = layer.name
                break

        grad_model = keras.models.Model(
            inputs=self.model.inputs,
            outputs=[
                self.model.get_layer(last_conv_name).output,
                self.model.output
            ]
        )

        with tf.GradientTape() as tape:
            conv_out, predictions = grad_model(img_array)
            # predictions[:, class_index] siempre válido:
            loss = predictions[:, class_index]
        grads = tape.gradient(loss, conv_out)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2)).numpy()
        conv_values = conv_out.numpy()[0]

        for i in range(pooled_grads.shape[-1]):
            conv_values[:, :, i] *= pooled_grads[i]

        heatmap = np.mean(conv_values, axis=-1)
        heatmap = np.maximum(heatmap, 0)
        heatmap /= (np.max(heatmap) + 1e-8)
        return heatmap

    def get_model_info(self) -> dict:
        """Información para el puente JS."""
        if not self.is_loaded or self.model is None:
            return {"status": "not_loaded"}
        return {
            "status": "loaded",
            "architecture": getattr(self.model, "name", None),
            "input_shape": self.input_shape,
            "params": int(self.model.count_params()),
            "model_path": self.model_path
        }
