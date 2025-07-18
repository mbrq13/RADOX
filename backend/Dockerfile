FROM python:3.11-slim

# Metadata
LABEL maintainer="RADOX Team"
LABEL description="RADOX - Sistema de Detección de Neumonía con IA"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgdcm-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios
RUN mkdir -p /app/data/{models,vector_db,uploads} && \
    mkdir -p /app/logs

# Copiar código del backend
COPY backend/ ./backend/

# Copiar archivos de configuración
COPY env.example .env

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 radox && \
    chown -R radox:radox /app

# Cambiar a usuario no-root
USER radox

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 