def test_comprobar_servicio(usuarios_client):
    respuesta = usuarios_client.get("/")

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "Microservicio de usuarios funcionando"


def test_registrar_usuario(usuarios_client):
    datos = {
        "nombre": "Ana",
        "email": "ana@example.com",
        "password": "password123"
    }

    respuesta = usuarios_client.post("/usuarios/registro", json=datos)

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["nombre"] == "Ana"
    assert respuesta.json()["usuario"]["email"] == "ana@example.com"


def test_evitar_correo_duplicado(usuarios_client):
    datos = {
        "nombre": "Ana",
        "email": "ana@example.com",
        "password": "password123"
    }

    usuarios_client.post("/usuarios/registro", json=datos)
    respuesta = usuarios_client.post("/usuarios/registro", json=datos)

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El correo electrónico ya está registrado"


def test_rechazar_correo_invalido(usuarios_client):
    datos = {
        "nombre": "Ana",
        "email": "correo-no-valido",
        "password": "password123"
    }

    respuesta = usuarios_client.post("/usuarios/registro", json=datos)

    assert respuesta.status_code == 422
