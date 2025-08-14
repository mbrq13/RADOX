# 🚀 **Guía de Distribución de RADOX**

## 📋 **Resumen**
RADOX es un sistema completo de detección de neumonía usando inteligencia artificial que combina:
- **Backend FastAPI** con modelo CNN TorchXRayVision
- **Frontend Next.js** con interfaz moderna y responsive
- **Modelo MedGemma** para generación de informes médicos
- **API REST completa** con documentación automática

## 🎯 **Opciones de Distribución**

### **1. Ejecutable Standalone (Recomendado) 🏆**
- ✅ **Sin instalación** - Ejecuta directamente
- ✅ **Portable** - Funciona en cualquier máquina compatible
- ✅ **Profesional** - Ideal para hospitales y clínicas
- ✅ **Fácil distribución** - Un solo archivo ejecutable

### **2. Instalación Automática 🔧**
- ✅ **Scripts automáticos** para Linux y Windows
- ✅ **Verificación de dependencias** automática
- ✅ **Entorno conda** configurado automáticamente
- ✅ **Frontend construido** para producción

### **3. Instalación Manual 📚**
- ✅ **Control total** sobre el proceso
- ✅ **Personalización** de dependencias
- ✅ **Debugging** más fácil
- ✅ **Para desarrolladores** avanzados

---

## 🚀 **Construir Ejecutable Standalone**

### **Opción A: Solo Backend (Recomendado)**
```bash
# En tu entorno conda radox
conda activate radox

# Construir solo backend (más rápido, más estable)
./build_executable.sh -b

# Con instalación automática de dependencias
./build_executable.sh -i -b

# Limpiar build anterior y construir
./build_executable.sh -c -b
```

### **Opción B: Backend + Frontend Completo**
```bash
# Construir RADOX completo
./build_executable.sh -f

# Con instalación automática
./build_executable.sh -i -f
```

### **Resultado:**
```
dist/
├── RADOX_Backend/           # Solo backend
│   ├── RADOX_Backend        # Ejecutable principal
│   ├── RADOX_Backend.sh     # Launcher Linux/Mac
│   ├── RADOX_Backend.bat    # Launcher Windows
│   ├── README.md            # Documentación
│   ├── models/              # Modelos de IA
│   └── scripts/             # Scripts de utilidad
└── RADOX/                   # Versión completa
    ├── RADOX               # Ejecutable principal
    ├── RADOX.sh            # Launcher
    ├── frontend/           # Frontend Next.js
    └── backend/            # Backend FastAPI
```

---

## 📦 **Distribuir el Ejecutable**

### **Para Usuarios Finales:**
1. **Descargar** el archivo ejecutable
2. **Ejecutar** directamente (no requiere instalación)
3. **Configurar** archivo `.env` con tokens
4. **Usar** en http://localhost:8000

### **Archivos a Incluir:**
- ✅ Ejecutable principal (`RADOX_Backend` o `RADOX`)
- ✅ Script launcher (`.sh` para Linux/Mac, `.bat` para Windows)
- ✅ Archivo de configuración `.env.example`
- ✅ README con instrucciones
- ✅ Carpeta `models/` con modelos de IA
- ✅ Carpeta `scripts/` con utilidades

---

## 🔧 **Instalación Automática**

### **Linux/Mac:**
```bash
# Hacer ejecutable
chmod +x install_radox.sh

# Ejecutar instalador
./install_radox.sh
```

### **Windows:**
```cmd
# Ejecutar instalador
install_radox.bat
```

### **Qué hace el instalador:**
1. ✅ Verifica sistema y dependencias
2. ✅ Crea entorno conda `radox`
3. ✅ Instala PyTorch + TorchXRayVision
4. ✅ Instala dependencias Python
5. ✅ Configura frontend Next.js
6. ✅ Crea archivo `.env` de ejemplo
7. ✅ Verifica instalación completa

---

## 🌐 **Uso del Sistema**

### **Después de la Instalación:**
```bash
# Activar entorno
conda activate radox

# Ejecutar RADOX completo
./run_dev_all.sh

# Solo backend
./run_dev.sh
```

### **Acceso:**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔑 **Configuración Requerida**

### **Archivo `.env`:**
```env
# Tokens de Hugging Face
HUGGINGFACE_TOKEN=tu_token_aqui
MEDGEMMA_ENDPOINT=https://tu-endpoint.huggingface.cloud

# Configuración de seguridad
SECRET_KEY=clave_secreta_para_produccion

# Configuración de red
API_HOST=127.0.0.1
API_PORT=8000

# Modo de operación
DEBUG=false
```

### **Obtener Tokens:**
1. **Hugging Face**: https://huggingface.co/settings/tokens
2. **MedGemma Endpoint**: https://huggingface.co/inference-endpoints
3. **Secret Key**: Generar clave aleatoria segura

---

## 📊 **Requisitos del Sistema**

### **Mínimos:**
- **RAM**: 4GB
- **Almacenamiento**: 10GB
- **CPU**: 2 cores
- **Sistema**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

### **Recomendados:**
- **RAM**: 8GB+
- **Almacenamiento**: 20GB+
- **CPU**: 4+ cores
- **GPU**: NVIDIA con CUDA (opcional)

