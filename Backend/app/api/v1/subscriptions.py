"""
사용자 구독 관리 API 엔드포인트
카테고리 및 기업 구독 설정
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.category import Category
from app.models.company import Company
from app.models.subscription import UserCategorySubscription, UserCompanySubscription
from app.schemas.subscription import (
    CategorySubscriptionResponse,
    CompanySubscriptionResponse,
    SubscriptionUpdateRequest,
    UserPreferencesResponse
)

router = APIRouter()


@router.get("/categories", response_model=List[CategorySubscriptionResponse])
async def get_user_category_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[CategorySubscriptionResponse]:
    """
    사용자의 카테고리 구독 목록 조회
    """
    try:
        # 모든 카테고리와 사용자 구독 상태 조회
        categories = db.query(Category).filter(Category.is_active == True).all()
        user_subscriptions = db.query(UserCategorySubscription).filter(
            UserCategorySubscription.user_id == current_user.id,
            UserCategorySubscription.is_active == True
        ).all()
        
        # 구독 상태 매핑
        subscribed_category_ids = {sub.category_id for sub in user_subscriptions}
        
        result = []
        for category in categories:
            result.append(CategorySubscriptionResponse(
                category_id=category.id,
                category_name=category.name,
                category_description=category.description,
                is_subscribed=category.id in subscribed_category_ids
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리 구독 조회 실패: {str(e)}")


@router.post("/categories", response_model=Dict[str, Any])
async def update_category_subscriptions(
    request: SubscriptionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    사용자의 카테고리 구독 설정 업데이트
    """
    try:
        # 기존 구독 삭제
        db.query(UserCategorySubscription).filter(
            UserCategorySubscription.user_id == current_user.id
        ).delete()
        
        # 새 구독 추가
        added_count = 0
        for category_id in request.category_ids:
            # 카테고리 존재 확인
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                continue
                
            subscription = UserCategorySubscription(
                user_id=current_user.id,
                category_id=category_id,
                is_active=True
            )
            db.add(subscription)
            added_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{added_count}개 카테고리 구독이 업데이트되었습니다",
            "subscribed_categories": added_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"카테고리 구독 업데이트 실패: {str(e)}")


