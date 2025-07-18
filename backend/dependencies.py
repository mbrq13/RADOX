"""
Dependencias de la API RADOX
Funciones de dependencia para inyección de servicios
"""

from fastapi import HTTPException

# Variables globales para servicios (se inicializan en main.py)
# Estas variables se asignan desde main.py durante la inicialización
cnn_model = None
detection_service = None
report_service = None

def set_services(cnn_model_instance, detection_service_instance, report_service_instance):
    """Establecer las instancias de servicios (llamado desde main.py)"""
    global cnn_model, detection_service, report_service
    cnn_model = cnn_model_instance
    detection_service = detection_service_instance
    report_service = report_service_instance

def get_detection_service():
    """Obtener servicio de detección de neumonía"""
    if detection_service is None:
        raise HTTPException(status_code=503, detail="Servicio de detección no disponible")
    return detection_service

def get_report_service():
    """Obtener servicio de generación de informes"""
    if report_service is None:
        raise HTTPException(status_code=503, detail="Servicio de informes no disponible")
    return report_service 