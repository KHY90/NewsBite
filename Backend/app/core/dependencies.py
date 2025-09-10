# 이 파일은 FastAPI 애플리케이션에서 사용되는 공통 의존성(Dependency)들을 정의합니다.
# 주로 사용자 인증과 관련된 기능을 제공하며, API 엔드포인트에서 사용자의 로그인 상태를
# 확인하고 현재 사용자 정보를 가져오는 역할을 합니다.
#
# - `get_current_user`: HTTP 헤더의 Bearer 토큰을 검증하여 현재 로그인된 사용자 정보를 반환합니다.
#                       인증이 필요한 모든 엔드포인트에서 사용됩니다.
# - `get_current_user_optional`: 토큰이 있는 경우에만 사용자 정보를 반환하고, 없어도 오류를
#                                발생시키지 않아 비로그인 상태에서도 접근 가능한 엔드포인트에 사용됩니다.
# - `get_current_active_user`: `get_current_user`와 유사하지만, 이메일 인증까지 완료된
#                              활성 사용자만 허용하는 더 엄격한 인증입니다.
# - `get_db_session`: 데이터베이스 세션을 생성하고 반환하는 의존성입니다.

"""
인증 및 기타 공통 기능을 위한 FastAPI 의존성
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.utils.auth import verify_supabase_token, extract_token_from_header, AuthError
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 토큰 스키마
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    현재 인증된 사용자 정보 가져오기
    
    Args:
        credentials: HTTP Bearer 인증 자격증명
        
    Returns:
        사용자 정보 딕셔너리
        
    Raises:
        HTTPException: 인증 실패 시
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user_info = verify_supabase_token(token)
        return user_info
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"사용자 인증 중 예기치 못한 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 처리 중 오류가 발생했습니다"
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    선택적 사용자 인증 (로그인하지 않아도 접근 가능한 엔드포인트용)
    
    Args:
        credentials: HTTP Bearer 인증 자격증명
        
    Returns:
        사용자 정보 또는 None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_info = verify_supabase_token(token)
        return user_info
        
    except AuthError as e:
        logger.warning(f"선택적 인증에서 토큰 검증 실패: {e}")
        return None
    except Exception as e:
        logger.error(f"선택적 인증 중 예기치 못한 오류: {e}")
        return None

def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    활성 사용자만 허용 (이메일 인증 완료 사용자)
    
    Args:
        current_user: 현재 사용자 정보
        
    Returns:
        활성 사용자 정보
        
    Raises:
        HTTPException: 이메일 미인증 시
    """
    if not current_user.get("email_confirmed"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이메일 인증이 필요합니다"
        )
    
    return current_user

async def get_db_session() -> AsyncSession:
    """
    데이터베이스 세션 의존성
    
    Yields:
        AsyncSession: 데이터베이스 세션
    """
    async with get_db() as session:
        yield session