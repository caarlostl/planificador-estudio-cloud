import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

import httpx
import jwt
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from asignaturas_tareas.app.auth import JWT_SECRET_KEY
from asignaturas_tareas.app.database import Base, get_db
from asignaturas_tareas.app.main import app as asignaturas_app
from planificacion.app.database import Base as PlanificacionBase
from planificacion.app.database import get_db as get_planificacion_db
from planificacion.app.main import app as planificacion_app
from usuarios.app.database import Base as UsuariosBase
from usuarios.app.database import get_db as get_usuarios_db
from usuarios.app.main import app as usuarios_app

load_dotenv()


#Base de datos SQLite temporal para las pruebas
engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    asignaturas_app.dependency_overrides[get_db] = override_get_db

    yield db

    db.close()
    asignaturas_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)



@pytest.fixture
def usuarios_db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    UsuariosBase.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    usuarios_app.dependency_overrides[get_usuarios_db] = override_get_db

    yield db

    db.close()
    usuarios_app.dependency_overrides.clear()
    UsuariosBase.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def usuarios_client(usuarios_db_session):
    with TestClient(usuarios_app) as client:
        yield client



@pytest.fixture
def asignaturas_client(db_session):
    with TestClient(asignaturas_app) as client:
        yield client



@pytest.fixture
def planificacion_db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    PlanificacionBase.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )

    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    planificacion_app.dependency_overrides[
        get_planificacion_db
    ] = override_get_db

    yield db

    db.close()
    planificacion_app.dependency_overrides.clear()
    PlanificacionBase.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def planificacion_client(planificacion_db_session):
    with TestClient(planificacion_app) as client:
        yield client


@pytest.fixture
def postgres_db_session():
    database_url = os.getenv("TEST_ASIGNATURAS_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "Falta TEST_ASIGNATURAS_DATABASE_URL en el archivo .env"
        )

    engine = create_engine(database_url, pool_pre_ping=True)

    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )

    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    asignaturas_app.dependency_overrides[get_db] = override_get_db

    yield db

    db.close()
    asignaturas_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def conectar_microservicios(asignaturas_client, monkeypatch):
    peticiones = []

    def simular_peticion(url, headers=None, timeout=5.0):
        ruta = urlsplit(url).path

        peticiones.append(url)

        respuesta = asignaturas_client.get(
            ruta,
            headers=headers,
        )

        return httpx.Response(
            status_code=respuesta.status_code,
            json=respuesta.json(),
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(
        "planificacion.app.main.httpx.get",
        simular_peticion,
    )

    return peticiones


@pytest.fixture
def auth_headers():
    def crear_cabecera(estudiante_id):
        token = jwt.encode(
            {
                "sub": str(estudiante_id),
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
            },
            JWT_SECRET_KEY,
            algorithm="HS256"
        )

        return {"Authorization": f"Bearer {token}"}

    return crear_cabecera