"""
FastAPI dependencies for authentication and other common functionality
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