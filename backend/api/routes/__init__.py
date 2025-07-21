"""Módulo de rutas de API para RADOX"""
from .pneumonia import router as pneumonia_router
from .reports import router as reports_router
from .patients import router as patients_router
from .studies import router as studies_router

all_routers = [
    pneumonia_router,
    reports_router,
    patients_router,
    studies_router
] 