
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

#Cargar las variables del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("USUARIOS_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("No se ha encontrado USUARIOS_DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
