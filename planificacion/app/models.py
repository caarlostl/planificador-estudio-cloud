from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Planificacion(Base):
    __tablename__ = "planificaciones"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    estudiante_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    horas_disponibles: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    plan: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )

    horas_utilizadas: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    horas_restantes: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
