"""
Alembic 환경 설정 파일
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# 현재 파일의 상위 디렉토리를 파이썬 경로에 추가 (app 모듈을 찾기 위해)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# 프로젝트에서 설정과 DB 베이스 불러오기
from app.core.config import settings
from app.core.database import Base
from app.models import *  # 모든 모델을 임포트 (자동 마이그레이션 지원)

# Alembic의 Config 객체 (alembic.ini 설정 파일과 연결됨)
config = context.config

# 로깅 설정 (alembic.ini에 정의된 로거 사용)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 자동 마이그레이션을 위해 모델의 메타데이터 등록
target_metadata = Base.metadata

# 데이터베이스 URL을 가져오는 함수 (환경변수나 설정에서 불러옴)
def get_url():
    """환경 변수나 설정에서 DB URL 가져오기"""
    return str(settings.DATABASE_URL)

def run_migrations_offline() -> None:
    """
    '오프라인' 모드에서 마이그레이션 실행.
    - DB 엔진을 만들지 않고 URL만 사용
    - SQL 스크립트를 출력하는 방식 (실제 DB 연결 X)
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # SQL에 실제 값 삽입
        dialect_opts={"paramstyle": "named"},  # 바인딩 방식(named 파라미터) 지정
    )

    # 트랜잭션 시작 후 마이그레이션 실행
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    '온라인' 모드에서 마이그레이션 실행.
    - 실제 DB 엔진을 생성하고 연결하여 마이그레이션 실행
    """
    # alembic.ini에 정의된 설정 불러오기
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()  # DB URL을 동적으로 주입

    # SQLAlchemy 엔진 생성 (NullPool = 매 연결마다 새로운 커넥션)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # DB 연결을 맺고 Alembic 컨텍스트에 적용
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # 트랜잭션 내에서 마이그레이션 실행
        with context.begin_transaction():
            context.run_migrations()

# Alembic 실행 모드에 따라 offline/online 함수 실행
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
