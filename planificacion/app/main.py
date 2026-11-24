from fastapi import FastAPI
from pydantic import BaseModel, Field

app=FastAPI(
    title="Microservicio de planificación",
    description="Generación de planes de estudio",
    version="1.0.0"
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

@app.get("/")
def comprobar_servicio():
    return {"mensaje": "Microservicio de planificación funcionando"}


@app.post("/planificacion/generar")
def generar_plan(solicitud: SolicitudPlan):
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
        "horas_utilizadas": solicitud.horas_disponibles - horas_restantes,
        "horas_restantes": horas_restantes
    }
