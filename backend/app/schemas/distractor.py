from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

DistractorTipo = Literal["url", "proceso"]
DistractorCategoria = Literal["red_social", "videojuego", "streaming", "otro"]
DistractorOrigen = Literal["global", "personal"]


class DistractorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    identificador: str = Field(..., min_length=1, max_length=255)
    tipo: DistractorTipo
    categoria: DistractorCategoria


class DistractorCreate(DistractorBase):
    pass


class DistractorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    identificador: Optional[str] = Field(None, min_length=1, max_length=255)
    tipo: Optional[DistractorTipo] = None
    categoria: Optional[DistractorCategoria] = None


class DistractorOut(DistractorBase):
    id: int
    origen: DistractorOrigen
    estudiante_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
