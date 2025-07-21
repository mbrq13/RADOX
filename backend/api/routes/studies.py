from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from datetime import datetime
import shutil
import uuid

router = APIRouter()

PROJECT_ROOT = '/home/mbrq/Documents/RADOX'
DATA_PATH = os.path.join(PROJECT_ROOT, 'data/studies.json')
UPLOADS_PATH = os.path.join(PROJECT_ROOT, 'data/uploads')
IMAGES_PATH = os.path.join(PROJECT_ROOT, 'data/uploads/images')
REPORTS_PATH = os.path.join(PROJECT_ROOT, 'data/uploads/reports')

class Study(BaseModel):
    id: str = Field(..., description="ID único del estudio")
    patient_id: str
    fecha_estudio: str
    filename: str
    descripcion: Optional[str] = None
    diagnostico: Optional[str] = None
    confianza: Optional[float] = None

def load_studies() -> List[dict]:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_studies(studies: List[dict]):
    with open(DATA_PATH, 'w') as f:
        json.dump(studies, f, indent=2, ensure_ascii=False)

@router.get("/studies", response_model=List[Study], summary="Listar estudios")
async def get_studies(patient_id: Optional[str] = None):
    studies = load_studies()
    if patient_id:
        studies = [s for s in studies if s['patient_id'] == patient_id]
    return studies

@router.post("/studies", response_model=Study, summary="Crear estudio y subir imagen")
async def create_study(
    patient_id: str = Form(...),
    descripcion: str = Form(None),
    file: UploadFile = File(...)
):
    print("[DEBUG] POST /studies llamado")
    print(f"[DEBUG] patient_id: {patient_id}")
    print(f"[DEBUG] descripcion: {descripcion}")
    print(f"[DEBUG] file.filename: {file.filename}")
    print(f"[DEBUG] file.file type: {type(file.file)}")
    try:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        print(f"[DEBUG] file actual size: {size} bytes")
    except Exception as e:
        print(f"[ERROR] No se pudo determinar el tamaño del archivo: {e}")
    studies = load_studies()
    study_id = str(uuid.uuid4())
    fecha_estudio = datetime.now().isoformat()
    # Crear carpetas si no existen
    if not os.path.exists(IMAGES_PATH):
        os.makedirs(IMAGES_PATH)
    if not os.path.exists(REPORTS_PATH):
        os.makedirs(REPORTS_PATH)
    filename = f"{study_id}_{file.filename}"
    file_path = os.path.join(IMAGES_PATH, filename)
    print(f"[DEBUG] Guardando archivo en: {file_path}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"[DEBUG] Archivo guardado correctamente")
    except Exception as e:
        print(f"[ERROR] Error guardando archivo: {e}")
    try:
        study = Study(
            id=study_id,
            patient_id=patient_id,
            fecha_estudio=fecha_estudio,
            filename=filename,  # Solo el nombre, no la ruta completa
            descripcion=descripcion
        )
        studies.append(study.dict())
        save_studies(studies)
        print(f"[DEBUG] Estudio guardado en studies.json: {study.dict()}")
        return study
    except Exception as e:
        print(f"[ERROR] Error guardando estudio en JSON: {e}")
        raise HTTPException(status_code=500, detail=f"Error guardando estudio: {e}")

@router.patch("/studies/{study_id}", response_model=Study, summary="Actualizar diagnóstico/confianza de un estudio")
async def update_study(
    study_id: str = Path(..., description="ID del estudio a actualizar"),
    diagnostico: str = Form(None),
    confianza: float = Form(None)
):
    studies = load_studies()
    for study in studies:
        if study["id"] == study_id:
            if diagnostico is not None:
                study["diagnostico"] = diagnostico
            if confianza is not None:
                study["confianza"] = confianza
            save_studies(studies)
            return study
    raise HTTPException(status_code=404, detail="Estudio no encontrado")

@router.delete("/studies/{study_id}", summary="Borrar un estudio")
async def delete_study(study_id: str = Path(..., description="ID del estudio a borrar")):
    studies = load_studies()
    new_studies = [s for s in studies if s["id"] != study_id]
    if len(new_studies) == len(studies):
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    save_studies(new_studies)
    return {"success": True, "deleted_id": study_id} 