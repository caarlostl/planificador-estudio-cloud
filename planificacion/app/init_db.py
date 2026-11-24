from . import models  # noqa: F401
from .database import Base, engine

Base.metadata.create_all(bind=engine)

print("Tablas de planificación creadas correctamente")
