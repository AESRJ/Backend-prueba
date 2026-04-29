from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

DistractorCategoria = Literal["red_social", "videojuego", "streaming", "otro"]
RestrictionLevel = Literal["bajo", "intermedio", "alto"]


class DetectionCreate(BaseModel):
    # El frontend puede enviar `distractor_id` (preferido) o `identificador`
    # (hostname/proceso) para que el backend resuelva el distractor.
    distractor_id: Optional[int] = None
    identificador: Optional[str] = Field(None, min_length=1, max_length=255)

    nombre_detectado: str = Field(..., min_length=1, max_length=100)
    categoria: DistractorCategoria
    # Si no se envía, se calcula con datetime.utcnow al recibir.
    timestamp_deteccion: Optional[str] = Field(
        None,
        description="Formato YYYY-MM-DD|HH:MM:SS. Si se omite, se genera en servidor.",
        max_length=20,
    )


class DetectionOut(BaseModel):
    id: int
    sesion_id: int
    distractor_id: int
    nombre_detectado: str
    categoria: DistractorCategoria
    nivel_restriccion_activo: RestrictionLevel
    timestamp_deteccion: str
    timestamp_nativo: datetime

    model_config = {"from_attributes": True}
