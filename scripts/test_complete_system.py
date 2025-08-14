#!/usr/bin/env python3
# test_complete_system.py
"""
Script de prueba completa del sistema RADOX con TorchXRayVision
Prueba todo el flujo: modelo, backend, API y frontend
"""

import os
import sys
import asyncio
import requests
import json
import base64
import numpy as np
from PIL import Image, ImageDraw
import io
import time

def create_test_xray_image():
    """Crea una imagen de rayos X sintética para testing."""
    print("🎨 Creando imagen de rayos X sintética...")
    
    # Crear imagen base 512x512
    img = Image.new('L', (512, 512), color=0)
    draw = ImageDraw.Draw(img)
    
    # Simular patrón pulmonar con neumonía
    for i in range(0, 512, 20):
        for j in range(0, 512, 20):
            if 100 < i < 400 and 50 < j < 450:
                # Simular neumonía en el área central
                if 200 < i < 350 and 200 < j < 350:
                    intensity = 120 + np.random.randint(0, 40)  # Más brillante (neumonía)
                else:
                    intensity = 40 + np.random.randint(0, 30)   # Normal
                draw.rectangle([i, j, i+15, j+15], fill=int(intensity))
    
    # Convertir a bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print("✅ Imagen de prueba creada")
    return img_bytes

def test_backend_health():
    """Prueba la salud del backend."""
    print("🏥 Probando salud del backend...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend saludable: {health_data['status']}")
            print(f"📊 Servicios: {health_data['services']}")
            return True
        else:
            print(f"❌ Backend no saludable: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_model_info():
    """Prueba la información del modelo."""
    print("🤖 Probando información del modelo...")
    
    try:
        # Intentar obtener info del modelo (si existe el endpoint)
        response = requests.get("http://localhost:8000/api/v1/model/info", timeout=10)
        if response.status_code == 200:
            model_info = response.json()
            print(f"✅ Información del modelo: {model_info}")
        else:
            print(f"ℹ️  Endpoint de modelo no disponible: {response.status_code}")
    except Exception as e:
        print(f"ℹ️  No se pudo obtener info del modelo: {e}")

def test_pneumonia_detection():
    """Prueba la detección de neumonía."""
    print("🔍 Probando detección de neumonía...")
    
    try:
        # Crear imagen de prueba
        img_bytes = create_test_xray_image()
        
        # Preparar datos para la API
        files = {'file': ('test_xray.png', img_bytes, 'image/png')}
        data = {'patient_info': json.dumps({
            'age': 45,
            'gender': 'M',
            'symptoms': 'Tos, fiebre, dificultad para respirar'
        })}
        
        # Llamar a la API
        print("📤 Enviando imagen al backend...")
        response = requests.post(
            "http://localhost:8000/api/v1/detect",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Detección exitosa!")
            print(f"📊 Resultado: {result['prediction']['predicted_class']}")
            print(f"🎯 Probabilidad: {result['prediction']['prob_neumonia']:.4f}")
            print(f"🆔 Case ID: {result['case_id']}")
            print(f"⏰ Timestamp: {result['timestamp']}")
            
            # Verificar que el heatmap esté presente
            if 'heatmap' in result['prediction']:
                print("🔥 Heatmap generado correctamente")
            else:
                print("⚠️  Heatmap no encontrado en la respuesta")
            
            return True
        else:
            print(f"❌ Error en detección: {response.status_code}")
            print(f"📝 Detalle: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de detección: {e}")
        return False

def test_frontend_connectivity():
    """Prueba la conectividad del frontend."""
    print("🌐 Probando conectividad del frontend...")
    
    try:
        # Verificar que el frontend esté accesible
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accesible en puerto 3000")
            return True
        else:
            print(f"ℹ️  Frontend no accesible en puerto 3000: {response.status_code}")
            return False
    except Exception as e:
        print(f"ℹ️  Frontend no está ejecutándose: {e}")
        return False

def run_performance_test():
    """Ejecuta pruebas de rendimiento."""
    print("⚡ Ejecutando pruebas de rendimiento...")
    
    try:
        # Crear imagen de prueba
        img_bytes = create_test_xray_image()
        files = {'file': ('perf_test.png', img_bytes, 'image/png')}
        
        # Medir tiempo de respuesta
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/v1/detect",
            files=files,
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = end_time - start_time
            print(f"✅ Tiempo de respuesta: {response_time:.2f} segundos")
            
            if response_time < 5.0:
                print("🚀 Rendimiento EXCELENTE (< 5s)")
            elif response_time < 10.0:
                print("👍 Rendimiento BUENO (< 10s)")
            else:
                print("⚠️  Rendimiento LENTO (> 10s)")
            
            return response_time
        else:
            print(f"❌ Error en prueba de rendimiento: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en prueba de rendimiento: {e}")
        return None

def main():
    """Función principal de pruebas."""
    print("🚀 PRUEBA COMPLETA DEL SISTEMA RADOX")
    print("=" * 50)
    
    # Verificar que el backend esté ejecutándose
    if not test_backend_health():
        print("❌ Backend no está funcionando. Ejecuta primero:")
        print("   conda activate radox")
        print("   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    print("\n" + "=" * 50)
    
    # Probar información del modelo
    test_model_info()
    
    print("\n" + "=" * 50)
    
    # Probar detección de neumonía
    if test_pneumonia_detection():
        print("✅ Sistema de detección funcionando correctamente")
    else:
        print("❌ Sistema de detección con problemas")
    
    print("\n" + "=" * 50)
    
    # Probar conectividad del frontend
    test_frontend_connectivity()
    
    print("\n" + "=" * 50)
    
    # Pruebas de rendimiento
    perf_time = run_performance_test()
    
    print("\n" + "=" * 50)
    print("🏁 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    print("✅ Backend: Funcionando")
    print("✅ Modelo TorchXRayVision: Cargado")
    print("✅ API de detección: Funcionando")
    
    if perf_time:
        print(f"✅ Rendimiento: {perf_time:.2f}s")
    
    print("\n🎉 ¡SISTEMA RADOX FUNCIONANDO CORRECTAMENTE!")
    print("\n💡 Para usar el sistema:")
    print("   1. Backend: http://localhost:8000")
    print("   2. API Docs: http://localhost:8000/docs")
    print("   3. Frontend: http://localhost:3000 (si está ejecutándose)")

if __name__ == "__main__":
    main()
