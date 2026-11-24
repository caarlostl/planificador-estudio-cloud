
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .auth import obtener_estudiante_actual
from .database import get_db

app = FastAPI(
    title="Microservicio de asignaturas y tareas",
    description="Gestión de asignaturas y tareas de los estudiantes",
    version="1.0.0"
)


class AsignaturaEntrada(BaseModel):
    nombre: str
    descripcion: str = ""


class TareaEntrada(BaseModel):
    titulo: str
    descripcion: str = ""
    fecha_entrega: str
    importancia: int = Field(ge=1, le=5)
    dificultad: int = Field(ge=1, le=5)
    duracion_estimada: float = Field(gt=0)
    asignatura_id: int


@app.get("/")
def comprobar_servicio():
    return {"mensaje": "Microservicio de asignaturas y tareas funcionando"}


@app.post("/asignaturas")
def crear_asignatura(
    asignatura: AsignaturaEntrada,
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db)
):
    nueva = models.Asignatura(
        **asignatura.model_dump(),
        estudiante_id=estudiante_id
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@app.get("/asignaturas")
def listar_asignaturas(
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db)
):
    return db.query(models.Asignatura).filter(
        models.Asignatura.estudiante_id == estudiante_id
    ).all()


@app.post("/tareas")
def crear_tarea(
    tarea: TareaEntrada,
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db)
):
    asignatura = db.query(models.Asignatura).filter(
        models.Asignatura.id == tarea.asignatura_id,
        models.Asignatura.estudiante_id == estudiante_id
    ).first()

    if not asignatura:
        raise HTTPException(
            status_code=404,
            detail="La asignatura no existe para este estudiante"
        )

    nueva = models.Tarea(
        **tarea.model_dump(),
        estudiante_id=estudiante_id
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@app.get("/tareas")
def listar_tareas_estudiante(
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db)
):
    return db.query(models.Tarea).filter(
        models.Tarea.estudiante_id == estudiante_id
    ).all()


@app.get("/tareas/pendientes")
def listar_tareas_pendientes(
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db)
):
    return db.query(models.Tarea).filter(
        models.Tarea.estudiante_id == estudiante_id,
        models.Tarea.completada.is_(False)
    ).all()


@app.patch("/tareas/{tarea_id}/completar")
def completar_tarea(
    tarea_id: int,
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db)
):
    tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.estudiante_id == estudiante_id
    ).first()

    if not tarea:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada"
        )

    tarea.completada = True
    db.commit()
    db.refresh(tarea)
    return tarea