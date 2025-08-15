# RADOX - Sistema de Detección de Neumonía con IA

## 🏥 Descripción

RADOX es un sistema completo para la detección automática de neumonía en radiografías de tórax utilizando inteligencia artificial. El sistema está diseñado para ser desplegado localmente y proporciona una API REST para subir imágenes, analizar resultados y generar informes médicos automáticos.

**Versión actual:** Utiliza el modelo **TorchXRayVision DenseNet121 RSNA** para la detección de neumonía y la API de Hugging Face (MedGemma) para la generación de informes médicos.

---

## 🚀 Inicio Rápido

### Comando Principal de Ejecución

**Para ejecutar todo el sistema (backend + frontend moderno):**
```bash
./run_dev_all.sh
```

Este comando:
- ✅ Levanta el backend FastAPI en el puerto 8000
- ✅ Levanta el frontend Next.js moderno en el puerto 3000
- ✅ Configura automáticamente el entorno conda
- ✅ Ejecuta ambos servicios en paralelo

---

## 📖 Cómo Usar RADOX

### 1. **Instalación Inicial**

```bash
# Clonar el repositorio
git clone https://github.com/mbrq13/RADOX.git
cd RADOX

# Configuración rápida con TorchXRayVision
./quick_start_torchxrayvision.sh
```

### 2. **Configurar Token de Hugging Face**

```bash
# Editar archivo de configuración
nano .env

# Cambiar esta línea:
HUGGINGFACE_TOKEN=tu_token_aqui

# También configurar el frontend moderno
nano Front_guide/ai-pneumonia-assistant/config.js
# Actualizar HUGGINGFACE_TOKEN
```

### 3. **Ejecutar el Sistema**

```bash
# Opción A: Ejecutar todo (recomendado)
./run_dev_all.sh

# Opción B: Solo backend en desarrollo
./run_dev.sh

# Opción C: Con Docker
./run.sh
```

### 4. **Acceder a la Aplicación**

- **Frontend Moderno:** http://localhost:3000
- **Frontend Clásico:** http://localhost:8000
- **API Backend:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs

### 5. **Usar la Detección de Neumonía**

1. **Subir Imagen:**
   - Ve a http://localhost:3000
   - Arrastra y suelta una radiografía de tórax (JPG, PNG, DICOM)
   - O haz clic para seleccionar archivo

2. **Análisis Automático:**
   - El sistema procesará la imagen con el modelo CNN
   - Mostrará predicción: Normal o Neumonía
   - Nivel de confianza y recomendación clínica

3. **Generar Informe Médico:**
   - Haz clic en "Generar Informe"
   - El sistema usará MedGemma para crear un informe profesional
   - Descarga o copia el informe generado

### 6. **Usar la API Directamente**

```bash
# Detectar neumonía
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@tu_radiografia.jpg"

# Generar informe
curl -X POST "http://localhost:8000/api/v1/report" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"case_id": "tu_case_id", "report_type": "completo"}'
```

### 7. **Verificar Estado del Sistema**

```bash
# Estado de servicios
./run.sh --status

# Ver logs en tiempo real
./run.sh --logs

# Health check de la API
curl http://localhost:8000/health
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Análisis Rápido de Radiografía

```bash
# 1. Iniciar sistema
./run_dev_all.sh

