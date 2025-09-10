"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op   # Alembic에서 제공하는 마이그레이션 작업 함수들 (테이블 추가/삭제, 컬럼 변경 등)
import sqlalchemy as sa  # SQLAlchemy (컬럼, 타입 정의 등에 사용)
${imports if imports else ""}   # 필요시 추가 import (예: Enum, JSON 등)

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}       # 현재 revision ID (고유 값)
down_revision = ${repr(down_revision)}  # 이전 revision ID
branch_labels = ${repr(branch_labels)}  # 브랜치 라벨 (특별한 경우에만 사용)
depends_on = ${repr(depends_on)}        # 다른 마이그레이션에 의존성이 있을 경우 지정


def upgrade() -> None:
    """
    upgrade(): 마이그레이션 '적용' 시 실행되는 함수
    예: 새로운 테이블 생성, 컬럼 추가, 제약 조건 변경 등
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    downgrade(): 마이그레이션 '롤백' 시 실행되는 함수
    예: upgrade에서 추가한 테이블/컬럼 제거, 원래 상태로 되돌리기
    """
    ${downgrades if downgrades else "pass"}