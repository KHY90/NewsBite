"""
뉴스 관련 API 엔드포인트
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.news import News, NewsCategory
from app.models.category import Category
from app.services.crawler import run_news_crawling
from app.services.ai_processor import process_unprocessed_news
from app.schemas.news import NewsResponse, NewsListResponse, NewsSummaryResponse

router = APIRouter()


@router.get("/", response_model=NewsListResponse)
async def get_news_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    search: Optional[str] = Query(None, description="검색 키워드"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> NewsListResponse:
    """
    뉴스 목록 조회
    
    Query Parameters:
        page: 페이지 번호 (기본값: 1)
        size: 페이지 크기 (기본값: 20, 최대: 100)
        category: 카테고리 필터
        search: 검색 키워드
        start_date: 시작 날짜
        end_date: 종료 날짜
    """
    try:
        # 기본 쿼리
        query = db.query(News).filter(News.is_active == True)
        
        # 카테고리 필터
        if category:
            query = query.join(NewsCategory).join(Category).filter(
                Category.name == category
            )
        
        # 검색 키워드
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                News.title.ilike(search_filter) | 
                News.summary.ilike(search_filter)
            )
        
        # 날짜 범위 필터
        if start_date:
            query = query.filter(News.published_at >= start_date)
        if end_date:
            query = query.filter(News.published_at <= end_date)
        
        # 전체 개수
        total = query.count()
        
        # 페이징 및 정렬
        offset = (page - 1) * size
        news_list = query.order_by(desc(News.published_at)).offset(offset).limit(size).all()
        
        # 응답 생성
        news_responses = [NewsResponse.from_orm(news) for news in news_list]
        
        return NewsListResponse(
            news=news_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 목록 조회 실패: {str(e)}")


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> NewsResponse:
    """
    뉴스 상세 조회
    
    Path Parameters:
        news_id: 뉴스 ID
    """
    news = db.query(News).filter(
        News.id == news_id,
        News.is_active == True
    ).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")
    
    return NewsResponse.from_orm(news)


@router.get("/categories/{category_name}", response_model=NewsListResponse)
async def get_news_by_category(
    category_name: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> NewsListResponse:
    """
    카테고리별 뉴스 조회
    
    Path Parameters:
        category_name: 카테고리명
    """
    try:
        # 카테고리 존재 확인
        category = db.query(Category).filter(Category.name == category_name).first()
        if not category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        
        # 뉴스 조회
        query = db.query(News).join(NewsCategory).filter(
            NewsCategory.category_id == category.id,
            News.is_active == True
        )
        
        total = query.count()
        offset = (page - 1) * size
        news_list = query.order_by(desc(News.published_at)).offset(offset).limit(size).all()
        
        news_responses = [NewsResponse.from_orm(news) for news in news_list]
        
        return NewsListResponse(
            news=news_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리 뉴스 조회 실패: {str(e)}")


@router.get("/companies/{company_name}", response_model=NewsListResponse)
async def get_news_by_company(
    company_name: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> NewsListResponse:
    """
    기업별 뉴스 조회
    
    Path Parameters:
        company_name: 기업명
        
    Query Parameters:
        days: 조회 기간 (기본값: 30일)
    """
    try:
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 기업 관련 뉴스 조회
        query = db.query(News).filter(
            News.mentioned_companies.any(company_name),
            News.is_active == True,
            News.published_at >= start_date,
            News.published_at <= end_date
        )
        
        total = query.count()
        offset = (page - 1) * size
        news_list = query.order_by(desc(News.published_at)).offset(offset).limit(size).all()
        
        news_responses = [NewsResponse.from_orm(news) for news in news_list]
        
        return NewsListResponse(
            news=news_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 뉴스 조회 실패: {str(e)}")


@router.get("/sentiment/{company_name}", response_model=Dict[str, Any])
async def get_company_sentiment_analysis(
    company_name: str,
    days: int = Query(30, ge=1, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    기업 감정분석 결과 조회
    
    Path Parameters:
        company_name: 기업명
        
    Query Parameters:
        days: 분석 기간 (기본값: 30일)
    """
    try:
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 기업 관련 뉴스의 감정분석 결과 조회
        sentiment_stats = db.query(
            func.count(News.id).label('total_count'),
            func.avg(News.sentiment_score).label('avg_sentiment'),
            func.count(News.id).filter(News.sentiment_label == 'positive').label('positive_count'),
            func.count(News.id).filter(News.sentiment_label == 'negative').label('negative_count'),
            func.count(News.id).filter(News.sentiment_label == 'neutral').label('neutral_count')
        ).filter(
            News.mentioned_companies.any(company_name),
            News.is_active == True,
            News.is_processed == True,
            News.published_at >= start_date,
            News.published_at <= end_date
        ).first()
        
        if not sentiment_stats or sentiment_stats.total_count == 0:
            return {
                "company": company_name,
                "period_days": days,
                "total_news": 0,
                "average_sentiment": 0.0,
                "sentiment_distribution": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0
                },
                "message": "분석할 뉴스가 없습니다"
            }
        
        return {
            "company": company_name,
            "period_days": days,
            "total_news": sentiment_stats.total_count,
            "average_sentiment": round(float(sentiment_stats.avg_sentiment or 0), 3),
            "sentiment_distribution": {
                "positive": sentiment_stats.positive_count,
                "negative": sentiment_stats.negative_count,
                "neutral": sentiment_stats.neutral_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정분석 조회 실패: {str(e)}")


@router.get("/controversial/", response_model=NewsListResponse)
async def get_controversial_news(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30, description="조회 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> NewsListResponse:
    """
    논쟁적 이슈 뉴스 조회
    
    Query Parameters:
        days: 조회 기간 (기본값: 7일)
    """
    try:
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 논쟁적 뉴스 조회
        query = db.query(News).filter(
            News.is_controversial == True,
            News.is_active == True,
            News.published_at >= start_date,
            News.published_at <= end_date
        )
        
        total = query.count()
        offset = (page - 1) * size
        news_list = query.order_by(desc(News.published_at)).offset(offset).limit(size).all()
        
        news_responses = [NewsResponse.from_orm(news) for news in news_list]
        
        return NewsListResponse(
            news=news_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"논쟁 뉴스 조회 실패: {str(e)}")


@router.post("/crawl", response_model=Dict[str, Any])
async def trigger_news_crawling(
    limit_per_category: int = Query(10, ge=1, le=50, description="카테고리별 최대 뉴스 수"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    수동 뉴스 크롤링 실행 (인증 필요)
    
    Query Parameters:
        limit_per_category: 카테고리별 최대 뉴스 수 (기본값: 10)
    """
    try:
        # 크롤링 실행
        result = await run_news_crawling(limit_per_category)
        
        # AI 처리도 함께 실행
        if result["success"] and result["saved_count"] > 0:
            ai_result = await process_unprocessed_news(batch_size=result["saved_count"])
            result["ai_processing"] = ai_result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 크롤링 실패: {str(e)}")


@router.post("/process-ai", response_model=Dict[str, Any])
async def trigger_ai_processing(
    batch_size: int = Query(20, ge=1, le=100, description="배치 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    수동 AI 처리 실행 (인증 필요)
    
    Query Parameters:
        batch_size: 배치 크기 (기본값: 20)
    """
    try:
        result = await process_unprocessed_news(batch_size)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 처리 실패: {str(e)}")


@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_news_summary_stats(
    days: int = Query(7, ge=1, le=30, description="통계 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    뉴스 통계 요약
    
    Query Parameters:
        days: 통계 기간 (기본값: 7일)
    """
    try:
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 기본 통계
        total_news = db.query(News).filter(
            News.published_at >= start_date,
            News.published_at <= end_date,
            News.is_active == True
        ).count()
        
        processed_news = db.query(News).filter(
            News.published_at >= start_date,
            News.published_at <= end_date,
            News.is_active == True,
            News.is_processed == True
        ).count()
        
        controversial_news = db.query(News).filter(
            News.published_at >= start_date,
            News.published_at <= end_date,
            News.is_active == True,
            News.is_controversial == True
        ).count()
        
        return {
            "period_days": days,
            "total_news": total_news,
            "processed_news": processed_news,
            "controversial_news": controversial_news,
            "processing_rate": round(processed_news / total_news * 100, 1) if total_news > 0 else 0,
            "controversy_rate": round(controversial_news / total_news * 100, 1) if total_news > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")