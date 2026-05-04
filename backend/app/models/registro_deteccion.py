from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Index
from datetime import datetime
from .user import Base


class RegistroDeteccion(Base):
    __tablename__ = "registros_deteccion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones.id"), nullable=False)
    distractor_id = Column(Integer, ForeignKey("distractores.id"), nullable=False)
    nombre_detectado = Column(String(100), nullable=False)
    categoria = Column(Enum("red_social", "videojuego", "streaming", "otro"), nullable=False)
    nivel_restriccion_activo = Column(Enum("bajo", "intermedio", "alto"), nullable=False)
    # Formato textual requerido por la historia: YYYY-MM-DD|HH:MM:SS
    timestamp_deteccion = Column(String(20), nullable=False)
    # Timestamp nativo en paralelo para consultas y ordenamientos eficientes
    timestamp_nativo = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_registros_sesion", "sesion_id"),
        Index("idx_registros_timestamp", "timestamp_deteccion"),
    )
