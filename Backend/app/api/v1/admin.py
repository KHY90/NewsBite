"""
관리자 대시보드 API 엔드포인트
시스템 통계, 사용자 관리, 뉴스 관리 등
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User
from app.models.news import News, NewsCategory
from app.models.category import Category
from app.models.company import Company
from app.models.subscription import UserCategorySubscription, UserCompanySubscription

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    관리자 대시보드 메인 통계
    """
    try:
        # 날짜 범위 설정
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # 전체 사용자 통계
        total_users = db.query(User).filter(User.is_active == True).count()
        new_users_week = db.query(User).filter(
            User.is_active == True,
            func.date(User.created_at) >= week_ago
        ).count()
        new_users_month = db.query(User).filter(
            User.is_active == True,
            func.date(User.created_at) >= month_ago
        ).count()
        
        # 이메일 구독 통계
        email_subscribers = db.query(User).filter(
            User.is_active == True,
            User.email_notifications_enabled == True
        ).count()
        
        # 뉴스 통계
        total_news = db.query(News).filter(News.is_active == True).count()
        processed_news = db.query(News).filter(
            News.is_active == True,
            News.is_processed == True
        ).count()
        
        news_today = db.query(News).filter(
            News.is_active == True,
            func.date(News.created_at) == today
        ).count()
        
        # 카테고리별 뉴스 분포
        category_stats = db.query(
            Category.name,
            func.count(NewsCategory.news_id).label('news_count')
        ).join(NewsCategory).join(News).filter(
            News.is_active == True,
            func.date(News.created_at) >= week_ago
        ).group_by(Category.name).all()
        
        # 인기 카테고리 (구독자 수 기준)
        popular_categories = db.query(
            Category.name,
            func.count(UserCategorySubscription.user_id).label('subscriber_count')
        ).join(UserCategorySubscription).filter(
            UserCategorySubscription.is_active == True
        ).group_by(Category.name).order_by(desc('subscriber_count')).limit(5).all()
        
        # 인기 기업 (구독자 수 기준)
        popular_companies = db.query(
            Company.name,
            func.count(UserCompanySubscription.user_id).label('subscriber_count')
        ).join(UserCompanySubscription).filter(
            UserCompanySubscription.is_active == True
        ).group_by(Company.name).order_by(desc('subscriber_count')).limit(5).all()
        
        # 논쟁 뉴스 통계
        controversial_news = db.query(News).filter(
            News.is_active == True,
            News.is_controversial == True,
            func.date(News.created_at) >= week_ago
        ).count()
        
        return {
            "user_stats": {
                "total_users": total_users,
                "new_users_week": new_users_week,
                "new_users_month": new_users_month,
                "email_subscribers": email_subscribers,
                "subscription_rate": round(email_subscribers / max(total_users, 1) * 100, 1)
            },
            "news_stats": {
                "total_news": total_news,
                "processed_news": processed_news,
                "processing_rate": round(processed_news / max(total_news, 1) * 100, 1),
                "news_today": news_today,
                "controversial_news_week": controversial_news
            },
            "category_distribution": [
                {"name": cat.name, "count": cat.news_count} 
                for cat in category_stats
            ],
            "popular_categories": [
                {"name": cat.name, "subscribers": cat.subscriber_count}
                for cat in popular_categories
            ],
            "popular_companies": [
                {"name": comp.name, "subscribers": comp.subscriber_count}
                for comp in popular_companies
            ],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 조회 실패: {str(e)}")


@router.get("/users", response_model=Dict[str, Any])
async def get_users_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    사용자 목록 조회 (페이지네이션, 검색)
    """
    try:
        # 기본 쿼리
        query = db.query(User).filter(User.is_active == True)
        
        # 검색 조건
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                User.email.ilike(search_pattern) |
                User.name.ilike(search_pattern)
            )
        
        # 전체 개수
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * size
        users = query.order_by(desc(User.created_at)).offset(offset).limit(size).all()
        
        # 사용자별 구독 정보 추가
        users_data = []
        for user in users:
            # 구독 통계
            category_count = db.query(UserCategorySubscription).filter(
                UserCategorySubscription.user_id == user.id,
                UserCategorySubscription.is_active == True
            ).count()
            
            company_count = db.query(UserCompanySubscription).filter(
                UserCompanySubscription.user_id == user.id,
                UserCompanySubscription.is_active == True
            ).count()
            
            users_data.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "email_notifications_enabled": user.email_notifications_enabled,
                "email_send_time": user.email_send_time,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "subscribed_categories": category_count,
                "subscribed_companies": company_count
            })
        
        return {
            "users": users_data,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 목록 조회 실패: {str(e)}")


@router.get("/users/stats", response_model=Dict[str, Any])
async def get_user_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    사용자 가입 통계 (차트용)
    """
    try:
        # 날짜 범위 설정
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 일별 가입자 수
        daily_signups = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('signups')
        ).filter(
            User.is_active == True,
            func.date(User.created_at) >= start_date
        ).group_by(func.date(User.created_at)).order_by('date').all()
        
        # 누적 사용자 수
        cumulative_data = []
        total = 0
        for signup in daily_signups:
            total += signup.signups
            cumulative_data.append({
                "date": signup.date.isoformat(),
                "daily_signups": signup.signups,
                "total_users": total
            })
        
        # 이메일 구독률 추이
        email_subscription_rate = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('total_users'),
            func.sum(func.cast(User.email_notifications_enabled, db.Integer)).label('subscribers')
        ).filter(
            User.is_active == True,
            func.date(User.created_at) >= start_date
        ).group_by(func.date(User.created_at)).order_by('date').all()
        
        subscription_rate_data = []
        for rate in email_subscription_rate:
            rate_percentage = (rate.subscribers / max(rate.total_users, 1)) * 100
            subscription_rate_data.append({
                "date": rate.date.isoformat(),
                "rate": round(rate_percentage, 1)
            })
        
        return {
            "daily_signups": cumulative_data,
            "subscription_rate_trend": subscription_rate_data,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 통계 조회 실패: {str(e)}")


@router.get("/news", response_model=Dict[str, Any])
async def get_news_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
    controversial: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    뉴스 목록 조회 (필터링, 페이지네이션)
    """
    try:
        # 기본 쿼리
        query = db.query(News).filter(News.is_active == True)
        
        # 필터링
        if processed is not None:
            query = query.filter(News.is_processed == processed)
        
        if controversial is not None:
            query = query.filter(News.is_controversial == controversial)
        
        if category:
            query = query.join(NewsCategory).join(Category).filter(
                Category.name == category
            )
        
        # 전체 개수
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * size
        news_list = query.order_by(desc(News.published_at)).offset(offset).limit(size).all()
        
        # 뉴스 데이터 구성
        news_data = []
        for news in news_list:
            # 카테고리 조회
            categories = db.query(Category.name).join(NewsCategory).filter(
                NewsCategory.news_id == news.id
            ).all()
            
            news_data.append({
                "id": news.id,
                "title": news.title,
                "summary": news.summary,
                "source_name": news.source_name,
                "source_url": news.source_url,
                "published_at": news.published_at.isoformat(),
                "created_at": news.created_at.isoformat(),
                "is_processed": news.is_processed,
                "is_controversial": news.is_controversial,
                "sentiment_label": news.sentiment_label,
                "sentiment_score": news.sentiment_score,
                "categories": [cat.name for cat in categories],
                "mentioned_companies": news.mentioned_companies
            })
        
        return {
            "news": news_data,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            },
            "filters": {
                "category": category,
                "processed": processed,
                "controversial": controversial
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 목록 조회 실패: {str(e)}")


@router.get("/news/stats", response_model=Dict[str, Any])
async def get_news_stats(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    뉴스 처리 통계
    """
    try:
        # 날짜 범위 설정
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 일별 뉴스 수집 통계
        daily_news = db.query(
            func.date(News.created_at).label('date'),
            func.count(News.id).label('total'),
            func.sum(func.cast(News.is_processed, db.Integer)).label('processed'),
            func.sum(func.cast(News.is_controversial, db.Integer)).label('controversial')
        ).filter(
            News.is_active == True,
            func.date(News.created_at) >= start_date
        ).group_by(func.date(News.created_at)).order_by('date').all()
        
        daily_stats = []
        for stat in daily_news:
            processing_rate = (stat.processed / max(stat.total, 1)) * 100
            controversial_rate = (stat.controversial / max(stat.total, 1)) * 100
            
            daily_stats.append({
                "date": stat.date.isoformat(),
                "total_news": stat.total,
                "processed_news": stat.processed,
                "controversial_news": stat.controversial,
                "processing_rate": round(processing_rate, 1),
                "controversial_rate": round(controversial_rate, 1)
            })
        
        # 카테고리별 뉴스 분포
        category_distribution = db.query(
            Category.name,
            func.count(NewsCategory.news_id).label('count')
        ).join(NewsCategory).join(News).filter(
            News.is_active == True,
            func.date(News.created_at) >= start_date
        ).group_by(Category.name).order_by(desc('count')).all()
        
        return {
            "daily_stats": daily_stats,
            "category_distribution": [
                {"category": cat.name, "count": cat.count}
                for cat in category_distribution
            ],
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 통계 조회 실패: {str(e)}")


@router.delete("/news/{news_id}")
async def delete_news(
    news_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    뉴스 삭제 (비활성화)
    """
    try:
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")
        
        news.is_active = False
        db.commit()
        
        return {"message": "뉴스가 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"뉴스 삭제 실패: {str(e)}")


@router.put("/users/{user_id}/email-notifications")
async def toggle_user_email_notifications(
    user_id: int,
    enabled: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    사용자 이메일 알림 설정 변경
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        user.email_notifications_enabled = enabled
        db.commit()
        
        return {
            "user_id": user_id,
            "email_notifications_enabled": enabled,
            "message": f"이메일 알림이 {'활성화' if enabled else '비활성화'}되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"이메일 알림 설정 변경 실패: {str(e)}")