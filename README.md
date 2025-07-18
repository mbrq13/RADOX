# RADOX - Sistema de Detección de Neumonía con IA

## Descripción

RADOX es un sistema completo para la detección automática de neumonía en radiografías de tórax utilizando inteligencia artificial. El sistema está diseñado para ser desplegado localmente y proporciona una API REST para subir imágenes, analizar resultados y generar informes médicos automáticos.

**Versión actual:** Utiliza un modelo CNN (ResNet50) para la detección y la API de Hugging Face (MedGemma) para la generación de informes médicos.

---

## Características principales

- **Detección de neumonía:** Utiliza un modelo CNN ResNet50 entrenado para clasificar radiografías de tórax como "Normal" o "Neumonía".
- **Generación de informes médicos:** Integra la API de Hugging Face (MedGemma) para crear informes médicos automáticos a partir de los resultados de la CNN.
- **API REST:** Proporciona endpoints para subir imágenes (JPG, PNG, DICOM), obtener predicciones y generar informes.
- **Despliegue sencillo:** Instalación y ejecución con comandos simples.
- **Sin dependencias complejas:** No requiere bases de datos vectoriales ni servicios adicionales.

---

## Flujo de trabajo del sistema

1. **Subida de imagen:**
   - El usuario envía una radiografía de tórax (JPG, PNG o DICOM) a través de la API.

2. **Predicción con CNN:**
   - El backend procesa la imagen y utiliza el modelo CNN para predecir si la imagen muestra neumonía o es normal.
   - Se calcula el nivel de confianza y se genera una recomendación clínica automática.

3. **Generación de informe médico:**
   - El usuario puede solicitar la generación de un informe médico.
   - El sistema envía los resultados de la CNN a la API de Hugging Face (MedGemma), que devuelve un informe médico profesional en texto.

4. **Respuesta de la API:**
   - La API devuelve el diagnóstico, la confianza, la recomendación y el informe médico generado.

---

## Instalación y despliegue

### Opción 1: Con Conda (Recomendado)

1. **Crear entorno conda:**
   ```bash
   conda create -n radox python=3.11
   conda activate radox
   ```

2. **Instalación de dependencias:**
   ```bash
   ./setup.sh
   ```

3. **Configuración:**
   - Copia `env.example` a `.env` y añade tu token de Hugging Face.

4. **Ejecución:**
   ```bash
   ./run.sh
   ```

5. **Acceso:**
   - API: http://localhost:8000
   - Documentación API: http://localhost:8000/docs

### Opción 2: Sin Docker (Desarrollo)

1. **Activar entorno conda:**
   ```bash
   conda activate radox
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp env.example .env
   # Editar .env y agregar tu token de Hugging Face
   ```

4. **Ejecutar backend:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## Configuración de credenciales

### Token de Hugging Face

1. **Obtener token:**
   - Ve a https://huggingface.co/settings/tokens
   - Crea un nuevo token con permisos de lectura

2. **Configurar token:**
   - Edita el archivo `.env`
   - Reemplaza `your_hf_token_here` con tu token real:
   ```
   HUGGINGFACE_TOKEN=tu_token_aqui
   ```

---

## Estructura del proyecto

```
RADOX/
├── backend/                 # Backend FastAPI
│   ├── api/routes/         # Endpoints de la API
│   ├── models/             # Modelos de IA
│   ├── services/           # Servicios de negocio
│   ├── config/             # Configuración
│   └── utils/              # Utilidades
├── data/                   # Datos del sistema
│   ├── models/             # Modelos pre-entrenados
│   └── uploads/            # Imágenes subidas
├── scripts/                # Scripts de utilidad
├── tests/                  # Tests unitarios
├── requirements.txt        # Dependencias Python
├── docker-compose.yml      # Configuración Docker
├── setup.sh               # Script de instalación
└── run.sh                 # Script de ejecución
```

---

## Endpoints de la API

- `POST /api/v1/detect` - Detectar neumonía en imagen
- `POST /api/v1/report` - Generar informe médico
- `GET /health` - Verificar estado del sistema
- `GET /docs` - Documentación interactiva

---

## Tecnologías utilizadas

- **Backend:** Python 3.11, FastAPI, TensorFlow (CNN), Uvicorn
- **IA Médica:** ResNet50 (detección), MedGemma (informes, vía Hugging Face API)
- **Contenedores:** Docker, Docker Compose (opcional)

---

## Notas importantes

- **Este sistema es solo para fines educativos y de investigación.** No debe usarse para diagnóstico médico real.
- **No se almacena información médica ni imágenes en bases de datos.**
- **El flujo es directo:** imagen → predicción CNN → informe MedGemma → respuesta API.

---

## Contacto

Para dudas o soporte, contacta al equipo de desarrollo de RADOX. 