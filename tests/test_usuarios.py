import jwt

from usuarios.app import main as usuarios_main
from usuarios.app.main import password_hash
from usuarios.app.models import Usuario


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

def test_guardar_contrasena_cifrada(
    usuarios_client,
    usuarios_db_session
):
    datos = {
        "nombre": "Carlos",
        "email": "carlos@example.com",
        "password": "password123"
    }

    respuesta = usuarios_client.post(
        "/usuarios/registro",
        json=datos
    )

    usuario = usuarios_db_session.query(Usuario).filter(
        Usuario.email == "carlos@example.com"
    ).first()

    assert respuesta.status_code == 200
    assert usuario is not None
    assert usuario.password_hash != "password123"
    assert password_hash.verify(
        "password123",
        usuario.password_hash
    )


def test_no_devolver_hash_en_respuesta(
    usuarios_client
):
    datos = {
        "nombre": "Ana",
        "email": "ana@example.com",
        "password": "password123"
    }

    respuesta = usuarios_client.post(
        "/usuarios/registro",
        json=datos
    )

    usuario = respuesta.json()["usuario"]

    assert respuesta.status_code == 200
    assert "password" not in usuario
    assert "password_hash" not in usuario


def test_iniciar_sesion_correctamente(usuarios_client):
    usuarios_client.post(
        "/usuarios/registro",
        json={
            "nombre": "Ana",
            "email": "ana@example.com",
            "password": "password123"
        }
    )

    respuesta = usuarios_client.post(
        "/usuarios/login",
        json={
            "email": "ana@example.com",
            "password": "password123"
        }
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert "access_token" in datos
    assert datos["token_type"] == "bearer"

    contenido = jwt.decode(
        datos["access_token"],
        usuarios_main.JWT_SECRET_KEY,
        algorithms=["HS256"]
    )

    assert contenido["sub"] == "1"
    assert "exp" in contenido


def test_rechazar_contrasena_incorrecta(usuarios_client):
    usuarios_client.post(
        "/usuarios/registro",
        json={
            "nombre": "Ana",
            "email": "ana@example.com",
            "password": "password123"
        }
    )

    respuesta = usuarios_client.post(
        "/usuarios/login",
        json={
            "email": "ana@example.com",
            "password": "incorrecta"
        }
    )

    assert respuesta.status_code == 401


def test_rechazar_usuario_inexistente(usuarios_client):
    respuesta = usuarios_client.post(
        "/usuarios/login",
        json={
            "email": "desconocido@example.com",
            "password": "password123"
        }
    )

    assert respuesta.status_code == 401
