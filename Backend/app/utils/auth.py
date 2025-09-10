# 이 파일은 인증, 특히 JWT(JSON Web Token) 처리와 관련된 유틸리티 함수들을 제공합니다.
# 다른 서비스나 의존성 파일에서 공통으로 사용되는 인증 관련 보조 기능들을 모아놓았습니다.
#
# - `AuthError`: 인증 과정에서 발생하는 특정 오류들을 처리하기 위한 커스텀 예외 클래스입니다.
# - `verify_supabase_token`: Supabase에서 발급한 JWT 토큰이 유효한지 검증합니다.
#                            Supabase 관리자 클라이언트를 사용하여 토큰의 서명, 만료 시간 등을
#                            확인하고, 성공 시 토큰에 담긴 사용자 정보를 반환합니다.
# - `extract_token_from_header`: HTTP 요청의 'Authorization' 헤더에서 'Bearer' 스킴을 사용하는
#                                토큰을 안전하게 추출합니다.

"""
JWT 토큰 검증을 위한 인증 유틸리티
"""
import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
from app.utils.supabase_client import supabase_admin_client
import logging

logger = logging.getLogger(__name__)

class AuthError(Exception):
    """인증 관련 예외"""
    pass

def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Supabase JWT 토큰 검증
    
    Args:
        token: JWT 토큰 문자열
        
    Returns:
        토큰 페이로드 (사용자 정보 포함)
        
    Raises:
        AuthError: 토큰이 유효하지 않은 경우
    """
    try:
        # Supabase에서 토큰 검증
        response = supabase_admin_client.auth.get_user(token)
        
        if not response.user:
            raise AuthError("유효하지 않은 토큰입니다")
            
        user = response.user
        
        # 토큰 만료 확인
        if user.expires_at:
            expires_at = datetime.fromisoformat(user.expires_at.replace('Z', '+00:00'))
            if expires_at < datetime.now(timezone.utc):
                raise AuthError("만료된 토큰입니다")
        
        return {
            "user_id": user.id,
            "email": user.email,
            "email_confirmed": user.email_confirmed_at is not None,
            "user_metadata": user.user_metadata,
            "app_metadata": user.app_metadata,
            "created_at": user.created_at,
            "last_sign_in": user.last_sign_in_at
        }
        
    except AuthError:
        raise
    except Exception as e:
        logger.error(f"토큰 검증 중 오류 발생: {e}")
        raise AuthError("토큰 검증에 실패했습니다")

def extract_token_from_header(authorization: Optional[str]) -> str:
    """
    Authorization 헤더에서 Bearer 토큰 추출
    
    Args:
        authorization: Authorization 헤더 값
        
    Returns:
        JWT 토큰 문자열
        
    Raises:
        AuthError: 토큰 형식이 올바르지 않은 경우
    """
    if not authorization:
        raise AuthError("Authorization 헤더가 없습니다")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise AuthError("Bearer 토큰이 아닙니다")
        return token
    except ValueError:
        raise AuthError("잘못된 Authorization 헤더 형식입니다")

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    이메일로 Supabase 사용자 조회
    
    Args:
        email: 사용자 이메일
        
    Returns:
        사용자 정보 또는 None
    """
    try:
        response = supabase_admin_client.auth.admin.list_users()
        
        if response.users:
            for user in response.users:
                if user.email == email:
                    return {
                        "user_id": user.id,
                        "email": user.email,
                        "email_confirmed": user.email_confirmed_at is not None,
                        "created_at": user.created_at,
                        "last_sign_in": user.last_sign_in_at,
                        "user_metadata": user.user_metadata
                    }
        
        return None
        
    except Exception as e:
        logger.error(f"사용자 조회 중 오류 발생: {e}")
        return None

def create_or_update_local_user(supabase_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supabase 사용자 정보를 기반으로 로컬 사용자 생성/업데이트
    
    Args:
        supabase_user: Supabase 사용자 정보
        
    Returns:
        로컬 사용자 정보
    """
    # TODO: 실제 데이터베이스 연동 시 구현
    # 현재는 Supabase 사용자 정보를 그대로 반환
    return {
        "id": supabase_user["user_id"],
        "supabase_id": supabase_user["user_id"],
        "email": supabase_user["email"],
        "display_name": supabase_user.get("user_metadata", {}).get("full_name", ""),
        "avatar_url": supabase_user.get("user_metadata", {}).get("avatar_url", ""),
        "is_active": True,
        "email_notifications_enabled": True
    }