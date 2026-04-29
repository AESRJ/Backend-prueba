from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import current_active_user
from ..db import get_async_session
from ..models.distractor import Distractor
from ..models.user import User
from ..schemas.distractor import (
    DistractorCreate,
    DistractorOut,
    DistractorUpdate,
)

router = APIRouter(prefix="/distractors", tags=["distractors"])

OrigenFilter = Literal["all", "global", "personal"]


@router.get("", response_model=List[DistractorOut])
async def list_distractors(
    origen: OrigenFilter = Query(
        "all",
        description="Filtra por origen. 'all' devuelve globales + personales del usuario.",
    ),
    categoria: Optional[str] = Query(None, description="Filtra por categoría"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Lista distractores visibles para el usuario."""
    stmt = select(Distractor)

    if origen == "global":
        stmt = stmt.where(Distractor.origen == "global")
    elif origen == "personal":
        stmt = stmt.where(
            Distractor.origen == "personal",
            Distractor.estudiante_id == user.id,
        )
    else:  # 'all'
        stmt = stmt.where(
            or_(
                Distractor.origen == "global",
                (Distractor.origen == "personal")
                & (Distractor.estudiante_id == user.id),
            )
        )

    if categoria is not None:
        stmt = stmt.where(Distractor.categoria == categoria)

    stmt = stmt.order_by(Distractor.origen, Distractor.nombre)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=DistractorOut, status_code=status.HTTP_201_CREATED)
async def create_personal_distractor(
    payload: DistractorCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Crea un distractor personal del usuario autenticado."""
    distractor = Distractor(
        nombre=payload.nombre,
        identificador=payload.identificador,
        tipo=payload.tipo,
        categoria=payload.categoria,
        origen="personal",
        estudiante_id=user.id,
    )
    session.add(distractor)
    await session.commit()
    await session.refresh(distractor)
    return distractor


@router.get("/{distractor_id}", response_model=DistractorOut)
async def get_distractor(
    distractor_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    distractor = await session.get(Distractor, distractor_id)
    if distractor is None:
        raise HTTPException(status_code=404, detail="Distractor no encontrado")
    # Solo permite ver globales o los personales propios
    if distractor.origen == "personal" and distractor.estudiante_id != user.id:
        raise HTTPException(status_code=404, detail="Distractor no encontrado")
    return distractor


@router.patch("/{distractor_id}", response_model=DistractorOut)
async def update_personal_distractor(
    distractor_id: int,
    payload: DistractorUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Actualiza un distractor personal propio. Los globales no se pueden editar."""
    distractor = await session.get(Distractor, distractor_id)
    if distractor is None:
        raise HTTPException(status_code=404, detail="Distractor no encontrado")
    if distractor.origen == "global":
        raise HTTPException(
            status_code=403,
            detail="Los distractores globales no se pueden modificar",
        )
    if distractor.estudiante_id != user.id:
        raise HTTPException(status_code=404, detail="Distractor no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(distractor, key, value)

    session.add(distractor)
    await session.commit()
    await session.refresh(distractor)
    return distractor


@router.delete("/{distractor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_personal_distractor(
    distractor_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Elimina un distractor personal propio. Los globales no se pueden borrar."""
    distractor = await session.get(Distractor, distractor_id)
    if distractor is None:
        raise HTTPException(status_code=404, detail="Distractor no encontrado")
    if distractor.origen == "global":
        raise HTTPException(
            status_code=403,
            detail="Los distractores globales no se pueden eliminar",
        )
    if distractor.estudiante_id != user.id:
        raise HTTPException(status_code=404, detail="Distractor no encontrado")

    await session.delete(distractor)
    await session.commit()
