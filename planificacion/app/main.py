import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .auth import obtener_estudiante_actual
from .database import get_db

app = FastAPI(
    title="Microservicio de planificación",
    description="Generación y gestión de planes de estudio",
    version="1.0.0"
)

ASIGNATURAS_TAREAS_URL = os.getenv(
    "ASIGNATURAS_TAREAS_URL",
    "http://localhost:8001"
)


class TareaPlanificacion(BaseModel):
    titulo: str
    duracion_estimada: float = Field(gt=0)
    importancia: int = Field(ge=1, le=5)
    dificultad: int = Field(ge=1, le=5)
    fecha_entrega: str


class SolicitudPlan(BaseModel):
    horas_disponibles: float = Field(gt=0)
    tareas: list[TareaPlanificacion]


class SolicitudPlanificacion(BaseModel):
    horas_disponibles: float = Field(gt=0)


class SolicitudModificacionPlan(BaseModel):
    horas_disponibles: float = Field(gt=0)
    tareas: list[TareaPlanificacion]

class SolicitudGeneracion(BaseModel):
    horas_disponibles: float = Field(gt=0)

def calcular_plan(solicitud: SolicitudPlan):
    tareas_ordenadas = sorted(
        solicitud.tareas,
        key=lambda tarea: (
            tarea.fecha_entrega,
            -tarea.importancia,
            -tarea.dificultad
        )
    )

    horas_restantes = solicitud.horas_disponibles
    plan = []

    for tarea in tareas_ordenadas:
        if horas_restantes <= 0:
            break

        tiempo_asignado = min(
            tarea.duracion_estimada,
            horas_restantes
        )

        plan.append({
            "tarea": tarea.titulo,
            "horas_asignadas": tiempo_asignado
        })

        horas_restantes -= tiempo_asignado

    return {
        "plan": plan,
        "horas_utilizadas": (
            solicitud.horas_disponibles - horas_restantes
        ),
        "horas_restantes": horas_restantes
    }


@app.get("/")
def comprobar_servicio():
    return {"mensaje": "Microservicio de planificación funcionando"}


@app.post("/planificaciones")
def crear_planificacion(
    solicitud: SolicitudPlanificacion,
    request: Request,
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db),
):
    try:
        respuesta = httpx.get(
            f"{ASIGNATURAS_TAREAS_URL}/tareas/pendientes",
            headers={
                "Authorization": request.headers.get("Authorization")
            },
            timeout=5.0,
        )
        respuesta.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Tiempo de espera agotado al consultar las tareas",
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Error al consultar las tareas pendientes",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con el microservicio de tareas",
        )

    tareas = [
        TareaPlanificacion(**tarea)
        for tarea in respuesta.json()
    ]

    solicitud_plan = SolicitudPlan(
        horas_disponibles=solicitud.horas_disponibles,
        tareas=tareas,
    )

    resultado = calcular_plan(solicitud_plan)

    nueva_planificacion = models.Planificacion(
        estudiante_id=estudiante_id,
        horas_disponibles=solicitud.horas_disponibles,
        plan=resultado["plan"],
        horas_utilizadas=resultado["horas_utilizadas"],
        horas_restantes=resultado["horas_restantes"],
    )

    db.add(nueva_planificacion)
    db.commit()
    db.refresh(nueva_planificacion)

    return {
        "mensaje": "Planificación generada correctamente",
        "id": nueva_planificacion.id,
        "estudiante_id": estudiante_id,
        "tareas_recibidas": len(tareas),
        **resultado,
    }


# Consultar la última planificación de un estudiante
@app.get("/planificaciones/actual")
def obtener_planificacion_actual(
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db),
):
    planificacion = (
        db.query(models.Planificacion)
        .filter(
            models.Planificacion.estudiante_id == estudiante_id
        )
        .order_by(models.Planificacion.fecha_creacion.desc())
        .first()
    )

    if planificacion is None:
        raise HTTPException(
            status_code=404,
            detail="No se ha encontrado ninguna planificación"
        )

    return {
        "id": planificacion.id,
        "estudiante_id": planificacion.estudiante_id,
        "horas_disponibles": planificacion.horas_disponibles,
        "plan": planificacion.plan,
        "horas_utilizadas": planificacion.horas_utilizadas,
        "horas_restantes": planificacion.horas_restantes,
        "fecha_creacion": planificacion.fecha_creacion
    }


# Modificar una planificación existente
@app.put("/planificaciones/{planificacion_id}")
def modificar_planificacion(
    planificacion_id: int,
    solicitud: SolicitudModificacionPlan,
    estudiante_id: int = Depends(obtener_estudiante_actual),
    db: Session = Depends(get_db),
):
    planificacion = db.query(models.Planificacion).filter(
        models.Planificacion.id == planificacion_id,
        models.Planificacion.estudiante_id == estudiante_id
    ).first()

    if planificacion is None:
        raise HTTPException(
            status_code=404,
            detail="No se ha encontrado la planificación"
        )

    resultado = calcular_plan(solicitud)

    planificacion.plan = resultado["plan"]
    planificacion.horas_disponibles = solicitud.horas_disponibles
    planificacion.horas_utilizadas = resultado["horas_utilizadas"]
    planificacion.horas_restantes = resultado["horas_restantes"]

    db.commit()
    db.refresh(planificacion)

    return {
        "mensaje": "Planificación modificada correctamente",
        "id": planificacion.id,
        "estudiante_id": planificacion.estudiante_id,
        **resultado
    }
