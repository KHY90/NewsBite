"""
뉴스 관련 Pydantic 스키마
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NewsBase(BaseModel):
    """뉴스 기본 스키마"""
    title: str = Field(..., description="뉴스 제목")
    content: str = Field(..., description="뉴스 내용")
    summary: str = Field(..., description="뉴스 요약")
    url: str = Field(..., description="원문 URL")
    source: str = Field(..., description="뉴스 출처")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    published_at: datetime = Field(..., description="발행 시간")


class NewsCreate(NewsBase):
    """뉴스 생성 스키마"""
    category_id: int = Field(..., description="카테고리 ID")


class NewsUpdate(BaseModel):
    """뉴스 수정 스키마"""
    title: Optional[str] = Field(None, description="뉴스 제목")
    content: Optional[str] = Field(None, description="뉴스 내용") 
    summary: Optional[str] = Field(None, description="뉴스 요약")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    ai_summary: Optional[str] = Field(None, description="AI 생성 요약")
    sentiment_score: Optional[float] = Field(None, description="감정 점수")
    pros_and_cons: Optional[str] = Field(None, description="찬반 정리")


class NewsResponse(NewsBase):
    """뉴스 응답 스키마"""
    id: int = Field(..., description="뉴스 ID")
    category_id: int = Field(..., description="카테고리 ID")
    category_name: Optional[str] = Field(None, description="카테고리 이름")
    view_count: int = Field(0, description="조회수")
    ai_summary: Optional[str] = Field(None, description="AI 생성 요약")
    sentiment_score: Optional[float] = Field(None, description="감정 점수")
    pros_and_cons: Optional[str] = Field(None, description="찬반 정리")
    is_processed: bool = Field(False, description="AI 처리 여부")
    processed_at: Optional[datetime] = Field(None, description="AI 처리 시간")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """뉴스 목록 응답 스키마"""
    news: List[NewsResponse] = Field(..., description="뉴스 목록")
    total: int = Field(..., description="총 뉴스 수")
    limit: int = Field(..., description="페이지 크기")
    offset: int = Field(..., description="시작 위치")


class NewsStatsResponse(BaseModel):
    """뉴스 통계 응답 스키마"""
    total_news: int = Field(..., description="총 뉴스 수")
    today_news: int = Field(..., description="오늘 뉴스 수")
    by_category: Dict[str, int] = Field(..., description="카테고리별 뉴스 수")
    by_source: Dict[str, int] = Field(..., description="소스별 뉴스 수")


class CategoryNewsResponse(BaseModel):
    """카테고리별 뉴스 응답 스키마"""
    category_name: str = Field(..., description="카테고리 이름")
    news: List[NewsResponse] = Field(..., description="뉴스 목록")
    total_count: int = Field(..., description="해당 카테고리 총 뉴스 수")


class TrendingNewsResponse(BaseModel):
    """트렌딩 뉴스 응답 스키마"""
    period_hours: int = Field(..., description="집계 기간(시간)")
    news: List[NewsResponse] = Field(..., description="트렌딩 뉴스 목록")
    updated_at: datetime = Field(..., description="마지막 업데이트 시간")


class NewsSearchRequest(BaseModel):
    """뉴스 검색 요청 스키마"""
    keyword: str = Field(..., min_length=1, description="검색 키워드")
    category_id: Optional[int] = Field(None, description="카테고리 ID")
    source: Optional[str] = Field(None, description="뉴스 출처")
    date_from: Optional[datetime] = Field(None, description="시작 날짜")
    date_to: Optional[datetime] = Field(None, description="종료 날짜")
    limit: int = Field(20, ge=1, le=100, description="조회할 뉴스 수")
    offset: int = Field(0, ge=0, description="시작 위치")


class NewsSearchResponse(BaseModel):
    """뉴스 검색 응답 스키마"""
    keyword: str = Field(..., description="검색 키워드")
    news: List[NewsResponse] = Field(..., description="검색된 뉴스 목록")
    total_count: int = Field(..., description="총 검색 결과 수")
    search_time_ms: float = Field(..., description="검색 소요 시간(밀리초)")


# AI 처리 관련 스키마
class AIProcessingRequest(BaseModel):
    """AI 처리 요청 스키마"""
    news_ids: List[int] = Field(..., description="처리할 뉴스 ID 목록")
    processing_type: str = Field(..., description="처리 유형 (summary, sentiment, pros_cons)")


class AIProcessingResponse(BaseModel):
    """AI 처리 응답 스키마"""
    processed_count: int = Field(..., description="처리된 뉴스 수")
    failed_count: int = Field(..., description="처리 실패 뉴스 수")
    processing_time_seconds: float = Field(..., description="처리 소요 시간(초)")
    results: List[Dict[str, Any]] = Field(..., description="처리 결과 상세")


# 스케줄러 관련 스키마
class SchedulerJobInfo(BaseModel):
    """스케줄러 작업 정보 스키마"""
    id: str = Field(..., description="작업 ID")
    name: str = Field(..., description="작업 이름")
    next_run_time: Optional[datetime] = Field(None, description="다음 실행 시간")


class SchedulerStatusResponse(BaseModel):
    """스케줄러 상태 응답 스키마"""
    is_running: bool = Field(..., description="스케줄러 실행 상태")
    jobs: List[SchedulerJobInfo] = Field(..., description="작업 목록")
    server_time: datetime = Field(default_factory=datetime.now, description="서버 시간")