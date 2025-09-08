"""
뉴스 서비스
뉴스 데이터 관리 및 비즈니스 로직
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.news import News
from app.models.category import Category
from app.models.company import Company
from app.services.news_crawler import NewsItem
from app.core.database import get_db_session


class NewsService:
    """뉴스 서비스 클래스"""
    
    def __init__(self):
        pass
    
    async def create_news_article(self, news_item: NewsItem) -> Optional[News]:
        """뉴스 기사 생성"""
        try:
            async with get_db_session() as db:
                # 중복 체크 (제목 기반)
                existing = db.query(News).filter(
                    News.title == news_item.title
                ).first()
                
                if existing:
                    return existing
                
                # 카테고리 찾기 또는 생성
                category = db.query(Category).filter(
                    Category.name == news_item.category
                ).first()
                
                if not category:
                    category = Category(
                        name=news_item.category,
                        description=f"{news_item.category} 카테고리"
                    )
                    db.add(category)
                    db.commit()
                    db.refresh(category)
                
                # 뉴스 기사 생성
                news_article = News(
                    title=news_item.title,
                    content=news_item.content,
                    summary=news_item.summary,
                    url=news_item.url,
                    source=news_item.source,
                    thumbnail_url=news_item.thumbnail_url,
                    published_at=news_item.published_at,
                    category_id=category.id,
                    created_at=datetime.now(),
                    is_processed=False,  # AI 처리 전
                    view_count=0
                )
                
                db.add(news_article)
                db.commit()
                db.refresh(news_article)
                
                return news_article
                
        except Exception as e:
            print(f"뉴스 기사 생성 오류: {e}")
            return None
    
    async def get_recent_news(self, 
                            category_id: Optional[int] = None,
                            limit: int = 20,
                            offset: int = 0) -> List[News]:
        """최근 뉴스 조회"""
        try:
            async with get_db_session() as db:
                query = db.query(News)
                
                if category_id:
                    query = query.filter(News.category_id == category_id)
                
                news_list = query.order_by(desc(News.published_at))\
                                .offset(offset)\
                                .limit(limit)\
                                .all()
                
                return news_list
                
        except Exception as e:
            print(f"최근 뉴스 조회 오류: {e}")
            return []
    
    async def get_news_by_category(self, category_name: str, limit: int = 10) -> List[News]:
        """카테고리별 뉴스 조회"""
        try:
            async with get_db_session() as db:
                news_list = db.query(News)\
                             .join(Category)\
                             .filter(Category.name == category_name)\
                             .order_by(desc(News.published_at))\
                             .limit(limit)\
                             .all()
                
                return news_list
                
        except Exception as e:
            print(f"카테고리별 뉴스 조회 오류: {e}")
            return []
    
    async def get_trending_news(self, hours: int = 24, limit: int = 10) -> List[News]:
        """트렌딩 뉴스 조회 (조회수 기준)"""
        try:
            async with get_db_session() as db:
                since = datetime.now() - timedelta(hours=hours)
                
                news_list = db.query(News)\
                             .filter(News.published_at >= since)\
                             .order_by(desc(News.view_count), desc(News.published_at))\
                             .limit(limit)\
                             .all()
                
                return news_list
                
        except Exception as e:
            print(f"트렌딩 뉴스 조회 오류: {e}")
            return []
    
    async def search_news(self, 
                         keyword: str, 
                         category_id: Optional[int] = None,
                         limit: int = 20) -> List[News]:
        """뉴스 검색"""
        try:
            async with get_db_session() as db:
                query = db.query(News)
                
                # 제목 또는 내용에서 키워드 검색
                search_filter = or_(
                    News.title.contains(keyword),
                    News.content.contains(keyword),
                    News.summary.contains(keyword)
                )
                query = query.filter(search_filter)
                
                if category_id:
                    query = query.filter(News.category_id == category_id)
                
                news_list = query.order_by(desc(News.published_at))\
                                .limit(limit)\
                                .all()
                
                return news_list
                
        except Exception as e:
            print(f"뉴스 검색 오류: {e}")
            return []
    
    async def get_personalized_news(self, user_id: int) -> List[News]:
        """개인화된 뉴스 조회"""
        try:
            # TODO: 사용자 관심사 기반 개인화 로직 구현
            # 현재는 최근 뉴스 반환
            return await self.get_recent_news(limit=10)
            
        except Exception as e:
            print(f"개인화된 뉴스 조회 오류: {e}")
            return []
    
    async def increment_view_count(self, news_id: int) -> bool:
        """뉴스 조회수 증가"""
        try:
            async with get_db_session() as db:
                news = db.query(News).filter(News.id == news_id).first()
                if news:
                    news.view_count += 1
                    db.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"조회수 증가 오류: {e}")
            return False
    
    async def get_news_statistics(self) -> Dict:
        """뉴스 통계 조회"""
        try:
            async with get_db_session() as db:
                # 총 뉴스 수
                total_news = db.query(News).count()
                
                # 오늘 뉴스 수
                today = datetime.now().date()
                today_news = db.query(News)\
                               .filter(News.published_at >= today)\
                               .count()
                
                # 카테고리별 뉴스 수
                category_stats = db.query(Category.name, db.func.count(News.id))\
                                  .join(News)\
                                  .group_by(Category.name)\
                                  .all()
                
                # 소스별 뉴스 수
                source_stats = db.query(News.source, db.func.count(News.id))\
                                .group_by(News.source)\
                                .all()
                
                return {
                    "total_news": total_news,
                    "today_news": today_news,
                    "by_category": dict(category_stats),
                    "by_source": dict(source_stats)
                }
                
        except Exception as e:
            print(f"뉴스 통계 조회 오류: {e}")
            return {}
    
    async def mark_as_processed(self, news_id: int) -> bool:
        """AI 처리 완료 표시"""
        try:
            async with get_db_session() as db:
                news = db.query(News).filter(News.id == news_id).first()
                if news:
                    news.is_processed = True
                    news.processed_at = datetime.now()
                    db.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"처리 완료 표시 오류: {e}")
            return False
    
    async def get_unprocessed_news(self, limit: int = 50) -> List[News]:
        """미처리 뉴스 조회 (AI 처리 대기 중)"""
        try:
            async with get_db_session() as db:
                news_list = db.query(News)\
                             .filter(News.is_processed == False)\
                             .order_by(News.created_at)\
                             .limit(limit)\
                             .all()
                
                return news_list
                
        except Exception as e:
            print(f"미처리 뉴스 조회 오류: {e}")
            return []


# 뉴스 서비스 인스턴스
news_service = NewsService()