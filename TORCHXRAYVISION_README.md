# TorchXRayVision DenseNet121 RSNA - RADOX

## 📋 Descripción

Este proyecto utiliza el modelo **TorchXRayVision DenseNet121 RSNA** específicamente entrenado para el **RSNA Pneumonia Challenge**. Según la [documentación oficial](https://mlmed.org/torchxrayvision/models.html), este modelo está optimizado para la detección de neumonía en radiografías de tórax.

## 🎯 Características del Modelo

- **Arquitectura**: DenseNet121
- **Resolución**: 224x224 píxeles
- **Dataset**: RSNA Pneumonia Challenge
- **Patologías**: 18 diferentes, incluyendo "Pneumonia"
- **Precisión**: Optimizado para detección de neumonía

## 🚀 Instalación

### Prerrequisitos
- Conda instalado
- Python 3.11+

### Pasos de Instalación

1. **Crear y activar entorno conda:**
   ```bash
   conda create -n radox python=3.11
   conda activate radox
   ```

2. **Ejecutar script de instalación:**
   ```bash
   ./scripts/install_torchxrayvision.sh
   ```

   **⚠️ IMPORTANTE**: Debes tener el entorno `radox` activado antes de ejecutar este script.

3. **Verificar instalación:**
   ```bash
   python -c "import torchxrayvision as xrv; print('✅ Instalación exitosa')"
   ```

## 🧪 Pruebas del Modelo

### Prueba Automática
```bash
./scripts/test_radox_env.sh
```

### Prueba Manual
```bash
conda activate radox
python scripts/test_torchxrayvision_model.py
```

## 📊 Patologías Disponibles

El modelo RSNA incluye las siguientes patologías:
- Atelectasis
- Consolidation
- Infiltration
- Pneumothorax
- Edema
- Emphysema
- Fibrosis
- Effusion
- **Pneumonia** ← **OBJETIVO PRINCIPAL**
- Pleural_Thickening
- Cardiomegaly
- Nodule
- Mass
- Hernia
- Lung Lesion
- Fracture
- Lung Opacity
- Enlarged Cardiomediastinum

## 🔍 Uso del Modelo

### En el Backend
El modelo se carga automáticamente en `backend/models/cnn_model.py`:

```python
# Carga del modelo RSNA
model = xrv.models.DenseNet(weights="densenet121-res224-rsna")
```

### Predicciones
```python
# Preprocesamiento automático
x = self._preprocess(image_array)

# Inferencia
with torch.no_grad():
    logits = self.model(x)
    probs = torch.sigmoid(logits)[0]

# Probabilidad de neumonía
pneumonia_prob = probs[self.pneumonia_idx]
```

## 🎨 Generación de Heatmaps

El modelo incluye dos métodos para generar heatmaps:

1. **Grad-CAM Clásico**: Usando activaciones de la última capa convolucional
2. **Gradiente de Entrada**: Método alternativo con Gaussian blur (como en `heatmaps.ipynb`)

## 📁 Archivos Principales

- `backend/models/cnn_model.py` - Implementación del modelo
- `scripts/test_torchxrayvision_model.py` - Script de prueba completo
- `scripts/install_torchxrayvision.sh` - Instalación automática
- `scripts/test_radox_env.sh` - Verificación del entorno

## 🚨 Solución de Problemas

### Error: "Entorno conda no activado"
```bash
conda activate radox
./scripts/install_torchxrayvision.sh
```

### Error: "TorchXRayVision no encontrado"
```bash
conda activate radox
pip install torchxrayvision
```

### Error: "PyTorch no encontrado"
```bash
conda activate radox
pip install torch torchvision torchaudio
```

## 🔧 Configuración del Backend

Para ejecutar el backend con el modelo TorchXRayVision:

```bash
conda activate radox
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📈 Rendimiento

- **Tiempo de carga**: ~2-5 segundos (primera vez)
- **Tiempo de inferencia**: <1 segundo por imagen
- **Memoria**: ~500MB (CPU), ~1GB (GPU)
- **Precisión**: Optimizada para RSNA Pneumonia Challenge

## 🌐 API Endpoints

- `POST /api/v1/detect` - Detección de neumonía
- `GET /api/v1/model/info` - Información del modelo
- `POST /api/v1/heatmap` - Generación de heatmap

## 📚 Referencias

- [Documentación TorchXRayVision](https://mlmed.org/torchxrayvision/models.html)
- [RSNA Pneumonia Challenge](https://www.kaggle.com/c/rsna-pneumonia-detection-challenge)
- [Paper DenseNet](https://arxiv.org/abs/1608.06993)

## 🤝 Contribución

Para contribuir al proyecto:

1. Activa el entorno conda: `conda activate radox`
2. Instala dependencias: `./scripts/install_torchxrayvision.sh`
3. Ejecuta pruebas: `./scripts/test_radox_env.sh`
4. Realiza cambios y verifica que las pruebas pasen

---

**🎉 ¡El modelo TorchXRayVision DenseNet121 RSNA está listo para usar en RADOX!**