# 2. Abrir navegador en http://localhost:3000
# 3. Subir imagen de radiografía
# 4. Ver resultado en tiempo real
```

### Ejemplo 2: Uso de la API para Automatización

```bash
# Script de análisis automático
#!/bin/bash
for image in radiografias/*.jpg; do
  echo "Analizando: $image"
  response=$(curl -s -X POST "http://localhost:8000/api/v1/detect" \
    -F "file=@$image")
  echo "Resultado: $response"
done
```

### Ejemplo 3: Generación de Informes en Lote

```bash
# Generar informes para múltiples casos
python3 -c "
import requests
import json

cases = ['case_001', 'case_002', 'case_003']
for case_id in cases:
    response = requests.post('http://localhost:8000/api/v1/report', 
                           json={'case_id': case_id, 'report_type': 'completo'})
    print(f'Informe {case_id}: {response.json()}')
"
```

### Ejemplo 4: Monitoreo del Sistema

```bash
# Script de monitoreo continuo
while true; do
  status=$(curl -s http://localhost:8000/health)
  echo "$(date): $status"
  sleep 30
done
```

---

## 🔄 Flujo de Trabajo Paso a Paso

### Paso 1: Preparación del Sistema
```bash
# 1. Clonar repositorio
git clone https://github.com/mbrq13/RADOX.git
cd RADOX

# 2. Configurar entorno
./quick_start_torchxrayvision.sh

# 3. Configurar token de Hugging Face
nano .env  # Agregar HUGGINGFACE_TOKEN=tu_token
nano Front_guide/ai-pneumonia-assistant/config.js  # Actualizar token
```

### Paso 2: Ejecutar el Sistema
```bash
# Ejecutar todo el sistema
./run_dev_all.sh

# Esperar a que ambos servicios estén listos:
# ✅ Backend: http://localhost:8000/health
# ✅ Frontend: http://localhost:3000
```

### Paso 3: Usar la Interfaz Web
1. **Abrir navegador:** http://localhost:3000
2. **Subir imagen:** Arrastra radiografía o haz clic para seleccionar
3. **Ver análisis:** El sistema procesa con IA y muestra resultados
4. **Generar informe:** Haz clic en "Generar Informe Médico"
5. **Descargar resultado:** Guarda el informe en tu computadora

### Paso 4: Usar la API (Opcional)
```bash
# Detectar neumonía
curl -X POST "http://localhost:8000/api/v1/detect" \
  -F "file=@mi_radiografia.jpg"

# Ver documentación completa
# Abrir: http://localhost:8000/docs
```

### Paso 5: Monitoreo y Mantenimiento
```bash
# Ver estado del sistema
./run.sh --status

# Ver logs en tiempo real
./run.sh --logs

# Detener sistema
./run.sh --stop
```

---

## 📋 Comandos de Uso Diario

### 🚀 **Comandos Principales (Usar a diario)**

```bash
# 1. INICIAR TODO EL SISTEMA (más usado)
./run_dev_all.sh

# 2. SOLO BACKEND (para desarrollo)
./run_dev.sh

# 3. CON DOCKER (para producción)
./run.sh
```

### 🔧 **Comandos de Mantenimiento**

```bash
# Ver estado de servicios
./run.sh --status

# Ver logs en tiempo real
./run.sh --logs

# Reiniciar sistema
./run.sh --restart

# Detener sistema
./run.sh --stop
```

### 📊 **Comandos de Monitoreo**

```bash
# Health check de la API
curl http://localhost:8000/health

# Estado de Docker
docker-compose ps

# Logs del backend
docker-compose logs radox-api

# Logs del frontend
cd Front_guide/ai-pneumonia-assistant && npm run dev
```

### 🧪 **Comandos de Testing**

```bash
# Probar modelo CNN
python scripts/test_torchxrayvision_model.py

# Ejecutar tests completos
pytest

# Demo interactivo
python demo.py
```

### 📁 **Comandos de Archivos**

```bash
# Ver estructura del proyecto
tree -L 3

# Ver logs del sistema
tail -f logs/radox.log

# Limpiar archivos temporales
rm -rf data/uploads/*
```

---

## ✨ Características Principales

- **Detección de neumonía:** Utiliza el modelo **TorchXRayVision DenseNet121 RSNA** específicamente entrenado para el RSNA Pneumonia Challenge
- **Generación de informes médicos:** Integra la API de Hugging Face (MedGemma) para crear informes médicos automáticos
- **API REST completa:** Endpoints para subir imágenes (JPG, PNG, DICOM), obtener predicciones y generar informes
- **Frontend moderno:** Interfaz Next.js con Tailwind CSS y componentes Radix UI
- **Frontend clásico:** Interfaz HTML/CSS/JS tradicional
- **Despliegue flexible:** Con Docker, sin Docker, o modo desarrollo
- **Sin dependencias complejas:** No requiere bases de datos vectoriales ni servicios adicionales

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **Backend FastAPI** (`backend/`)
   - API REST con FastAPI
   - Modelo CNN TorchXRayVision
   - Servicios de detección y generación de informes
   - Procesamiento de imágenes médicas

2. **Frontend Moderno** (`Front_guide/ai-pneumonia-assistant/`)
   - Aplicación Next.js 14
   - Tailwind CSS + Radix UI
   - Interfaz moderna y responsive
   - Componentes reutilizables

3. **Frontend Clásico** (`frontend/`)
   - HTML/CSS/JavaScript tradicional
   - Bootstrap para estilos
   - Interfaz simple y funcional

4. **Modelos de IA** (`models/`, `backend/models/`)
   - TorchXRayVision DenseNet121 RSNA
   - Modelos CNN pre-entrenados
   - Scripts de descarga automática

---

## 📋 Flujo de Trabajo del Sistema

1. **Subida de imagen:**
   - El usuario envía una radiografía de tórax (JPG, PNG o DICOM) a través de la API

2. **Predicción con CNN:**
   - El backend procesa la imagen y utiliza el modelo CNN para predecir si la imagen muestra neumonía o es normal
   - Se calcula el nivel de confianza y se genera una recomendación clínica automática

3. **Generación de informe médico:**
   - El usuario puede solicitar la generación de un informe médico
   - El sistema envía los resultados de la CNN a la API de Hugging Face (MedGemma), que devuelve un informe médico profesional en texto

4. **Respuesta de la API:**
   - La API devuelve el diagnóstico, la confianza, la recomendación y el informe médico generado

---

## 🛠️ Instalación y Despliegue

### Opción 1: Inicio Rápido con TorchXRayVision (Recomendado)

1. **Ejecutar script de inicio rápido:**
   ```bash
   ./quick_start_torchxrayvision.sh
   ```
   
   Este script automáticamente:
   - Crea y activa el entorno conda 'radox'
   - Instala TorchXRayVision y dependencias
   - Ejecuta pruebas del modelo

### Opción 2: Instalación Manual con Conda

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
   - Copia `env.example` a `.env` y añade tu token de Hugging Face

4. **Ejecución:**
   ```bash
   ./run.sh
   ```

5. **Acceso:**
   - API: http://localhost:8000
   - Documentación API: http://localhost:8000/docs

### Opción 3: Modo Desarrollo (Sin Docker)

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

### Opción 4: Ejecución Completa (Backend + Frontend)

**Para ejecutar todo el sistema:**
```bash
./run_dev_all.sh
```

**Para ejecutar solo el backend en desarrollo:**
```bash
./run_dev.sh
```

**Para ejecutar con Docker:**
```bash
./run.sh
```

---

## 🔑 Configuración de Credenciales

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

3. **Frontend moderno:**
   - Edita `Front_guide/ai-pneumonia-assistant/config.js`
   - Actualiza `HUGGINGFACE_TOKEN` con tu token real

---

## 📁 Estructura del Proyecto

```
RADOX/
├── backend/                 # Backend FastAPI
│   ├── api/routes/         # Endpoints de la API
│   │   ├── pneumonia.py    # Detección de neumonía
│   │   ├── reports.py      # Generación de informes
│   │   ├── patients.py     # Gestión de pacientes
│   │   └── studies.py      # Gestión de estudios
│   ├── models/             # Modelos de IA
│   │   └── cnn_model.py    # Modelo CNN principal
│   ├── services/           # Servicios de negocio
│   │   ├── pneumonia_detection.py
│   │   └── report_generation.py
│   ├── config/             # Configuración
│   │   └── settings.py
│   └── utils/              # Utilidades
│       └── image_processing.py
├── Front_guide/            # Frontend moderno Next.js
│   └── ai-pneumonia-assistant/
│       ├── app/            # Páginas y API routes
│       ├── components/     # Componentes React
│       ├── lib/            # Utilidades y hooks
│       └── config.js       # Configuración del frontend
├── frontend/               # Frontend clásico HTML/CSS/JS
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── index.html
├── data/                   # Datos del sistema
│   ├── models/             # Modelos pre-entrenados
│   ├── uploads/            # Imágenes subidas
│   └── vector_db/          # Base de datos vectorial (opcional)
├── scripts/                # Scripts de utilidad
│   ├── download_models.py
│   ├── test_torchxrayvision_model.py
│   └── python_cnn_bridge.py
├── tests/                  # Tests unitarios
├── requirements.txt        # Dependencias Python
├── package.json           # Dependencias Node.js
├── docker-compose.yml     # Configuración Docker
├── setup.sh              # Script de instalación
├── run.sh                # Script de ejecución con Docker
├── run_dev.sh            # Script de desarrollo
├── run_dev_all.sh        # Script principal (backend + frontend)
└── quick_start_torchxrayvision.sh  # Inicio rápido
```

---

## 🌐 Endpoints de la API

### Detección de Neumonía
- `POST /api/v1/detect` - Detectar neumonía en imagen
  - Parámetros: `file` (imagen), `patient_info` (opcional, JSON)
  - Respuesta: Predicción, confianza, recomendación clínica

### Generación de Informes
- `POST /api/v1/report` - Generar informe médico
  - Parámetros: `case_id`, `report_type`
  - Respuesta: Informe médico generado por MedGemma

### Gestión de Pacientes
- `GET /api/v1/patients` - Listar pacientes
- `POST /api/v1/patients` - Crear paciente
- `GET /api/v1/patients/{patient_id}` - Obtener paciente

### Gestión de Estudios
- `GET /api/v1/studies` - Listar estudios
- `POST /api/v1/studies` - Crear estudio
- `GET /api/v1/studies/{study_id}` - Obtener estudio

### Utilidades
- `GET /health` - Verificar estado del sistema
- `GET /docs` - Documentación interactiva (Swagger UI)
- `GET /redoc` - Documentación alternativa (ReDoc)

---

## 🎯 Comandos de Ejecución

### Comando Principal
```bash
./run_dev_all.sh
```
**Ejecuta todo el sistema (backend + frontend moderno)**

### Otros Comandos Disponibles

**Desarrollo (sin Docker):**
```bash
./run_dev.sh          # Solo backend en desarrollo
```

**Producción (con Docker):**
```bash
./run.sh              # Sistema completo con Docker
./run.sh --monitor    # Con monitoreo de logs
./run.sh --stop       # Detener sistema
./run.sh --restart    # Reiniciar sistema
./run.sh --logs       # Ver logs
./run.sh --status     # Estado de servicios
```

**Instalación:**
```bash
./setup.sh            # Instalación completa
./setup.sh --continue # Continuar instalación
```

**Inicio rápido:**
```bash
./quick_start_torchxrayvision.sh  # Configuración rápida
```

---

## 🧠 Modelo TorchXRayVision

RADOX utiliza el modelo **TorchXRayVision DenseNet121 RSNA** específicamente entrenado para el **RSNA Pneumonia Challenge**. Este modelo está optimizado para la detección de neumonía en radiografías de tórax.

### Características del Modelo
- **Arquitectura:** DenseNet121
- **Resolución:** 224x224 píxeles
- **Dataset:** RSNA Pneumonia Challenge
- **Patologías:** 18 diferentes, incluyendo "Pneumonia"
- **Precisión:** Optimizada para detección de neumonía

### Documentación
Para más información sobre el modelo, consulta:
- [TORCHXRAYVISION_README.md](TORCHXRAYVISION_README.md) - Documentación completa
- [Documentación oficial](https://mlmed.org/torchxrayvision/models.html) - TorchXRayVision

---

## 🎨 Frontend Moderno (Next.js)

### Características
- **Framework:** Next.js 14 con App Router
- **Estilos:** Tailwind CSS + Radix UI
- **Componentes:** Sistema de componentes reutilizables
- **Responsive:** Diseño adaptativo para móviles y desktop
- **Tema:** Soporte para tema claro/oscuro

### Páginas Disponibles
- **Página principal:** Interfaz de subida y análisis
- **Pacientes:** Gestión de información de pacientes
- **Estudios:** Historial de estudios médicos
- **Informes:** Visualización de informes generados
- **Configuración:** Ajustes del sistema

### Ejecución del Frontend
```bash
cd Front_guide/ai-pneumonia-assistant
npm install              # Instalar dependencias
npm run dev              # Modo desarrollo
npm run build            # Construir para producción
npm start                # Modo producción
```

---

## 🐳 Docker y Contenedores

### Servicios Docker
- **radox-api:** Backend FastAPI
- **Puerto:** 8000 (configurable)
- **Volúmenes:** Datos persistentes y código fuente
- **Healthcheck:** Verificación automática de salud

### Comandos Docker
```bash
# Construir imágenes
docker-compose build

# Ejecutar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Estado de servicios
docker-compose ps
```

---

## 🧪 Testing y Desarrollo

### Ejecutar Tests
```bash
# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Todos los tests
pytest

# Con cobertura
pytest --cov=backend
```

### Scripts de Prueba
```bash
# Prueba del modelo
python scripts/test_torchxrayvision_model.py

# Prueba del sistema completo
python scripts/test_complete_system.py

# Demo interactivo
python demo.py
```

---

## 📊 Monitoreo y Logs

### Logs del Sistema
- **Ubicación:** `logs/radox.log`
- **Rotación:** Diaria
- **Retención:** 30 días
- **Nivel:** INFO, ERROR, SUCCESS

### Health Checks
- **Endpoint:** `/health`
- **Verificación:** Estado del modelo CNN y servicios
- **Intervalo:** 30 segundos (Docker)

---

## 🔧 Tecnologías Utilizadas

### Backend
- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework web moderno
- **PyTorch** - Deep Learning
- **TorchXRayVision** - Modelos médicos pre-entrenados
- **Uvicorn** - Servidor ASGI

### Frontend
- **Next.js 14** - Framework React moderno
- **Tailwind CSS** - Framework CSS utilitario
- **Radix UI** - Componentes accesibles
- **TypeScript** - Tipado estático

### IA y Machine Learning
- **TorchXRayVision DenseNet121 RSNA** - Detección de neumonía
- **MedGemma** - Generación de informes médicos (vía Hugging Face)
- **Transformers** - Procesamiento de lenguaje natural

### Infraestructura
- **Docker** - Contenedores
- **Docker Compose** - Orquestación de servicios
- **Conda** - Gestión de entornos Python

---

## 📝 Notas Importantes

- **Este sistema es solo para fines educativos y de investigación.** No debe usarse para diagnóstico médico real.
- **No se almacena información médica ni imágenes en bases de datos permanentes.**
- **El flujo es directo:** imagen → predicción CNN → informe MedGemma → respuesta API.
- **El comando principal es `./run_dev_all.sh`** para ejecutar todo el sistema.

---

## 🚨 Solución de Problemas

### Problemas Comunes

**Error de entorno conda:**
```bash
conda activate radox
# Si no existe:
conda create -n radox python=3.11
```

**Token de Hugging Face no configurado:**
```bash
# Editar .env
nano .env
# Cambiar: HUGGINGFACE_TOKEN=tu_token_aqui
```

**Puerto ocupado:**
```bash
# Verificar puertos en uso
sudo lsof -i :8000
sudo lsof -i :3000

# Matar proceso
sudo fuser -k 8000/tcp
```

**Modelos no descargados:**
```bash
python scripts/download_models.py
```

---

## 📚 Documentación Adicional

- [GUIA_INSTALACION.md](GUIA_INSTALACION.md) - Guía detallada de instalación
- [GUIA_DISTRIBUCION.md](GUIA_DISTRIBUCION.md) - Guía de distribución
- [TORCHXRAYVISION_README.md](TORCHXRAYVISION_README.md) - Documentación del modelo
- [INSTALL_SUMMARY.txt](INSTALL_SUMMARY.txt) - Resumen de instalación

---

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Ejecuta los tests
5. Envía un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto

Para dudas o soporte, contacta al equipo de desarrollo de RADOX.

---

## 🎉 ¡RADOX está listo para detectar neumonía con IA!

**Recuerda: El comando principal es `./run_dev_all.sh` para ejecutar todo el sistema.** 
