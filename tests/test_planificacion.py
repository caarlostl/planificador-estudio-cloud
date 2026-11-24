def test_comprobar_servicio(planificacion_client):
    respuesta = planificacion_client.get("/")

    assert respuesta.status_code == 200


def test_generar_plan_con_varias_tareas(planificacion_client):
    datos = {
        "horas_disponibles": 5,
        "tareas": [
            {
                "titulo": "Práctica de Cloud",
                "duracion_estimada": 3,
                "importancia": 5,
                "dificultad": 4,
                "fecha_entrega": "2026-12-01"
            },
            {
                "titulo": "Estudiar teoría",
                "duracion_estimada": 4,
                "importancia": 3,
                "dificultad": 2,
                "fecha_entrega": "2026-12-03"
            }
        ]
    }

    respuesta = planificacion_client.post(
        "/planificacion/generar",
        json=datos
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert len(resultado["plan"]) == 2
    assert resultado["horas_utilizadas"] == 5
    assert resultado["horas_restantes"] == 0


def test_rechazar_horas_disponibles_no_validas(planificacion_client):
    datos = {
        "horas_disponibles": 0,
        "tareas": []
    }

    respuesta = planificacion_client.post(
        "/planificacion/generar",
        json=datos
    )

    assert respuesta.status_code == 422


def test_generar_plan_sin_tareas(planificacion_client):
    datos = {
        "horas_disponibles": 5,
        "tareas": []
    }

    respuesta = planificacion_client.post(
        "/planificacion/generar",
        json=datos
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["plan"] == []
    assert respuesta.json()["horas_utilizadas"] == 0
    assert respuesta.json()["horas_restantes"] == 5
