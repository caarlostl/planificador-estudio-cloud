def test_comprobar_servicio(asignaturas_client):
    respuesta = asignaturas_client.get("/")

    assert respuesta.status_code == 200


def test_crear_asignatura(asignaturas_client):
    datos = {
        "nombre": "Cloud Computing",
        "descripcion": "Asignatura del máster",
        "estudiante_id": 1
    }

    respuesta = asignaturas_client.post("/asignaturas", json=datos)

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Cloud Computing"


def test_crear_tarea(asignaturas_client):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": "Asignatura del máster",
        "estudiante_id": 1
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura
    )

    asignatura_id = respuesta_asignatura.json()["id"]

    tarea = {
        "titulo": "Práctica de Docker",
        "descripcion": "Crear los contenedores",
        "fecha_entrega": "2026-12-01",
        "importancia": 5,
        "dificultad": 3,
        "duracion_estimada": 4,
        "estudiante_id": 1,
        "asignatura_id": asignatura_id
    }

    respuesta = asignaturas_client.post("/tareas", json=tarea)

    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Práctica de Docker"


def test_no_crear_tarea_en_asignatura_de_otro_estudiante(asignaturas_client):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": "",
        "estudiante_id": 1
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura
    )

    tarea = {
        "titulo": "Práctica",
        "descripcion": "",
        "fecha_entrega": "2026-12-01",
        "importancia": 3,
        "dificultad": 3,
        "duracion_estimada": 2,
        "estudiante_id": 2,
        "asignatura_id": respuesta_asignatura.json()["id"]
    }

    respuesta = asignaturas_client.post("/tareas", json=tarea)

    assert respuesta.status_code == 404


def test_completar_tarea(asignaturas_client):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": "",
        "estudiante_id": 1
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura
    )

    tarea = {
        "titulo": "Práctica",
        "descripcion": "",
        "fecha_entrega": "2026-12-01",
        "importancia": 3,
        "dificultad": 3,
        "duracion_estimada": 2,
        "estudiante_id": 1,
        "asignatura_id": respuesta_asignatura.json()["id"]
    }

    respuesta_tarea = asignaturas_client.post("/tareas", json=tarea)
    tarea_id = respuesta_tarea.json()["id"]

    respuesta = asignaturas_client.patch(
        f"/tareas/{tarea_id}/completar",
        params={"estudiante_id": 1}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True


def test_listar_tareas_pendientes(asignaturas_client):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": "",
        "estudiante_id": 1
    }

    asignaturas_client.post("/asignaturas", json=asignatura)

    respuesta = asignaturas_client.get("/tareas/pendientes/1")

    assert respuesta.status_code == 200
    assert respuesta.json() == []
