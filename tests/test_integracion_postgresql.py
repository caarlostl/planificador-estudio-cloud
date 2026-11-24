
from asignaturas_tareas.app import models


def test_persistencia_asignatura_postgresql(
    asignaturas_client,
    postgres_db_session,
    auth_headers,
):
    datos = {
        "nombre": "Cloud Computing",
        "descripcion": "Prueba de integración con PostgreSQL",
    }

    respuesta = asignaturas_client.post(
        "/asignaturas",
        json=datos,
        headers=auth_headers(100),
    )

    assert respuesta.status_code == 200

    asignatura_id = respuesta.json()["id"]

    # Comprobar que el registro está realmente en PostgreSQL
    asignatura_guardada = (
        postgres_db_session.query(models.Asignatura)
        .filter(models.Asignatura.id == asignatura_id)
        .first()
    )

    assert asignatura_guardada is not None
    assert asignatura_guardada.nombre == "Cloud Computing"
    assert asignatura_guardada.estudiante_id == 100


def test_persistencia_tarea_postgresql(
    asignaturas_client,
    postgres_db_session,
    auth_headers,
):
    asignatura = {
        "nombre": "Bases de datos",
        "descripcion": "",
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura,
        headers=auth_headers(200),
    )

    assert respuesta_asignatura.status_code == 200

    asignatura_id = respuesta_asignatura.json()["id"]

    tarea = {
        "titulo": "Práctica de PostgreSQL",
        "descripcion": "Comprobar almacenamiento",
        "fecha_entrega": "2026-12-10",
        "importancia": 5,
        "dificultad": 3,
        "duracion_estimada": 4,
        "asignatura_id": asignatura_id,
    }

    respuesta = asignaturas_client.post(
        "/tareas",
        json=tarea,
        headers=auth_headers(200),
    )

    assert respuesta.status_code == 200

    tarea_id = respuesta.json()["id"]

    tarea_guardada = (
        postgres_db_session.query(models.Tarea)
        .filter(models.Tarea.id == tarea_id)
        .first()
    )

    assert tarea_guardada is not None
    assert tarea_guardada.titulo == "Práctica de PostgreSQL"
    assert tarea_guardada.estudiante_id == 200
