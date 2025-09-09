"""
Authentication related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class GoogleLoginRequest(BaseModel):
    """구글 로그인 요청 스키마"""
    access_token: str = Field(..., description="구글 OAuth Access Token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "google_oauth_token_here"
            }
        }

class LoginResponse(BaseModel):
    """로그인 응답 스키마"""
    access_token: str = Field(..., description="Supabase JWT 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: Optional[int] = Field(None, description="토큰 만료 시간(초)")
    user: "UserResponse" = Field(..., description="사용자 정보")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "jwt.token.here",
                "token_type": "bearer", 
                "expires_in": 3600,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "display_name": "홍길동",
                    "avatar_url": "https://example.com/avatar.jpg"
                }
            }
        }

class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: str = Field(..., description="사용자 ID")
    supabase_id: Optional[str] = Field(None, description="Supabase 사용자 ID")
    email: EmailStr = Field(..., description="이메일 주소")
    display_name: Optional[str] = Field(None, description="표시 이름")
    avatar_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    is_active: bool = Field(True, description="활성 상태")
    email_notifications_enabled: bool = Field(True, description="이메일 알림 허용")
    email_send_time: str = Field("19:00", description="이메일 발송 시간")
    created_at: Optional[datetime] = Field(None, description="가입 일시")
    last_login_at: Optional[datetime] = Field(None, description="마지막 로그인 일시")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "supabase_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "display_name": "홍길동",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "email_notifications_enabled": True,
                "email_send_time": "19:00",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login_at": "2024-01-01T12:00:00Z"
            }
        }

class UserUpdateRequest(BaseModel):
    """사용자 정보 수정 요청 스키마"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100, description="표시 이름")
    email_notifications_enabled: Optional[bool] = Field(None, description="이메일 알림 허용")
    email_send_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="이메일 발송 시간 (HH:MM)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "display_name": "김뉴스",
                "email_notifications_enabled": True,
                "email_send_time": "18:30"
            }
        }

class TokenValidationRequest(BaseModel):
    """토큰 검증 요청 스키마"""
    token: str = Field(..., description="검증할 JWT 토큰")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "jwt.token.here"
            }
        }

class TokenValidationResponse(BaseModel):
    """토큰 검증 응답 스키마"""
    valid: bool = Field(..., description="토큰 유효성")
    user: Optional[UserResponse] = Field(None, description="사용자 정보 (유효한 경우)")
    message: Optional[str] = Field(None, description="에러 메시지 (유효하지 않은 경우)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "display_name": "홍길동"
                },
                "message": None
            }
        }

class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""
    message: str = Field(..., description="로그아웃 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "성공적으로 로그아웃되었습니다"
            }
        }

class AuthErrorResponse(BaseModel):
    """인증 오류 응답 스키마"""
    detail: str = Field(..., description="오류 메시지")
    error_code: Optional[str] = Field(None, description="오류 코드")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "유효하지 않은 토큰입니다",
                "error_code": "INVALID_TOKEN"
            }
        }

# Forward reference 해결
LoginResponse.model_rebuild()