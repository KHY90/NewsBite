# 이 파일은 사용자 인증 관련 API 엔드포인트를 정의합니다.
# Google OAuth를 이용한 로그인, 로그아웃, 현재 사용자 정보 조회,
# 그리고 JWT 토큰의 유효성 검증 기능을 제공합니다.
# 각 엔드포인트는 AuthService를 호출하여 비즈니스 로직을 처리합니다.

"""
인증 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.core.dependencies import get_current_user, get_db_session
from app.schemas.auth import (
    GoogleLoginRequest, LoginResponse, LogoutResponse, 
    UserResponse, TokenValidationRequest, TokenValidationResponse,
    UserUpdateRequest
)
from app.services.auth_service import AuthService
from app.utils.auth import AuthError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/google-login", response_model=LoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db_session)
) -> LoginResponse:
    """
    구글 OAuth 로그인
    
    - 구글 OAuth Access Token을 받아서 Supabase 인증 수행
    - 성공 시 Supabase JWT 토큰과 사용자 정보 반환
    - 로컬 데이터베이스에 사용자 정보 저장/업데이트
    """
    try:
        # 구글 OAuth 토큰으로 Supabase 인증
        auth_result = await AuthService.authenticate_with_google(request.access_token)
        
        # 로컬 데이터베이스에 사용자 정보 저장/업데이트
        user = await AuthService.get_or_create_user(db, auth_result["user"])
        
        # 응답 데이터 구성
        user_response = UserResponse(
            id=str(user.id),
            supabase_id=user.supabase_id,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            email_notifications_enabled=user.email_notifications_enabled,
            email_send_time=user.email_send_time,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        
        return LoginResponse(
            access_token=auth_result["access_token"],
            token_type=auth_result["token_type"],
            expires_in=auth_result.get("expires_in"),
            user=user_response
        )
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"구글 로그인 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: dict = Depends(get_current_user)
) -> LogoutResponse:
    """
    로그아웃
    
    - 현재 사용자 세션 종료
    - Supabase 토큰 무효화
    """
    try:
        # 로그아웃 처리 (현재는 클라이언트에서 토큰 삭제로 처리)
        # Supabase는 서버사이드에서 토큰 무효화가 제한적이므로
        # 클라이언트에서 토큰을 삭제하도록 안내
        
        return LogoutResponse(
            message="성공적으로 로그아웃되었습니다. 클라이언트에서 토큰을 삭제해주세요."
        )
        
    except Exception as e:
        logger.error(f"로그아웃 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    현재 사용자 정보 조회
    
    - JWT 토큰을 검증하여 현재 로그인한 사용자 정보 반환
    - 로컬 데이터베이스의 최신 사용자 정보 반영
    """
    try:
        # 로컬 데이터베이스에서 사용자 정보 조회
        user = await AuthService.get_user_by_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 정보를 찾을 수 없습니다"
            )
        
        return UserResponse(
            id=str(user.id),
            supabase_id=user.supabase_id,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            email_notifications_enabled=user.email_notifications_enabled,
            email_send_time=user.email_send_time,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 정보 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 정보 조회 중 오류가 발생했습니다"
        )


@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(request: TokenValidationRequest) -> TokenValidationResponse:
    """
    JWT 토큰 유효성 검증
    
    - 프론트엔드에서 토큰 유효성을 확인할 때 사용
    - 토큰이 유효한 경우 사용자 정보도 함께 반환
    """
    try:
        validation_result = await AuthService.validate_token(request.token)
        
        if validation_result["valid"]:
            user_info = validation_result["user"]
            user_response = UserResponse(
                id=user_info["user_id"],
                supabase_id=user_info["user_id"],
                email=user_info["email"],
                display_name=user_info.get("user_metadata", {}).get("full_name", ""),
                avatar_url=user_info.get("user_metadata", {}).get("avatar_url", ""),
                is_active=True,
                email_notifications_enabled=True,
                email_send_time="19:00"
            )
            
            return TokenValidationResponse(
                valid=True,
                user=user_response,
                message=None
            )
        else:
            return TokenValidationResponse(
                valid=False,
                user=None,
                message=validation_result["message"]
            )
            
    except Exception as e:
        logger.error(f"토큰 검증 중 오류 발생: {e}")
        return TokenValidationResponse(
            valid=False,
            user=None,
            message="토큰 검증 중 오류가 발생했습니다"
        )