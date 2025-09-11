"""
Supabase 구글 인증 시스템
JWT 토큰 검증 및 사용자 인증 미들웨어
"""
import jwt
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


class SupabaseAuth:
    """Supabase JWT 토큰 검증 및 인증 관리"""
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.service_key = settings.SUPABASE_SERVICE_KEY
        self.security = HTTPBearer()
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Supabase JWT 토큰 검증
        
        Args:
            token: JWT 토큰 문자열
            
        Returns:
            토큰 payload (사용자 정보)
            
        Raises:
            HTTPException: 토큰이 유효하지 않은 경우
        """
        try:
            # Supabase JWT 시크릿 키로 토큰 디코딩
            # 실제로는 Supabase에서 공개키를 가져와야 함
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,  # 환경변수에 추가 필요
                algorithms=["HS256"],
                audience="authenticated"
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="토큰이 만료되었습니다"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="유효하지 않은 토큰입니다"
            )
    
    async def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        토큰에서 사용자 정보 추출
        
        Args:
            token: JWT 토큰
            
        Returns:
            사용자 정보 딕셔너리
        """
        payload = await self.verify_token(token)
        
        # Supabase 사용자 정보 API 호출
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": self.supabase_key
            }
            
            response = await client.get(
                f"{self.supabase_url}/auth/v1/user",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=401,
                    detail="사용자 정보를 가져올 수 없습니다"
                )
    
    async def create_or_update_user(
        self, 
        db: Session, 
        supabase_user: Dict[str, Any]
    ) -> User:
        """
        Supabase 사용자 정보로 로컬 DB 사용자 생성 또는 업데이트
        
        Args:
            db: 데이터베이스 세션
            supabase_user: Supabase에서 가져온 사용자 정보
            
        Returns:
            User 모델 인스턴스
        """
        user_id = supabase_user["id"]
        email = supabase_user["email"]
        
        # 기존 사용자 확인
        existing_user = db.query(User).filter(User.supabase_id == user_id).first()
        
        if existing_user:
            # 기존 사용자 정보 업데이트
            existing_user.email = email
            existing_user.name = supabase_user.get("user_metadata", {}).get("name", email)
            existing_user.avatar_url = supabase_user.get("user_metadata", {}).get("avatar_url")
            existing_user.last_login = supabase_user.get("last_sign_in_at")
            
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # 새 사용자 생성
            new_user = User(
                supabase_id=user_id,
                email=email,
                name=supabase_user.get("user_metadata", {}).get("name", email),
                avatar_url=supabase_user.get("user_metadata", {}).get("avatar_url"),
                last_login=supabase_user.get("last_sign_in_at")
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user


# 전역 인증 인스턴스
supabase_auth = SupabaseAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 정보 반환
    
    FastAPI Dependency로 사용
    인증이 필요한 엔드포인트에서 사용
    
    Args:
        credentials: HTTP Bearer 토큰
        db: 데이터베이스 세션
        
    Returns:
        현재 사용자 User 모델
        
    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials
    
    try:
        # Supabase에서 사용자 정보 가져오기
        supabase_user = await supabase_auth.get_user_from_token(token)
        
        # 로컬 DB에 사용자 생성/업데이트
        user = await supabase_auth.create_or_update_user(db, supabase_user)
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"인증에 실패했습니다: {str(e)}"
        )


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적 사용자 인증 (토큰이 없어도 None 반환)
    
    공개 API에서 사용자가 로그인한 경우 추가 정보 제공 시 사용
    
    Args:
        request: FastAPI Request 객체
        db: 데이터베이스 세션
        
    Returns:
        User 모델 또는 None
    """
    authorization = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    
    try:
        supabase_user = await supabase_auth.get_user_from_token(token)
        user = await supabase_auth.create_or_update_user(db, supabase_user)
        return user
    except:
        return None


# 관리자 권한 확인
async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    관리자 권한 확인
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        관리자 사용자
        
    Raises:
        HTTPException: 관리자가 아닌 경우
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="관리자 권한이 필요합니다"
        )
    
    return current_user


# 관리자 권한 확인 (편의 함수)
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    관리자 권한 필요 (get_admin_user와 동일)
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        관리자 사용자
        
    Raises:
        HTTPException: 관리자가 아닌 경우
    """
    return await get_admin_user(current_user)