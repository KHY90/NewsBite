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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict[str, Any]:
    """
    사용자 관심사 조회
    
    - 구독중인 카테고리 목록
    - 관심 기업 목록
    - 알림 설정
    """
    try:
        from app.models.subscription import UserCategorySubscription, UserCompanySubscription
        from app.models.category import Category
        from app.models.company import Company
        from sqlalchemy import select
        
        # 카테고리 구독 정보 조회
        stmt = select(UserCategorySubscription, Category).join(
            Category, UserCategorySubscription.category_id == Category.id
        ).where(
            UserCategorySubscription.user_id == current_user["user_id"],
            UserCategorySubscription.is_active == True
        )
        
        result = await db.execute(stmt)
        category_subscriptions = result.fetchall()
        
        categories = [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "color": category.color
            }
            for subscription, category in category_subscriptions
        ]
        
        # 기업 구독 정보 조회
        stmt = select(UserCompanySubscription, Company).join(
            Company, UserCompanySubscription.company_id == Company.id
        ).where(
            UserCompanySubscription.user_id == current_user["user_id"],
            UserCompanySubscription.is_active == True
        )
        
        result = await db.execute(stmt)
        company_subscriptions = result.fetchall()
        
        companies = [
            {
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "logo_url": company.logo_url,
                "sentiment_alerts": subscription.sentiment_alerts_enabled
            }
            for subscription, company in company_subscriptions
        ]
        
        return {
            "categories": categories,
            "companies": companies,
            "total_categories": len(categories),
            "total_companies": len(companies)
        }
        
    except Exception as e:
        logger.error(f"사용자 관심사 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="관심사 조회 중 오류가 발생했습니다"
        )


@router.put("/preferences")
async def update_user_preferences(
    preferences_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict[str, str]:
    """
    사용자 관심사 업데이트
    
    Request body:
    {
        "category_ids": [1, 2, 3],  // 구독할 카테고리 ID 목록
        "company_ids": [1, 2],      // 관심 기업 ID 목록
    }
    """
    try:
        from app.models.subscription import UserCategorySubscription, UserCompanySubscription
        from sqlalchemy import select, delete
        
        user_id = current_user["user_id"]
        category_ids = preferences_data.get("category_ids", [])
        company_ids = preferences_data.get("company_ids", [])
        
        # 기존 구독 정보 삭제
        await db.execute(
            delete(UserCategorySubscription).where(
                UserCategorySubscription.user_id == user_id
            )
        )
        
        await db.execute(
            delete(UserCompanySubscription).where(
                UserCompanySubscription.user_id == user_id
            )
        )
        
        # 새 카테고리 구독 추가
        for category_id in category_ids:
            subscription = UserCategorySubscription(
                user_id=user_id,
                category_id=category_id,
                is_active=True
            )
            db.add(subscription)
        
        # 새 기업 구독 추가
        for company_id in company_ids:
            subscription = UserCompanySubscription(
                user_id=user_id,
                company_id=company_id,
                is_active=True,
                sentiment_alerts_enabled=True
            )
            db.add(subscription)
        
        await db.commit()
        
        return {
            "message": "관심사가 성공적으로 업데이트되었습니다",
            "categories_updated": len(category_ids),
            "companies_updated": len(company_ids)
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"사용자 관심사 업데이트 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="관심사 업데이트 중 오류가 발생했습니다"
        )