from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .core.config import settings
from .models.user import User

# Corregir el driver en la URL si viene como mysql:// o mysql+mysqldb://
def _fix_db_url(url: str) -> str:
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+aiomysql://", 1)
    if url.startswith("mysql+mysqldb://"):
        return url.replace("mysql+mysqldb://", "mysql+aiomysql://", 1)
    return url

engine = create_async_engine(
    _fix_db_url(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)