import asyncio
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models.campaign import Base

settings = get_settings()
logger = structlog.get_logger()

# ✅ ASYNC ENGINE
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)

# ✅ ASYNC SESSION FACTORY
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ✅ WAIT FOR DB
async def wait_for_db(max_retries=30, delay=2):
    for attempt in range(max_retries):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return
        except Exception as e:
            logger.warning(
                f"Database connection attempt {attempt + 1}/{max_retries} failed",
                error=str(e),
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error("Failed to connect to database after all retries")
                raise

# ✅ INIT DB
async def init_db():
    await wait_for_db()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully")

# ✅ FASTAPI DEPENDENCY
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            await session.close()

# ✅ SHUTDOWN
async def close_db():
    await engine.dispose()
    logger.info("Database connection closed")
