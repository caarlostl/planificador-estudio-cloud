
def test_comprobar_servicio(asignaturas_client):
    respuesta = asignaturas_client.get("/")

    assert respuesta.status_code == 200


def test_rechazar_peticion_sin_token(asignaturas_client):
    respuesta = asignaturas_client.get("/asignaturas")

    assert respuesta.status_code == 401


def test_rechazar_token_invalido(asignaturas_client):
    respuesta = asignaturas_client.get(
        "/asignaturas",
        headers={"Authorization": "Bearer token_invalido"}
    )

    assert respuesta.status_code == 401


def test_crear_asignatura(asignaturas_client, auth_headers):
    datos = {
        "nombre": "Cloud Computing",
        "descripcion": "Asignatura del máster"
    }

    respuesta = asignaturas_client.post(
        "/asignaturas",
        json=datos,
        headers=auth_headers(1)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Cloud Computing"
    assert respuesta.json()["estudiante_id"] == 1


def test_listar_solo_asignaturas_propias(asignaturas_client, auth_headers):
    datos = {
        "nombre": "Cloud Computing",
        "descripcion": "Asignatura del máster"
    }

    asignaturas_client.post(
        "/asignaturas",
        json=datos,
        headers=auth_headers(1)
    )

    respuesta = asignaturas_client.get(
        "/asignaturas",
        headers=auth_headers(2)
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_crear_tarea(asignaturas_client, auth_headers):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": "Asignatura del máster"
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura,
        headers=auth_headers(1)
    )

    asignatura_id = respuesta_asignatura.json()["id"]

    tarea = {
        "titulo": "Práctica de Docker",
        "descripcion": "Crear los contenedores",
        "fecha_entrega": "2026-12-01",
        "importancia": 5,
        "dificultad": 3,
        "duracion_estimada": 4,
        "asignatura_id": asignatura_id
    }

    respuesta = asignaturas_client.post(
        "/tareas",
        json=tarea,
        headers=auth_headers(1)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Práctica de Docker"
    assert respuesta.json()["estudiante_id"] == 1


def test_no_crear_tarea_en_asignatura_de_otro_estudiante(
    asignaturas_client,
    auth_headers
):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": ""
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura,
        headers=auth_headers(1)
    )

    tarea = {
        "titulo": "Práctica",
        "descripcion": "",
        "fecha_entrega": "2026-12-01",
        "importancia": 3,
        "dificultad": 3,
        "duracion_estimada": 2,
        "asignatura_id": respuesta_asignatura.json()["id"]
    }

    respuesta = asignaturas_client.post(
        "/tareas",
        json=tarea,
        headers=auth_headers(2)
    )

    assert respuesta.status_code == 404


def test_completar_tarea(asignaturas_client, auth_headers):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": ""
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura,
        headers=auth_headers(1)
    )

    tarea = {
        "titulo": "Práctica",
        "descripcion": "",
        "fecha_entrega": "2026-12-01",
        "importancia": 3,
        "dificultad": 3,
        "duracion_estimada": 2,
        "asignatura_id": respuesta_asignatura.json()["id"]
    }

    respuesta_tarea = asignaturas_client.post(
        "/tareas",
        json=tarea,
        headers=auth_headers(1)
    )

    tarea_id = respuesta_tarea.json()["id"]

    respuesta = asignaturas_client.patch(
        f"/tareas/{tarea_id}/completar",
        headers=auth_headers(1)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True


def test_listar_tareas_pendientes(asignaturas_client, auth_headers):
    asignatura = {
        "nombre": "Cloud Computing",
        "descripcion": ""
    }

    respuesta_asignatura = asignaturas_client.post(
        "/asignaturas",
        json=asignatura,
        headers=auth_headers(1)
    )

    tarea = {
        "titulo": "Práctica",
        "descripcion": "",
        "fecha_entrega": "2026-12-01",
        "importancia": 3,
        "dificultad": 3,
        "duracion_estimada": 2,
        "asignatura_id": respuesta_asignatura.json()["id"]
    }

    asignaturas_client.post(
        "/tareas",
        json=tarea,
        headers=auth_headers(1)
    )

    respuesta = asignaturas_client.get(
        "/tareas/pendientes",
        headers=auth_headers(1)
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["titulo"] == "Práctica"