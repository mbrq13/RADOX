import argparse
import os
import sys
from huggingface_hub import InferenceClient
import base64

parser = argparse.ArgumentParser(description='Generar informe con MedGemma 4b-it')
parser.add_argument('--prompt', type=str, required=True, help='Prompt para el modelo')
parser.add_argument('--image-path', type=str, required=True, help='Ruta local de la imagen a analizar')
args = parser.parse_args()

hf_token = os.environ.get('HF_TOKEN')
if not hf_token:
    print('ERROR: No se encontró el token HF_TOKEN en el entorno', file=sys.stderr)
    sys.exit(1)

client = InferenceClient(
    provider="featherless-ai",
    api_key=hf_token,
)

# Leer imagen local y convertir a base64
try:
    with open(args.image_path, 'rb') as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
except Exception as e:
    print(f'ERROR al leer la imagen local: {e}', file=sys.stderr)
    sys.exit(2)

# Construir el mensaje con imagen en base64 (si la API lo permite)
try:
    completion = client.chat.completions.create(
        model="google/medgemma-4b-it",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": args.prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ],
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(3) 