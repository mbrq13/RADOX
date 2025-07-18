# Guía de Instalación RADOX - Versión Simplificada

## Resumen del Proyecto

RADOX es un sistema de detección de neumonía que utiliza:
- **CNN ResNet50** para detectar neumonía en radiografías
- **API de Hugging Face (MedGemma)** para generar informes médicos
- **FastAPI** como backend
- **Sin RAG, vector store ni servicios complejos**

---

## Archivos Principales del Proyecto

### Backend (API)
- `backend/main.py` - Aplicación principal FastAPI
- `backend/config/settings.py` - Configuración del sistema
- `backend/models/cnn_model.py` - Modelo CNN para detección
- `backend/services/pneumonia_detection.py` - Servicio de detección
- `backend/services/report_generation.py` - Servicio de informes
- `backend/api/routes/pneumonia.py` - Endpoints de detección
- `backend/api/routes/reports.py` - Endpoints de informes

### Configuración
- `requirements.txt` - Dependencias Python
- `env.example` - Variables de entorno de ejemplo
- `.env` - Variables de entorno (crear desde ejemplo)
- `docker-compose.yml` - Configuración Docker (opcional)

### Scripts
- `setup_conda.sh` - Instalación con Conda
- `run_dev.sh` - Ejecución en desarrollo (sin Docker)
- `run.sh` - Ejecución con Docker
- `scripts/download_models.py` - Descarga de modelos

---

## Instalación Paso a Paso

### 1. Prerrequisitos

**Instalar Miniconda:**
```bash
# Descargar Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Reiniciar terminal o ejecutar:
source ~/.bashrc
```

**Instalar Docker (opcional):**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Reiniciar sesión o ejecutar: newgrp docker
```

### 2. Instalación Automática con Conda

```bash
# Ejecutar script de instalación
./setup_conda.sh
```

**El script hace:**
- Verifica que conda esté instalado
- Crea entorno conda 'radox' con Python 3.11
- Crea estructura de directorios
- Instala dependencias Python
- Configura archivo .env
- Descarga modelos (si el token está configurado)

### 3. Configurar Token de Hugging Face

**Obtener token:**
1. Ve a https://huggingface.co/settings/tokens
2. Crea un nuevo token con permisos de lectura
3. Copia el token

**Configurar token:**
```bash
# Editar archivo .env
nano .env

# Cambiar esta línea:
HUGGINGFACE_TOKEN=tu_token_aqui
```

### 4. Descargar Modelos

```bash
# Activar entorno conda
conda activate radox

# Descargar modelos
python scripts/download_models.py
```

---

## Ejecución del Sistema

### Opción 1: Sin Docker (Desarrollo) - RECOMENDADO

**Método 1: Script automático**
```bash
# Ejecutar script de desarrollo
./run_dev.sh
```

**Método 2: Manual**
```bash
# Activar entorno conda
conda activate radox

# Ejecutar desde el directorio raíz (IMPORTANTE)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Acceso:**
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs

### Opción 2: Con Docker

```bash
# Construir y ejecutar con Docker
./run.sh
```

**Acceso:**
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs

---

## Uso de la API

### 1. Detectar Neumonía

**Endpoint:** `POST /api/v1/detect`

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@tu_imagen.jpg"
```

**Respuesta:**
```json
{
  "prediction": "Neumonía",
  "confidence": 0.95,
  "recommendation": "Se recomienda consulta médica inmediata",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. Generar Informe Médico

**Endpoint:** `POST /api/v1/report`

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/report" \
     -H "Content-Type: application/json" \
     -d '{
       "prediction": "Neumonía",
       "confidence": 0.95,
       "image_path": "ruta/a/imagen.jpg"
     }'
```

**Respuesta:**
```json
{
  "report": "Informe médico generado por MedGemma...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Estructura de Directorios Final

```
RADOX/
├── backend/                 # Backend FastAPI
│   ├── api/routes/         # Endpoints de la API
│   │   ├── pneumonia.py    # Detección de neumonía
│   │   └── reports.py      # Generación de informes
│   ├── models/             # Modelos de IA
│   │   └── cnn_model.py    # Modelo CNN
│   ├── services/           # Servicios de negocio
│   │   ├── pneumonia_detection.py
│   │   └── report_generation.py
│   ├── config/             # Configuración
│   │   └── settings.py
│   ├── utils/              # Utilidades
│   └── main.py             # Aplicación principal
├── data/                   # Datos del sistema
│   ├── models/             # Modelos pre-entrenados
│   └── uploads/            # Imágenes subidas
├── scripts/                # Scripts de utilidad
│   └── download_models.py  # Descarga de modelos
├── requirements.txt        # Dependencias Python
├── env.example             # Variables de entorno ejemplo
├── .env                    # Variables de entorno (crear)
├── docker-compose.yml      # Configuración Docker
├── setup_conda.sh          # Instalación con Conda
├── run_dev.sh              # Ejecución en desarrollo
└── run.sh                  # Ejecución con Docker
```

---

## Comandos Útiles

### Gestión del Entorno Conda
```bash
# Activar entorno
conda activate radox

# Desactivar entorno
conda deactivate

# Ver entornos
conda env list

# Eliminar entorno
conda env remove -n radox
```

### Gestión de Docker
```bash
# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart
```

### Desarrollo
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
pytest

# Formatear código
black backend/
```

---

## Solución de Problemas

### Error: "No module named 'backend'"
- **Solución:** Ejecuta uvicorn desde el directorio raíz del proyecto
- **Comando correcto:** `uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- **O usa el script:** `./run_dev.sh`

### Error: Token de Hugging Face no válido
- Verifica que el token esté correctamente configurado en `.env`
- Asegúrate de que el token tenga permisos de lectura

### Error: Modelo CNN no encontrado
- Ejecuta `python scripts/download_models.py` para descargar modelos
- Verifica que la carpeta `data/models/` exista

### Error: Puerto 8000 ocupado
- Cambia el puerto en `backend/config/settings.py`
- O mata el proceso: `sudo fuser -k 8000/tcp`

### Error: Dependencias no encontradas
- Activa el entorno conda: `conda activate radox`
- Reinstala dependencias: `pip install -r requirements.txt`

---

## Notas Importantes

- **Solo para fines educativos:** No usar para diagnóstico médico real
- **No almacena datos:** Las imágenes no se guardan permanentemente
- **Token requerido:** Necesitas un token de Hugging Face para generar informes
- **Python 3.11:** El proyecto requiere Python 3.11 o superior
- **Ejecutar desde raíz:** Siempre ejecuta uvicorn desde el directorio raíz del proyecto 