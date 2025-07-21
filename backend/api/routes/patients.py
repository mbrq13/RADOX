from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from datetime import datetime

router = APIRouter()

PROJECT_ROOT = '/home/mbrq/Documents/RADOX'
DATA_PATH = os.path.join(PROJECT_ROOT, 'data/patients.json')

class Patient(BaseModel):
    id: str = Field(..., description="ID único del paciente")
    nombre: str
    edad: Optional[int] = None
    genero: Optional[str] = None
    fecha_registro: str

def load_patients() -> List[dict]:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_patients(patients: List[dict]):
    with open(DATA_PATH, 'w') as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)

@router.get("/patients", response_model=List[Patient], summary="Listar pacientes")
async def get_patients():
    return load_patients()

@router.post("/patients", response_model=Patient, summary="Crear paciente")
async def create_patient(paciente: Patient):
    pacientes = load_patients()
    if any(p['id'] == paciente.id for p in pacientes):
        raise HTTPException(status_code=400, detail="ID de paciente ya existe")
    paciente.fecha_registro = datetime.now().isoformat()
    pacientes.append(paciente.dict())
    save_patients(pacientes)
    return paciente 