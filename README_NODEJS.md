# RADOX Node.js - Sistema de Detección de Neumonía con IA

## 🏥 Descripción

RADOX Node.js es una implementación completa en Node.js del sistema de detección automática de neumonía en radiografías de tórax utilizando inteligencia artificial. El sistema combina un modelo CNN (Convolutional Neural Network) para la detección con la API de Hugging Face para la generación de informes médicos automáticos.

**Versión:** 1.0.0  
**Framework:** Node.js + Express  
**IA:** TensorFlow.js + Hugging Face API (MedGemma)  

---

## ✨ Características Principales

- **🧠 Detección de Neumonía:** Utiliza TensorFlow.js para ejecutar modelos CNN
- **📋 Generación de Informes:** Integración con Hugging Face API (MedGemma) para informes médicos
- **🖼️ Procesamiento de Imágenes:** Soporte para JPG, PNG y DICOM
- **🌐 Interfaz Web Intuitiva:** Frontend moderno con drag-and-drop
- **⚡ Despliegue Local:** Sin dependencias de Docker
- **🔄 Flujo Condicional:** Solo genera informes cuando detecta neumonía

---

## 🚀 Flujo de Trabajo

1. **Carga de Imagen:** Usuario sube radiografía de tórax (JPG/PNG/DICOM)
2. **Análisis CNN:** El modelo detecta presencia de neumonía con nivel de confianza
3. **Decisión Condicional:** 
   - ✅ **Si es Neumonía:** Habilita la generación de informe médico
   - ❌ **Si es Normal:** Solo muestra el diagnóstico, sin opción de informe
4. **Informe Médico:** Genera informe profesional usando Hugging Face API
5. **Visualización:** Muestra resultados y recomendaciones médicas

---

## 📋 Prerrequisitos

- **Node.js:** v16.0.0 o superior
- **npm:** v8.0.0 o superior  
- **Sistema Operativo:** Linux, macOS, Windows
- **Memoria:** Mínimo 2GB RAM
- **Token Hugging Face:** Para generación de informes (opcional)

---

## 🛠️ Instalación Rápida

### 1. Instalar y Configurar

```bash
# Hacer ejecutables los scripts
chmod +x setup_nodejs.sh run_nodejs.sh

# Ejecutar instalación
./setup_nodejs.sh
```

### 2. Configurar Token de Hugging Face

```bash
# Editar archivo de configuración
nano config.env

# Cambiar esta línea:
HUGGINGFACE_TOKEN=your_hf_token_here
# Por tu token real:
HUGGINGFACE_TOKEN=hf_tu_token_aqui
```

### 3. Completar Instalación

```bash
# Continuar después de configurar el token
./setup_nodejs.sh --continue
```

### 4. Iniciar Sistema

```bash
# Iniciar servidor
./run_nodejs.sh

# O en modo desarrollo
./run_nodejs.sh --dev
```

### 5. Acceder al Sistema

- **Interfaz Web:** http://localhost:3000
- **Health Check:** http://localhost:3000/health

---

## 🎯 Uso del Sistema

### Interfaz Web

1. **Abrir** http://localhost:3000 en tu navegador
2. **Cargar** radiografía arrastrando o clickeando en el área de carga
3. **Analizar** presionando el botón "Analizar Radiografía"
4. **Revisar** los resultados del diagnóstico
5. **Generar Informe** (solo si detecta neumonía)

### API REST

#### Analizar Radiografía
```bash
curl -X POST \
  http://localhost:3000/api/analyze \
  -F "radiografia=@mi_radiografia.jpg"
```

#### Generar Informe
```bash
curl -X POST \
  http://localhost:3000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "diagnostico": "Neumonía",
    "confianza": 0.87
  }'
```

---

## 📁 Estructura del Proyecto

```
RADOX/
├── server.js                 # Servidor principal Express
├── package.json             # Dependencias Node.js
├── config.env              # Variables de entorno
├── setup_nodejs.sh         # Script de instalación
├── run_nodejs.sh           # Script de ejecución
├── src/
│   ├── services/
│   │   ├── pneumoniaDetector.js    # Detector CNN
│   │   └── reportGenerator.js      # Generador de informes
│   └── utils/
│       └── imageProcessor.js       # Procesador de imágenes
├── public/
│   ├── index.html          # Interfaz web principal
│   └── js/
│       └── app.js          # JavaScript del frontend
├── uploads/                # Archivos temporales
├── models/                 # Modelos de IA
└── logs/                  # Archivos de log
```

---

## ⚙️ Configuración

### Variables de Entorno (config.env)

```bash
# Servidor
PORT=3000
NODE_ENV=development

# Hugging Face
HUGGINGFACE_TOKEN=your_hf_token_here
MEDGEMMA_MODEL=google/medgemma-7b

# Archivos
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
MODELS_DIR=./models

# IA
CONFIDENCE_THRESHOLD=0.8
IMAGE_SIZE=224
```

