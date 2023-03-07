from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import Config

# Async
async_engine = create_async_engine(Config.DATABASE_URI, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, autoflush=False, future=True, class_=AsyncSession
)
