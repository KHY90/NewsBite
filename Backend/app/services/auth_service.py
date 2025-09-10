# 이 파일은 사용자 인증과 관련된 핵심 비즈니스 로직을 처리하는 서비스 계층입니다.
# API 엔드포인트로부터의 요청을 받아 실제 인증 과정을 수행하고,
# 데이터베이스와 상호작용하여 사용자 정보를 관리합니다.
#
# - `AuthService` 클래스: 인증 관련 로직을 정적 메소드로 그룹화합니다.
#   - `authenticate_with_google`: Google OAuth 토큰을 받아 Supabase에 인증을 요청하고,
#                                 성공 시 JWT 토큰과 사용자 정보를 반환합니다.
#   - `get_or_create_user`: Supabase로부터 받은 사용자 정보를 기반으로 로컬 데이터베이스에
#                           사용자가 없으면 새로 생성하고, 있으면 정보를 업데이트합니다.
#   - `validate_token`: 클라이언트로부터 받은 JWT 토큰의 유효성을 검증합니다.
#   - `update_user_profile`: 사용자의 프로필 정보를 데이터베이스에서 업데이트합니다.

"""
인증 서비스 계층
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdateRequest
from app.utils.supabase_client import supabase_client, supabase_admin_client
from app.utils.auth import verify_supabase_token, AuthError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """인증 관련 비즈니스 로직"""
    
    @staticmethod
    async def authenticate_with_google(access_token: str) -> Dict[str, Any]:
        """
        구글 OAuth 토큰으로 Supabase 인증
        
        Args:
            access_token: 구글 OAuth Access Token
            
        Returns:
            인증 결과 (Supabase 토큰 포함)
            
        Raises:
            AuthError: 인증 실패 시
        """
        try:
            # Supabase를 통한 구글 OAuth 인증
            response = supabase_client.auth.sign_in_with_oauth_credentials(
                {
                    "provider": "google",
                    "access_token": access_token
                }
            )
            
            if not response.user or not response.session:
                raise AuthError("구글 인증에 실패했습니다")
            
            return {
                "access_token": response.session.access_token,
                "token_type": "bearer",
                "expires_in": response.session.expires_in,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "display_name": response.user.user_metadata.get("full_name", ""),
                    "avatar_url": response.user.user_metadata.get("avatar_url", ""),
                    "email_confirmed": response.user.email_confirmed_at is not None
                }
            }
            
        except Exception as e:
            logger.error(f"구글 인증 중 오류 발생: {e}")
            raise AuthError("인증 처리 중 오류가 발생했습니다")
    
    @staticmethod
    async def get_or_create_user(
        db: AsyncSession, 
        supabase_user: Dict[str, Any]
    ) -> User:
        """
        Supabase 사용자 정보로 로컬 사용자 가져오기 또는 생성
        
        Args:
            db: 데이터베이스 세션
            supabase_user: Supabase 사용자 정보
            
        Returns:
            User 모델 인스턴스
        """
        try:
            supabase_id = supabase_user["user_id"]
            
            # 기존 사용자 조회
            result = await db.execute(
                select(User).where(User.supabase_id == supabase_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # 기존 사용자 정보 업데이트
                user.last_login_at = datetime.utcnow()
                user.email = supabase_user["email"]
                
                # 프로필 정보 업데이트 (변경된 경우만)
                user_metadata = supabase_user.get("user_metadata", {})
                if user_metadata.get("full_name"):
                    user.display_name = user_metadata["full_name"]
                if user_metadata.get("avatar_url"):
                    user.avatar_url = user_metadata["avatar_url"]
                    
            else:
                # 새 사용자 생성
                user_metadata = supabase_user.get("user_metadata", {})
                user = User(
                    supabase_id=supabase_id,
                    email=supabase_user["email"],
                    display_name=user_metadata.get("full_name", ""),
                    avatar_url=user_metadata.get("avatar_url", ""),
                    is_active=True,
                    email_notifications_enabled=True,
                    last_login_at=datetime.utcnow()
                )
                db.add(user)
            
            await db.commit()
            await db.refresh(user)
            return user
            
        except Exception as e:
            logger.error(f"사용자 생성/업데이트 중 오류 발생: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def validate_token(token: str) -> Dict[str, Any]:
        """
        JWT 토큰 유효성 검증
        
        Args:
            token: JWT 토큰
            
        Returns:
            검증 결과
        """
        try:
            user_info = verify_supabase_token(token)
            return {
                "valid": True,
                "user": user_info,
                "message": None
            }
        except AuthError as e:
            return {
                "valid": False,
                "user": None,
                "message": str(e)
            }
    
    @staticmethod
    async def logout_user(token: str) -> bool:
        """
        사용자 로그아웃 (토큰 무효화)
        
        Args:
            token: JWT 토큰
            
        Returns:
            로그아웃 성공 여부
        """
        try:
            # Supabase 세션 종료
            supabase_client.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"로그아웃 중 오류 발생: {e}")
            return False
    
    @staticmethod
    async def update_user_profile(
        db: AsyncSession,
        user_id: str,
        update_data: UserUpdateRequest
    ) -> Optional[User]:
        """
        사용자 프로필 업데이트
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            update_data: 업데이트할 데이터
            
        Returns:
            업데이트된 User 모델 또는 None
        """
        try:
            # 사용자 조회
            result = await db.execute(
                select(User).where(User.supabase_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # 업데이트 적용
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(user)
            return user
            
        except Exception as e:
            logger.error(f"사용자 프로필 업데이트 중 오류 발생: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            User 모델 또는 None
        """
        try:
            result = await db.execute(
                select(User).where(User.supabase_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"사용자 조회 중 오류 발생: {e}")
            return None