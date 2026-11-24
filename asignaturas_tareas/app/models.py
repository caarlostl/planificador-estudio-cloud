from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Asignatura(Base):
    __tablename__ = "asignaturas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), default="")
    estudiante_id: Mapped[int] = mapped_column(Integer, nullable=False)

    tareas: Mapped[list["Tarea"]] = relationship(
        back_populates="asignatura",
        cascade="all, delete-orphan"
    )


class Tarea(Base):
    __tablename__ = "tareas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), default="")
    fecha_entrega: Mapped[str] = mapped_column(String(10), nullable=False)
    importancia: Mapped[int] = mapped_column(Integer, nullable=False)
    dificultad: Mapped[int] = mapped_column(Integer, nullable=False)
    duracion_estimada: Mapped[float] = mapped_column(Float, nullable=False)
    completada: Mapped[bool] = mapped_column(Boolean, default=False)

    estudiante_id: Mapped[int] = mapped_column(Integer, nullable=False)
    asignatura_id: Mapped[int] = mapped_column(
        ForeignKey("asignaturas.id"),
        nullable=False
    )

    asignatura: Mapped["Asignatura"] = relationship(
        back_populates="tareas"
    )
