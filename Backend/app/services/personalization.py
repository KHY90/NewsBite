"""
개인화 뉴스 필터링 서비스
사용자 관심사에 따른 맞춤형 뉴스 제공
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.news import News, NewsCategory
from app.models.category import Category
from app.models.company import Company
from app.models.subscription import UserCategorySubscription, UserCompanySubscription
from app.schemas.subscription import PersonalizedNewsItem

logger = logging.getLogger(__name__)


class PersonalizationService:
    """개인화 뉴스 서비스"""
    
    def __init__(self):
        pass
    
    async def get_personalized_news_for_user(
        self, 
        user_id: int, 
        limit: int = 20, 
        days: int = 1,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        사용자 맞춤형 뉴스 조회
        
        Args:
            user_id: 사용자 ID
            limit: 최대 뉴스 수
            days: 조회 기간 (일)
            db: 데이터베이스 세션
            
        Returns:
            개인화된 뉴스 데이터
        """
        if not db:
            db = next(get_db())
        
        try:
            # 사용자 정보 조회
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "사용자를 찾을 수 없습니다"}
            
            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 사용자 구독 정보 조회
            category_subscriptions = db.query(UserCategorySubscription).filter(
                UserCategorySubscription.user_id == user_id,
                UserCategorySubscription.is_active == True
            ).all()
            
            company_subscriptions = db.query(UserCompanySubscription).filter(
                UserCompanySubscription.user_id == user_id,
                UserCompanySubscription.is_active == True
            ).all()
            
            subscribed_category_ids = [sub.category_id for sub in category_subscriptions]
            subscribed_company_ids = [sub.company_id for sub in company_subscriptions]
            
            # 구독한 기업명 조회
            subscribed_company_names = []
            if subscribed_company_ids:
                companies = db.query(Company).filter(
                    Company.id.in_(subscribed_company_ids)
                ).all()
                subscribed_company_names = [company.name for company in companies]
            
            # 개인화된 뉴스 조회
            personalized_news = await self._get_filtered_news(
                db=db,
                category_ids=subscribed_category_ids,
                company_names=subscribed_company_names,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # 카테고리별 분류
            news_by_category = await self._group_news_by_category(
                db=db, 
                news_list=personalized_news
            )
            
            # 기업별 분류
            news_by_company = await self._group_news_by_company(
                news_list=personalized_news,
                company_names=subscribed_company_names
            )
            
            # 논쟁 이슈 별도 추출
            controversial_news = [
                news for news in personalized_news 
                if news.get('is_controversial', False)
            ]
            
            return {
                "user_id": user_id,
                "total_news": len(personalized_news),
                "news_by_category": news_by_category,
                "news_by_company": news_by_company,
                "controversial_news": controversial_news[:5],  # 최대 5개
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"개인화 뉴스 조회 실패 (user_id: {user_id}): {e}")
            return {"error": str(e)}
    
    async def _get_filtered_news(
        self,
        db: Session,
        category_ids: List[int],
        company_names: List[str],
        start_date: datetime,
        end_date: datetime,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        필터링된 뉴스 조회
        """
        # 기본 뉴스 쿼리
        query = db.query(News).filter(
            News.is_active == True,
            News.is_processed == True,
            News.published_at >= start_date,
            News.published_at <= end_date
        )
        
        # 카테고리 또는 기업 필터
        filters = []
        
        # 카테고리 필터
        if category_ids:
            category_filter = query.join(NewsCategory).filter(
                NewsCategory.category_id.in_(category_ids)
            ).exists()
            filters.append(category_filter)
        
        # 기업 필터
        if company_names:
            company_conditions = []
            for company_name in company_names:
                company_conditions.append(
                    News.mentioned_companies.any(company_name)
                )
            if company_conditions:
                filters.append(or_(*company_conditions))
        
        # 필터 적용
        if filters:
            query = query.filter(or_(*filters))
        
        # 정렬 및 제한
        news_list = query.order_by(desc(News.published_at)).limit(limit).all()
        
        # 딕셔너리로 변환
        result = []
        for news in news_list:
            result.append({
                "id": news.id,
                "title": news.title,
                "summary": news.summary,
                "source_name": news.source_name,
                "source_url": news.source_url,
                "published_at": news.published_at.isoformat(),
                "sentiment_score": news.sentiment_score,
                "sentiment_label": news.sentiment_label,
                "keywords": news.keywords,
                "mentioned_companies": news.mentioned_companies,
                "is_controversial": news.is_controversial,
                "pros_summary": news.pros_summary,
                "cons_summary": news.cons_summary
            })
        
        return result
    
    async def _group_news_by_category(
        self, 
        db: Session, 
        news_list: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        뉴스를 카테고리별로 그룹화
        """
        result = {}
        
        for news in news_list:
            # 뉴스의 카테고리 조회
            news_categories = db.query(Category).join(NewsCategory).filter(
                NewsCategory.news_id == news["id"]
            ).all()
            
            for category in news_categories:
                if category.name not in result:
                    result[category.name] = []
                result[category.name].append(news)
        
        return result
    
    async def _group_news_by_company(
        self,
        news_list: List[Dict[str, Any]],
        company_names: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        뉴스를 기업별로 그룹화
        """
        result = {}
        
        for company_name in company_names:
            result[company_name] = []
        
        for news in news_list:
            mentioned_companies = news.get("mentioned_companies", [])
            if mentioned_companies:
                for company in mentioned_companies:
                    if company in company_names:
                        if company not in result:
                            result[company] = []
                        result[company].append(news)
        
        return result
    
    async def get_trending_news(
        self,
        db: Session,
        hours: int = 24,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        트렌딩 뉴스 조회 (조회수, 논쟁성 기준)
        """
        try:
            # 시간 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)
            
            # 트렌딩 뉴스 조회 (논쟁적 뉴스 우선, 최신순)
            trending_news = db.query(News).filter(
                News.is_active == True,
                News.is_processed == True,
                News.published_at >= start_date
            ).order_by(
                desc(News.is_controversial),
                desc(News.published_at)
            ).limit(limit).all()
            
            result = []
            for news in trending_news:
                result.append({
                    "id": news.id,
                    "title": news.title,
                    "summary": news.summary,
                    "source_name": news.source_name,
                    "source_url": news.source_url,
                    "published_at": news.published_at.isoformat(),
                    "sentiment_score": news.sentiment_score,
                    "sentiment_label": news.sentiment_label,
                    "is_controversial": news.is_controversial,
                    "mentioned_companies": news.mentioned_companies
                })
            
            return result
            
        except Exception as e:
            logger.error(f"트렌딩 뉴스 조회 실패: {e}")
            return []


# 전역 서비스 인스턴스
personalization_service = PersonalizationService()


# 편의 함수
async def get_personalized_news_for_user(
    user_id: int, 
    limit: int = 20, 
    days: int = 1,
    db: Session = None
) -> Dict[str, Any]:
    """사용자 개인화 뉴스 조회 편의 함수"""
    return await personalization_service.get_personalized_news_for_user(
        user_id=user_id,
        limit=limit,
        days=days,
        db=db
    )


async def get_trending_news(
    hours: int = 24,
    limit: int = 10,
    db: Session = None
) -> List[Dict[str, Any]]:
    """트렌딩 뉴스 조회 편의 함수"""
    if not db:
        db = next(get_db())
    
    return await personalization_service.get_trending_news(
        db=db,
        hours=hours,
        limit=limit
    )