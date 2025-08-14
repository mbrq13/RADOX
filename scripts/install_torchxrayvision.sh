#!/bin/bash
# install_torchxrayvision.sh
# Script para instalar TorchXRayVision en el entorno conda radox

echo "🚀 Instalando TorchXRayVision en entorno conda 'radox'..."

# Verificar que estamos en el entorno radox
if [[ "$CONDA_DEFAULT_ENV" != "radox" ]]; then
    echo "❌ ERROR: Debes activar el entorno conda 'radox' primero"
    echo "💡 Ejecuta: conda activate radox"
    echo "💡 Luego ejecuta este script nuevamente"
    exit 1
fi

echo "✅ Entorno conda 'radox' activado correctamente"
echo "📊 Entorno actual: $CONDA_DEFAULT_ENV"
echo "🐍 Python: $(which python)"
echo "📦 Versión Python: $(python --version)"

# Instalar PyTorch (CPU por defecto)
echo "📦 Instalando PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Instalar TorchXRayVision
echo "📦 Instalando TorchXRayVision..."
pip install torchxrayvision

# Instalar dependencias adicionales
echo "📦 Instalando dependencias adicionales..."
pip install matplotlib pillow scikit-image opencv-python

# Verificar instalación
echo "🔍 Verificando instalación..."
python -c "
import torch
import torchxrayvision as xrv
print(f'✅ PyTorch version: {torch.__version__}')
print(f'✅ TorchXRayVision version: {xrv.__version__}')
print('✅ Instalación completada exitosamente')
"

echo "🎉 Instalación completada en entorno 'radox'!"
echo ""
echo "💡 Para probar el modelo, ejecuta:"
echo "   conda activate radox"
echo "   python scripts/test_torchxrayvision_model.py"
echo ""
echo "💡 Para ejecutar el backend:"
echo "   conda activate radox"
echo "   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
