from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from src.app.config import Settings

settings = Settings()

engine = create_async_engine(str(settings.postgres_url).replace("postgresql://", "postgresql+asyncpg://"))
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

