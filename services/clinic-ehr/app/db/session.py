from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = None
_factory = None


def _get_factory():
    global _engine, _factory
    if _factory is None:
        from app.config import settings
        _engine = create_async_engine(settings.database_url, echo=False)
        _factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _get_factory()() as session:
        yield session
