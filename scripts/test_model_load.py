#!/usr/bin/env python3
# test_model_load.py
"""
Script de prueba e inspección para archivos .h5 de Keras/TensorFlow:
  1. Intenta cargar el modelo completo con keras.models.load_model().
  2. Si falla, abre el .h5 con h5py y lista su contenido raíz.
  3. Extrae y muestra la configuración JSON del modelo, incluyendo el input_shape.
"""

import os
import sys
import json
import logging

import h5py
from tensorflow import keras

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger("test_model_load")


def try_load_full_model(path: str) -> bool:
    """Intenta cargar el modelo completo desde el .h5 y mostrar summary()."""
    log.info(f"👉 Intentando keras.models.load_model('{path}')")
    model = keras.models.load_model(path)
    log.info("✅ Modelo completo cargado correctamente. Summary:")
    model.summary()
    return True


def inspect_h5_file(path: str) -> None:
    """
    Inspecciona un archivo HDF5 (.h5):
      - Lista grupos en el nivel raíz.
      - Muestra si existe atributo `model_config` y extrae el input_shape.
    """
    log.info(f"🔍 Abriendo archivo HDF5 para inspección: {path}")
    with h5py.File(path, 'r') as f:
        root_keys = list(f.keys())
        log.info("📂 Claves en el nivel raíz:")
        for key in root_keys:
            item = f[key]
            kind = "Group" if isinstance(item, h5py.Group) else "Dataset"
            log.info(f"  • {key} ({kind})")

        if 'model_config' in f.attrs:
            raw = f.attrs['model_config']
            try:
                conf = raw.decode('utf-8') if isinstance(raw, (bytes, bytearray)) else str(raw)
                config = json.loads(conf)
                log.info("🏷️  Atributo 'model_config' encontrado. Extrayendo input_shape…")
                layers = config.get("config", {}).get("layers", [])
                if layers:
                    batch_input_shape = layers[0].get("config", {}).get("batch_input_shape")
                    log.info(f"📐 Modelo espera input_shape = {batch_input_shape}")
                else:
                    log.warning("⚠️  No se encontraron capas en el model_config.")
            except Exception as e:
                log.error(f"❌ Error al procesar 'model_config': {e}")
        else:
            log.warning("⚠️  No existe atributo 'model_config' en el HDF5.")


def main():
    if len(sys.argv) != 2:
        print("Uso: python test_model_load.py path/to/model.h5")
        sys.exit(1)

    model_path = sys.argv[1]
    if not os.path.isfile(model_path):
        log.error(f"❌ Archivo no encontrado: {model_path}")
        sys.exit(1)

    try:
        try_load_full_model(model_path)
        sys.exit(0)
    except Exception as e:
        log.warning(f"❌ load_model() falló: {e}")

    inspect_h5_file(model_path)
    log.info("🏁 Inspección completada.")


if __name__ == "__main__":
    main()