### **Dependencias del Sistema:**
- **Python**: 3.11+
- **Conda/Miniconda**: Última versión
- **Node.js**: 18+ (para frontend)
- **npm**: 8+ (para frontend)

---

## 🚨 **Solución de Problemas**

### **Error: "Module not found"**
```bash
# Verificar entorno conda
conda activate radox

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import torch, torchxrayvision, fastapi"
```

### **Error: "Port already in use"**
```bash
# Cambiar puerto en .env
API_PORT=8001

# O matar proceso
lsof -ti:8000 | xargs kill -9
```

### **Error: "CUDA not available"**
```bash
# Instalar versión CPU de PyTorch
conda install pytorch torchvision torchaudio cpuonly -c pytorch
```

### **Error: "Frontend build failed"**
```bash
# Limpiar node_modules
cd Front_guide/ai-pneumonia-assistant
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📈 **Optimización para Producción**

### **Configuración de Producción:**
```env
DEBUG=false
API_HOST=0.0.0.0  # Acceso externo
API_PORT=80        # Puerto estándar
LOG_LEVEL=WARNING  # Logs mínimos
```

### **Servidor de Producción:**
```bash
# Usar Gunicorn en lugar de uvicorn
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Proxy Reverso (Nginx):**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🌍 **Distribución Internacional**

### **Idiomas Soportados:**
- ✅ **Español** (predeterminado)
- ✅ **Inglés** (configurable)
- ✅ **Otros idiomas** (extensible)

### **Formatos de Fecha:**
- ✅ **DD/MM/YYYY** (español)
- ✅ **MM/DD/YYYY** (inglés)
- ✅ **ISO 8601** (estándar)

### **Monedas:**
- ✅ **Pesos** (MXN, ARS, CLP)
- ✅ **Dólares** (USD, CAD)
- ✅ **Euros** (EUR)
- ✅ **Otras** (configurables)

---

## 📋 **Checklist de Distribución**

### **Antes de Distribuir:**
- [ ] ✅ Código probado y funcionando
- [ ] ✅ Ejecutable construido exitosamente
- [ ] ✅ Dependencias incluidas
- [ ] ✅ Modelos de IA incluidos
- [ ] ✅ Documentación actualizada
- [ ] ✅ Archivos de configuración de ejemplo
- [ ] ✅ Scripts de instalación probados
- [ ] ✅ README con instrucciones claras

### **Para Usuarios Finales:**
- [ ] ✅ Instrucciones de instalación
- [ ] ✅ Guía de configuración
- [ ] ✅ Ejemplos de uso
- [ ] ✅ Solución de problemas comunes
- [ ] ✅ Contacto para soporte
- [ ] ✅ Licencia y términos de uso

---

## 🎯 **Casos de Uso Típicos**

### **Hospitales y Clínicas:**
- **Instalación**: Ejecutable standalone
- **Configuración**: Red interna, puertos seguros
- **Uso**: Análisis de radiografías en tiempo real
- **Integración**: PACS, HIS, RIS

### **Investigación Médica:**
- **Instalación**: Entorno conda completo
- **Configuración**: GPU, múltiples modelos
- **Uso**: Entrenamiento, validación, investigación
- **Integración**: Jupyter, TensorBoard

### **Educación Médica:**
- **Instalación**: Scripts automáticos
- **Configuración**: Modo demo, ejemplos
- **Uso**: Cursos, talleres, práctica
- **Integración**: LMS, plataformas educativas

---

## 🚀 **Próximos Pasos**

### **Versión 1.1:**
- [ ] **Docker** containers
- [ ] **Kubernetes** deployment
- [ ] **Cloud** integration (AWS, GCP, Azure)
- [ ] **Mobile** app (React Native)

### **Versión 1.2:**
- [ ] **Multi-modelo** support
- [ ] **Batch processing**
- [ ] **API rate limiting**
- [ ] **Authentication** system

### **Versión 2.0:**
- [ ] **Real-time** analysis
- [ ] **3D imaging** support
- [ ] **AI training** interface
- [ ] **Collaborative** features

---

## 📞 **Soporte y Contacto**

### **Documentación:**
- **README.md**: Guía principal
- **GUIA_INSTALACION.md**: Instalación detallada
- **GUIA_DISTRIBUCION.md**: Esta guía
- **API Docs**: http://localhost:8000/docs

### **Soporte Técnico:**
- **GitHub Issues**: Para bugs y feature requests
- **Email**: soporte@radox.com
- **Discord**: Comunidad de desarrolladores
- **Documentación**: Wiki del proyecto

---

## 🎉 **¡Listo para Distribuir!**

Con esta configuración, RADOX está listo para ser distribuido a:
- 🏥 **Hospitales** y clínicas
- 🔬 **Institutos** de investigación
- 🎓 **Universidades** médicas
- 💼 **Empresas** de tecnología médica
- 🌍 **Organizaciones** internacionales

**RADOX** - Transformando la medicina con inteligencia artificial 🚀🏥✨

---

*Última actualización: $(date)*
*Versión: 1.0.0*
*Licencia: MIT*
