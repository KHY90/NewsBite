"""
Users endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.core.dependencies import get_current_user, get_db_session
from app.schemas.auth import UserResponse, UserUpdateRequest
from app.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    사용자 프로필 조회
    
    - 현재 로그인한 사용자의 상세 프로필 정보 반환
    - 개인 설정 정보 포함 (알림 설정, 이메일 발송 시간 등)
    """
    try:
        user = await AuthService.get_user_by_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 프로필을 찾을 수 없습니다"
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
        logger.error(f"사용자 프로필 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 조회 중 오류가 발생했습니다"
        )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    사용자 프로필 업데이트
    
    - 표시 이름, 이메일 알림 설정, 이메일 발송 시간 등 수정 가능
    - 이메일 주소는 Supabase에서 관리되므로 변경 불가
    """
    try:
        user = await AuthService.update_user_profile(
            db, current_user["user_id"], update_data
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 프로필을 찾을 수 없습니다"
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
        logger.error(f"사용자 프로필 업데이트 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 업데이트 중 오류가 발생했습니다"
        )


@router.get("/preferences")
async def get_user_preferences(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """사용자 관심사 조회 - Phase 4에서 구현 예정"""
    # TODO: Phase 4에서 카테고리/기업 구독 정보 조회 구현
    raise HTTPException(status_code=501, detail="Phase 4에서 구현 예정")


@router.put("/preferences")
async def update_user_preferences(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """사용자 관심사 업데이트 - Phase 4에서 구현 예정"""
    # TODO: Phase 4에서 카테고리/기업 구독 정보 업데이트 구현
    raise HTTPException(status_code=501, detail="Phase 4에서 구현 예정")