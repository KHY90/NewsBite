"""
뉴스 관련 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.news_service import news_service
from app.schemas.news import NewsResponse, NewsListResponse, NewsStatsResponse
from app.models.news import News

router = APIRouter()


@router.get("/", response_model=NewsListResponse)
async def get_news(
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    limit: int = Query(20, ge=1, le=100, description="조회할 뉴스 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
) -> NewsListResponse:
    """최근 뉴스 목록 조회"""
    try:
        news_list = await news_service.get_recent_news(
            category_id=category_id,
            limit=limit,
            offset=offset
        )
        
        return NewsListResponse(
            news=[NewsResponse.from_orm(news) for news in news_list],
            total=len(news_list),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 실패: {str(e)}")


@router.get("/trending", response_model=List[NewsResponse])
async def get_trending_news(
    hours: int = Query(24, ge=1, le=168, description="시간 범위"),
    limit: int = Query(10, ge=1, le=50, description="조회할 뉴스 수")
) -> List[NewsResponse]:
    """트렌딩 뉴스 조회"""
    try:
        news_list = await news_service.get_trending_news(hours=hours, limit=limit)
        return [NewsResponse.from_orm(news) for news in news_list]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트렌딩 뉴스 조회 실패: {str(e)}")


@router.get("/category/{category_name}", response_model=List[NewsResponse])
async def get_news_by_category(
    category_name: str,
    limit: int = Query(10, ge=1, le=50, description="조회할 뉴스 수")
) -> List[NewsResponse]:
    """카테고리별 뉴스 조회"""
    try:
        news_list = await news_service.get_news_by_category(
            category_name=category_name,
            limit=limit
        )
        return [NewsResponse.from_orm(news) for news in news_list]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리별 뉴스 조회 실패: {str(e)}")


@router.get("/search", response_model=List[NewsResponse])
async def search_news(
    q: str = Query(..., min_length=1, description="검색 키워드"),
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    limit: int = Query(20, ge=1, le=100, description="조회할 뉴스 수")
) -> List[NewsResponse]:
    """뉴스 검색"""
    try:
        news_list = await news_service.search_news(
            keyword=q,
            category_id=category_id,
            limit=limit
        )
        return [NewsResponse.from_orm(news) for news in news_list]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 검색 실패: {str(e)}")


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(news_id: int) -> NewsResponse:
    """뉴스 상세 조회"""
    try:
        # 조회수 증가
        await news_service.increment_view_count(news_id)
        
        # TODO: 개별 뉴스 조회 메서드 구현 필요
        news_list = await news_service.get_recent_news(limit=1000)  # 임시 구현
        news = next((n for n in news_list if n.id == news_id), None)
        
        if not news:
            raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다.")
        
        return NewsResponse.from_orm(news)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 실패: {str(e)}")


@router.get("/stats/overview", response_model=NewsStatsResponse)
async def get_news_statistics() -> NewsStatsResponse:
    """뉴스 통계 조회"""
    try:
        stats = await news_service.get_news_statistics()
        return NewsStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@router.post("/crawl/trigger")
async def trigger_news_crawl():
    """뉴스 크롤링 수동 실행 (관리자용)"""
    try:
        # TODO: 관리자 권한 확인
        
        from app.services.scheduler import news_scheduler
        await news_scheduler.crawl_and_process_news()
        
        return {"message": "뉴스 크롤링이 시작되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"크롤링 실행 실패: {str(e)}")


@router.get("/scheduler/status")
async def get_scheduler_status():
    """스케줄러 상태 조회"""
    try:
        from app.services.scheduler import news_scheduler
        jobs = news_scheduler.get_next_run_times()
        
        return {
            "is_running": news_scheduler.is_running,
            "jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스케줄러 상태 조회 실패: {str(e)}")


@router.get("/companies/{company_name}")
async def get_company_news(company_name: str) -> List[NewsResponse]:
    """기업별 뉴스 조회"""
    try:
        # TODO: 기업별 뉴스 조회 로직 구현 (Phase 4에서)
        raise HTTPException(status_code=501, detail="기업별 뉴스 기능은 Phase 4에서 구현 예정")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업별 뉴스 조회 실패: {str(e)}")