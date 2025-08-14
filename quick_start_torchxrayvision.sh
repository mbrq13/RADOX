#!/bin/bash
# quick_start_torchxrayvision.sh
# Script de inicio rápido para TorchXRayVision en RADOX

echo "🚀 INICIO RÁPIDO - TorchXRayVision DenseNet121 RSNA"
echo "=================================================="

# Verificar si conda está disponible
if ! command -v conda &> /dev/null; then
    echo "❌ ERROR: Conda no está instalado o no está en el PATH"
    echo "💡 Instala conda primero: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Verificar si el entorno radox existe
if ! conda env list | grep -q "radox"; then
    echo "🔄 Creando entorno conda 'radox'..."
    conda create -n radox python=3.11 -y
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: No se pudo crear el entorno 'radox'"
        exit 1
    fi
fi

# Activar entorno radox
echo "🔄 Activando entorno conda 'radox'..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate radox

# Verificar activación
if [[ "$CONDA_DEFAULT_ENV" != "radox" ]]; then
    echo "❌ ERROR: No se pudo activar el entorno 'radox'"
    exit 1
fi

echo "✅ Entorno conda 'radox' activado correctamente"
echo "📊 Entorno actual: $CONDA_DEFAULT_ENV"
echo "🐍 Python: $(which python)"
echo "📦 Versión Python: $(python --version)"

# Verificar si TorchXRayVision ya está instalado
if python -c "import torchxrayvision" 2>/dev/null; then
    echo "✅ TorchXRayVision ya está instalado"
else
    echo "📦 Instalando TorchXRayVision y dependencias..."
    
    # Instalar PyTorch
    echo "  - Instalando PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    # Instalar TorchXRayVision
    echo "  - Instalando TorchXRayVision..."
    pip install torchxrayvision
    
    # Instalar dependencias adicionales
    echo "  - Instalando dependencias adicionales..."
    pip install matplotlib pillow scikit-image opencv-python
    
    echo "✅ Instalación completada"
fi

# Verificar instalación
echo "🔍 Verificando instalación..."
python -c "
import torch
import torchxrayvision as xrv
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ TorchXRayVision: {xrv.__version__}')
print('✅ Todas las dependencias están instaladas correctamente')
"

echo ""
echo "🧪 EJECUTANDO PRUEBAS DEL MODELO..."
echo "=================================="

# Ejecutar script de prueba
python scripts/test_torchxrayvision_model.py

echo ""
echo "🎉 ¡PRUEBAS COMPLETADAS!"
echo ""
echo "💡 Para mantener el entorno activo:"
echo "   conda activate radox"
echo ""
echo "💡 Para ejecutar el backend:"
echo "   conda activate radox"
echo "   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "💡 Para más información, consulta: TORCHXRAYVISION_README.md"
