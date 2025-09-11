"""
인증 관련 API 엔드포인트
Supabase 구글 로그인 및 사용자 정보 관리
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    현재 로그인한 사용자 정보 조회
    
    Headers:
        Authorization: Bearer {supabase_jwt_token}
    
    Returns:
        현재 사용자 정보
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    현재 사용자 정보 업데이트
    
    Args:
        user_update: 업데이트할 사용자 정보
        
    Returns:
        업데이트된 사용자 정보
    """
    # 업데이트 가능한 필드만 수정
    if user_update.name is not None:
        current_user.name = user_update.name
    
    if user_update.email_notifications_enabled is not None:
        current_user.email_notifications_enabled = user_update.email_notifications_enabled
    
    if user_update.email_send_time is not None:
        current_user.email_send_time = user_update.email_send_time
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    계정 비활성화
    
    Returns:
        성공 메시지
    """
    current_user.is_active = False
    db.commit()
    
    return {"message": "계정이 비활성화되었습니다"}


@router.get("/status")
async def auth_status(
    current_user: User = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    인증 상태 확인 (선택적)
    
    토큰이 있으면 사용자 정보, 없으면 익명 상태
    
    Returns:
        인증 상태 및 사용자 정보
    """
    if current_user:
        return {
            "authenticated": True,
            "user": UserResponse.from_orm(current_user).dict()
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }


@router.get("/health")
async def auth_health_check() -> Dict[str, str]:
    """
    인증 서비스 헬스 체크
    
    Returns:
        서비스 상태
    """
    return {"status": "healthy", "service": "auth"}