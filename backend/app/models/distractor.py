from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Index
from datetime import datetime
from .user import Base


class Distractor(Base):
    __tablename__ = "distractores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    identificador = Column(String(255), nullable=False)
    tipo = Column(Enum("url", "proceso"), nullable=False)
    categoria = Column(Enum("red_social", "videojuego", "streaming", "otro"), nullable=False)
    origen = Column(Enum("global", "personal"), nullable=False)
    # NULL cuando origen = 'global', obligatorio cuando origen = 'personal'
    estudiante_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Búsquedas rápidas durante monitoreo en tiempo real
        Index("idx_distractores_identificador", "identificador"),
        # Filtrar distractores globales + personales por estudiante
        Index("idx_distractores_origen_estudiante", "origen", "estudiante_id"),
    )
