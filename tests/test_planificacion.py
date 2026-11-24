
import httpx


def crear_tareas(asignaturas_client, auth_headers, estudiante_id=1):
    respuesta = asignaturas_client.post(
        "/asignaturas",
        json={
            "nombre": "Matemáticas",
            "descripcion": "Asignatura de prueba",
        },
        headers=auth_headers(estudiante_id),
    )

    asignatura_id = respuesta.json()["id"]

    tareas = [
        {
            "titulo": "Estudiar álgebra",
            "duracion_estimada": 3,
            "importancia": 5,
            "dificultad": 4,
            "fecha_entrega": "2026-12-01",
            "asignatura_id": asignatura_id,
        },
        {
            "titulo": "Estudiar geometría",
            "duracion_estimada": 2,
            "importancia": 4,
            "dificultad": 3,
            "fecha_entrega": "2026-12-05",
            "asignatura_id": asignatura_id,
        },
    ]

    for tarea in tareas:
        asignaturas_client.post(
            "/tareas",
            json=tarea,
            headers=auth_headers(estudiante_id),
        )


def datos_nueva_planificacion():
    return {
        "horas_disponibles": 5,
    }


def datos_modificacion():
    return {
        "horas_disponibles": 6,
        "tareas": [
            {
                "titulo": "Estudiar álgebra",
                "duracion_estimada": 3,
                "importancia": 5,
                "dificultad": 4,
                "fecha_entrega": "2026-12-01",
            },
            {
                "titulo": "Estudiar geometría",
                "duracion_estimada": 2,
                "importancia": 4,
                "dificultad": 3,
                "fecha_entrega": "2026-12-05",
            },
        ],
    }


def test_comprobar_servicio(planificacion_client):
    respuesta = planificacion_client.get("/")

    assert respuesta.status_code == 200


def test_rechazar_horas_disponibles_no_validas(
    planificacion_client,
    auth_headers,
):
    respuesta = planificacion_client.post(
        "/planificaciones",
        json={"horas_disponibles": 0},
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 422


def test_generar_plan_sin_tareas(
    planificacion_client,
    conectar_microservicios,
    auth_headers,
):
    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert resultado["tareas_recibidas"] == 0
    assert resultado["plan"] == []
    assert resultado["horas_utilizadas"] == 0
    assert resultado["horas_restantes"] == 5


# Pruebas de integración entre microservicios

def test_consultar_tareas_pendientes(
    planificacion_client,
    asignaturas_client,
    conectar_microservicios,
    auth_headers,
):
    crear_tareas(asignaturas_client, auth_headers)

    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["tareas_recibidas"] == 2

    assert len(conectar_microservicios) == 1
    assert conectar_microservicios[0].endswith(
        "/tareas/pendientes"
    )


def test_generar_plan_con_tareas_recibidas(
    planificacion_client,
    asignaturas_client,
    conectar_microservicios,
    auth_headers,
):
    crear_tareas(asignaturas_client, auth_headers)

    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert len(resultado["plan"]) == 2
    assert resultado["plan"][0]["tarea"] == "Estudiar álgebra"
    assert resultado["plan"][0]["horas_asignadas"] == 3
    assert resultado["plan"][1]["tarea"] == "Estudiar geometría"
    assert resultado["plan"][1]["horas_asignadas"] == 2
    assert resultado["horas_utilizadas"] == 5
    assert resultado["horas_restantes"] == 0


def test_guardar_planificacion_generada(
    planificacion_client,
    asignaturas_client,
    conectar_microservicios,
    auth_headers,
):
    crear_tareas(asignaturas_client, auth_headers)

    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 200
    planificacion_id = respuesta.json()["id"]

    consulta = planificacion_client.get(
        "/planificaciones/actual",
        headers=auth_headers(1),
    )

    assert consulta.status_code == 200
    assert consulta.json()["id"] == planificacion_id
    assert consulta.json()["estudiante_id"] == 1
    assert len(consulta.json()["plan"]) == 2
    assert consulta.json()["horas_utilizadas"] == 5


def test_error_si_microservicio_no_responde(
    planificacion_client,
    monkeypatch,
    auth_headers,
):
    def simular_error_conexion(url, headers=None, timeout=5.0):
        raise httpx.ConnectError(
            "Error de conexión",
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(
        "planificacion.app.main.httpx.get",
        simular_error_conexion,
    )

    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 503
    assert respuesta.json()["detail"] == (
        "No se pudo conectar con el microservicio de tareas"
    )


# Pruebas de consulta y modificación de planificaciones

def test_consultar_planificacion_inexistente(
    planificacion_client,
    auth_headers,
):
    respuesta = planificacion_client.get(
        "/planificaciones/actual",
        headers=auth_headers(99),
    )

    assert respuesta.status_code == 404


def test_modificar_planificacion(
    planificacion_client,
    asignaturas_client,
    conectar_microservicios,
    auth_headers,
):
    crear_tareas(asignaturas_client, auth_headers)

    creacion = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    planificacion_id = creacion.json()["id"]

    respuesta = planificacion_client.put(
        f"/planificaciones/{planificacion_id}",
        json=datos_modificacion(),
        headers=auth_headers(1),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == planificacion_id
    assert respuesta.json()["horas_utilizadas"] == 5
    assert respuesta.json()["horas_restantes"] == 1


def test_no_modificar_planificacion_de_otro_estudiante(
    planificacion_client,
    asignaturas_client,
    conectar_microservicios,
    auth_headers,
):
    crear_tareas(asignaturas_client, auth_headers)

    creacion = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers=auth_headers(1),
    )

    planificacion_id = creacion.json()["id"]

    respuesta = planificacion_client.put(
        f"/planificaciones/{planificacion_id}",
        json=datos_modificacion(),
        headers=auth_headers(2),
    )

    assert respuesta.status_code == 404


# Pruebas de autenticación

def test_rechazar_peticion_sin_token(planificacion_client):
    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
    )

    assert respuesta.status_code == 401


def test_rechazar_token_invalido(planificacion_client):
    respuesta = planificacion_client.post(
        "/planificaciones",
        json=datos_nueva_planificacion(),
        headers={"Authorization": "Bearer token_invalido"},
    )

    assert respuesta.status_code == 401