---

## 🔧 Comandos Disponibles

### Scripts de Sistema
```bash
./setup_nodejs.sh           # Instalación inicial
./setup_nodejs.sh --continue # Continuar después de configurar token
./run_nodejs.sh             # Iniciar en producción
./run_nodejs.sh --dev       # Iniciar en desarrollo
./run_nodejs.sh --status    # Ver estado del sistema
./run_nodejs.sh --stop      # Detener servidor
./run_nodejs.sh --restart   # Reiniciar servidor
./run_nodejs.sh --help      # Ver ayuda
```

### Comandos npm
```bash
npm start                   # Iniciar servidor
npm run dev                 # Modo desarrollo con nodemon
npm test                    # Ejecutar pruebas
npm install                 # Instalar dependencias
```

---

## 🧪 Modelo de IA

### Configuración Actual
- **Arquitectura:** ResNet50 (simulado para demo)
- **Entrada:** Imágenes 224x224 píxeles
- **Salida:** Binaria (Normal/Neumonía)
- **Framework:** TensorFlow.js

### Usar Modelo Real
Para usar un modelo real entrenado:

1. **Convertir modelo de Python:**
```bash
# Desde Python/TensorFlow
tensorflowjs_converter \
  --input_format=tf_saved_model \
  --output_format=tfjs_graph_model \
  ./python_model \
  ./models/js_model
```

2. **Actualizar código:**
Modificar `src/services/pneumoniaDetector.js` para cargar el modelo real.

---

## 🔍 Resolución de Problemas

### Puerto en Uso
```bash
# Ver qué proceso usa el puerto
lsof -i :3000

# Matar proceso
./run_nodejs.sh --stop
```

### Dependencias Faltantes
```bash
# Reinstalar dependencias
rm -rf node_modules
npm install
```

### Error de Token Hugging Face
```bash
# Verificar token en config.env
grep HUGGINGFACE_TOKEN config.env

# El sistema funciona sin token (con informes básicos)
```

### Errores de Memoria
```bash
# Aumentar memoria Node.js
node --max-old-space-size=4096 server.js
```

---

## 🛡️ Seguridad y Limitaciones

### Seguridad Implementada
- ✅ Validación de tipos de archivo
- ✅ Límites de tamaño de archivo
- ✅ Rate limiting en API
- ✅ Headers de seguridad (Helmet)
- ✅ Limpieza automática de archivos temporales

### Limitaciones Importantes
- ⚠️ **Solo para fines educativos/investigación**
- ⚠️ **NO usar para diagnósticos médicos reales**
- ⚠️ **Requiere validación médica profesional**
- ⚠️ **Modelo mock en demostración**

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real
```bash
./run_nodejs.sh --logs
```

### Health Check
```bash
curl http://localhost:3000/health
```

### Métricas del Sistema
- Monitor de CPU y memoria incluido
- Logs automáticos en directorio `logs/`
- Estado de servicios disponible en `/health`

---

## 🔄 Desarrollo y Contribución

### Modo Desarrollo
```bash
# Iniciar con recarga automática
./run_nodejs.sh --dev

# O directamente con nodemon
npm run dev
```

### Estructura de Desarrollo
- **Backend:** Express.js con arquitectura modular
- **Frontend:** Vanilla JavaScript con Bootstrap 5
- **Servicios:** Separación clara de responsabilidades
- **Utilidades:** Funciones auxiliares reutilizables

---

## 📝 API Documentation

### Endpoints Disponibles

#### GET /health
Verificar estado del sistema
```json
{
  "status": "OK",
  "message": "RADOX API funcionando correctamente",
  "timestamp": "2024-01-20T10:30:00.000Z",
  "version": "1.0.0"
}
```

#### POST /api/analyze
Analizar radiografía
- **Input:** FormData con archivo 'radiografia'
- **Output:** Diagnóstico y confianza

#### POST /api/generate-report
Generar informe médico
- **Input:** JSON con diagnóstico y confianza
- **Output:** Informe médico estructurado

---

## 🆘 Soporte

### Obtener Ayuda
```bash
./run_nodejs.sh --help
./setup_nodejs.sh --help
```

### Información del Sistema
```bash
./run_nodejs.sh --info
```

### Logs de Error
```bash
tail -f logs/radox.log
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

---

## ⚠️ Disclaimer Médico

**IMPORTANTE:** Este sistema es únicamente para fines educativos y de investigación. NO debe utilizarse para diagnósticos médicos reales. Siempre consulte con un profesional médico cualificado para cualquier decisión relacionada con la salud.

---

## 🎉 ¡Listo!

Tu sistema RADOX Node.js está configurado y listo para detectar neumonía con IA. 

**¡Disfruta explorando el poder de la inteligencia artificial en medicina!** 🏥🤖 