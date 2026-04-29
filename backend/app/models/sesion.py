from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, Index
from datetime import datetime
from .user import Base


class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    estudiante_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Snapshot del nivel al iniciar — inmutable durante la sesión
    nivel_restriccion_sesion = Column(Enum("bajo", "intermedio", "alto"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(Enum("activa", "finalizada"), nullable=False, default="activa")

    __table_args__ = (
        # Localizar rápidamente la sesión activa de un estudiante
        Index("idx_sesiones_estudiante_estado", "estudiante_id", "estado"),
    )
