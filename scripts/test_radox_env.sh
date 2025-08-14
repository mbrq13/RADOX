#!/bin/bash
# test_radox_env.sh
# Script para verificar y activar el entorno conda radox antes de ejecutar pruebas

echo "🔍 Verificando entorno conda..."

# Verificar si conda está disponible
if ! command -v conda &> /dev/null; then
    echo "❌ ERROR: Conda no está instalado o no está en el PATH"
    echo "💡 Instala conda primero o verifica tu configuración"
    exit 1
fi

# Verificar si el entorno radox existe
if ! conda env list | grep -q "radox"; then
    echo "❌ ERROR: El entorno conda 'radox' no existe"
    echo "💡 Crea el entorno primero con: conda create -n radox python=3.11"
    exit 1
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

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python -c "
try:
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
except ImportError:
    print('❌ PyTorch: No instalado')

try:
    import torchxrayvision as xrv
    print(f'✅ TorchXRayVision: {xrv.__version__}')
except ImportError:
    print('❌ TorchXRayVision: No instalado')

try:
    import matplotlib
    print(f'✅ Matplotlib: {matplotlib.__version__}')
except ImportError:
    print('❌ Matplotlib: No instalado')
"

echo ""
echo "🚀 Ejecutando prueba del modelo TorchXRayVision..."
python scripts/test_torchxrayvision_model.py

echo ""
echo "🏁 Prueba completada. Para mantener el entorno activo:"
echo "   conda activate radox"
