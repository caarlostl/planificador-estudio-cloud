import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from asignaturas_tareas.app.database import Base, get_db
from asignaturas_tareas.app.main import app as asignaturas_app
from planificacion.app.main import app as planificacion_app
from usuarios.app import main as usuarios_main
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
def usuarios_client():
    usuarios_main.usuarios.clear()

    with TestClient(usuarios_app) as client:
        yield client


@pytest.fixture
def asignaturas_client(db_session):
    with TestClient(asignaturas_app) as client:
        yield client


@pytest.fixture
def planificacion_client():
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