@router.get("/companies", response_model=List[CompanySubscriptionResponse])
async def get_user_company_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[CompanySubscriptionResponse]:
    """
    사용자의 기업 구독 목록 조회
    """
    try:
        # 모든 기업과 사용자 구독 상태 조회
        companies = db.query(Company).filter(Company.is_active == True).all()
        user_subscriptions = db.query(UserCompanySubscription).filter(
            UserCompanySubscription.user_id == current_user.id,
            UserCompanySubscription.is_active == True
        ).all()
        
        # 구독 상태 매핑
        subscription_map = {sub.company_id: sub for sub in user_subscriptions}
        
        result = []
        for company in companies:
            subscription = subscription_map.get(company.id)
            result.append(CompanySubscriptionResponse(
                company_id=company.id,
                company_name=company.name,
                company_description=company.description,
                stock_code=company.stock_code,
                is_subscribed=subscription is not None,
                sentiment_alerts_enabled=subscription.sentiment_alerts_enabled if subscription else False
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 구독 조회 실패: {str(e)}")


@router.post("/companies", response_model=Dict[str, Any])
async def update_company_subscriptions(
    request: SubscriptionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    사용자의 기업 구독 설정 업데이트
    """
    try:
        # 기존 구독 삭제
        db.query(UserCompanySubscription).filter(
            UserCompanySubscription.user_id == current_user.id
        ).delete()
        
        # 새 구독 추가
        added_count = 0
        for company_id in request.company_ids or []:
            # 기업 존재 확인
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                continue
                
            subscription = UserCompanySubscription(
                user_id=current_user.id,
                company_id=company_id,
                is_active=True,
                sentiment_alerts_enabled=True
            )
            db.add(subscription)
            added_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{added_count}개 기업 구독이 업데이트되었습니다",
            "subscribed_companies": added_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"기업 구독 업데이트 실패: {str(e)}")


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserPreferencesResponse:
    """
    사용자의 전체 구독 설정 조회
    """
    try:
        # 카테고리 구독
        category_subscriptions = db.query(UserCategorySubscription).filter(
            UserCategorySubscription.user_id == current_user.id,
            UserCategorySubscription.is_active == True
        ).all()
        
        # 기업 구독
        company_subscriptions = db.query(UserCompanySubscription).filter(
            UserCompanySubscription.user_id == current_user.id,
            UserCompanySubscription.is_active == True
        ).all()
        
        return UserPreferencesResponse(
            user_id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            email_notifications_enabled=current_user.email_notifications_enabled,
            email_send_time=current_user.email_send_time,
            subscribed_category_ids=[sub.category_id for sub in category_subscriptions],
            subscribed_company_ids=[sub.company_id for sub in company_subscriptions],
            total_categories=len(category_subscriptions),
            total_companies=len(company_subscriptions)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 설정 조회 실패: {str(e)}")


@router.get("/personalized-news", response_model=Dict[str, Any])
async def get_personalized_news_preview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    사용자 맞춤 뉴스 미리보기
    """
    try:
        from app.services.personalization import get_personalized_news_for_user
        
        # 개인화된 뉴스 조회
        personalized_news = await get_personalized_news_for_user(
            user_id=current_user.id,
            limit=10,
            db=db
        )
        
        return personalized_news
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개인화 뉴스 조회 실패: {str(e)}")


@router.get("/email-preview", response_model=Dict[str, Any])
async def get_email_preview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    이메일 콘텐츠 미리보기
    """
    try:
        from app.services.content_generator import get_content_preview
        
        preview = await get_content_preview(
            user_id=current_user.id,
            db=db
        )
        
        if not preview:
            raise HTTPException(status_code=404, detail="미리보기 콘텐츠를 생성할 수 없습니다")
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이메일 미리보기 생성 실패: {str(e)}")


@router.post("/send-test-email", response_model=Dict[str, Any])
async def send_test_email_to_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    현재 사용자에게 테스트 이메일 발송
    """
    try:
        from app.services.content_generator import generate_user_content
        from app.services.email_service import send_daily_news_email
        
        # 사용자 콘텐츠 생성
        content = await generate_user_content(
            user_id=current_user.id,
            db=db
        )
        
        if not content:
            raise HTTPException(status_code=404, detail="이메일 콘텐츠를 생성할 수 없습니다")
        
        # 테스트 이메일 발송
        success = await send_daily_news_email(
            user_email=current_user.email,
            user_name=current_user.name or "사용자",
            personalized_data=content["news_data"]
        )
        
        if success:
            return {
                "success": True,
                "message": f"테스트 이메일이 {current_user.email}로 발송되었습니다",
                "email": current_user.email
            }
        else:
            raise HTTPException(status_code=500, detail="이메일 발송에 실패했습니다")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테스트 이메일 발송 실패: {str(e)}")


@router.delete("/categories/{category_id}")
async def unsubscribe_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    특정 카테고리 구독 해제
    """
    try:
        # 구독 삭제
        result = db.query(UserCategorySubscription).filter(
            UserCategorySubscription.user_id == current_user.id,
            UserCategorySubscription.category_id == category_id
        ).delete()
        
        if result == 0:
            raise HTTPException(status_code=404, detail="구독하지 않은 카테고리입니다")
        
        db.commit()
        return {"message": "카테고리 구독이 해제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"구독 해제 실패: {str(e)}")


@router.delete("/companies/{company_id}")
async def unsubscribe_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    특정 기업 구독 해제
    """
    try:
        # 구독 삭제
        result = db.query(UserCompanySubscription).filter(
            UserCompanySubscription.user_id == current_user.id,
            UserCompanySubscription.company_id == company_id
        ).delete()
        
        if result == 0:
            raise HTTPException(status_code=404, detail="구독하지 않은 기업입니다")
        
        db.commit()
        return {"message": "기업 구독이 해제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"구독 해제 실패: {str(e)}")