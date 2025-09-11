"""
User 관련 Pydantic 스키마
API 입력/출력 데이터 구조 정의
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """사용자 기본 정보 스키마"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    supabase_id: str = Field(..., description="Supabase 사용자 ID")
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 스키마"""
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")
    email_notifications_enabled: Optional[bool] = Field(None, description="이메일 알림 활성화")
    email_send_time: Optional[str] = Field(
        None, 
        regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$',
        description="이메일 발송 시간 (HH:MM 형식)"
    )


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    supabase_id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # 사용자 설정
    is_active: bool
    is_admin: bool
    email_notifications_enabled: bool
    email_send_time: str
    
    # 메타 정보
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Pydantic v2에서 orm_mode 대신 사용


class UserList(BaseModel):
    """사용자 목록 응답 스키마"""
    users: list[UserResponse]
    total: int
    page: int
    size: int


class UserStats(BaseModel):
    """사용자 통계 스키마 (관리자용)"""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int