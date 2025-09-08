"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy 설정
engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def init_db() -> None:
    """데이터베이스 초기화"""
    async with engine.begin() as conn:
        # 개발환경에서는 모든 테이블을 생성 (프로덕션에서는 마이그레이션 사용)
        if settings.DEBUG:
            await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """데이터베이스 세션 의존성"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()