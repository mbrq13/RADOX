#!/bin/bash

# Script para levantar backend y frontend moderno en paralelo

# Asume que ya estás en la raíz del proyecto y conda activado

# Exportar PYTHONPATH para imports absolutos
export PYTHONPATH=$(pwd)

# Levantar backend desde la raíz
(uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000) &
BACK_PID=$!

# Levantar frontend moderno
cd Front_guide/ai-pneumonia-assistant
npm run dev

# Al cerrar el frontend, matar el backend
kill $BACK_PID 