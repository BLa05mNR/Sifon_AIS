from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_5hpicSMy1wvT@ep-frosty-feather-a291xvda-pooler.eu-central-1.aws.neon.tech/neondb"

engine = create_async_engine(DATABASE_URL, echo=True)

# Создание асинхронной фабрики сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)

# База моделей
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
