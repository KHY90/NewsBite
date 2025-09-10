# 이 파일은 데이터베이스 연결 및 세션 관리를 담당합니다.
# SQLAlchemy를 사용하여 비동기 데이터베이스 엔진(async_engine)을 생성하고,
# FastAPI의 의존성 주입 시스템에서 사용할 세션(async_session)을 설정합니다.
# 또한, 애플리케이션 시작 시 데이터베이스를 초기화하는 `init_db` 함수와
# 각 API 요청마다 데이터베이스 세션을 제공하는 `get_db` 함수를 정의합니다.

"""
데이터베이스 구성 및 세션 관리
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