"""
뉴스 관련 Pydantic 스키마
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NewsBase(BaseModel):
    """뉴스 기본 스키마"""
    title: str = Field(..., description="뉴스 제목")
    source_name: str = Field(..., description="뉴스 출처")
    source_url: str = Field(..., description="원문 URL")
    published_at: datetime = Field(..., description="발행 시간")


class NewsCreate(NewsBase):
    """뉴스 생성 스키마"""
    content_snippet: Optional[str] = Field(None, description="뉴스 미리보기")
    author: Optional[str] = Field(None, description="기자명")


class NewsUpdate(BaseModel):
    """뉴스 수정 스키마"""
    title: Optional[str] = Field(None, description="뉴스 제목")
    summary: Optional[str] = Field(None, description="AI 요약")
    sentiment_score: Optional[float] = Field(None, description="감정 점수")
    sentiment_label: Optional[str] = Field(None, description="감정 라벨")
    keywords: Optional[List[str]] = Field(None, description="키워드")
    is_controversial: Optional[bool] = Field(None, description="논쟁성 여부")
    pros_summary: Optional[str] = Field(None, description="찬성 의견 요약")
    cons_summary: Optional[str] = Field(None, description="반대 의견 요약")
    mentioned_companies: Optional[List[str]] = Field(None, description="언급된 기업")


class NewsResponse(BaseModel):
    """뉴스 응답 스키마"""
    id: int
    title: str
    summary: Optional[str] = None
    content_snippet: Optional[str] = None
    source_name: str
    source_url: str
    author: Optional[str] = None
    published_at: datetime
    
    # AI 분석 결과
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    keywords: Optional[List[str]] = None
    
    # 논쟁 이슈 관련
    is_controversial: bool = False
    pros_summary: Optional[str] = None
    cons_summary: Optional[str] = None
    
    # 기업 관련
    mentioned_companies: Optional[List[str]] = None
    
    # 상태
    is_processed: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """뉴스 목록 응답 스키마"""
    news: List[NewsResponse] = Field(..., description="뉴스 목록")
    total: int = Field(..., description="총 뉴스 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")


class NewsSummaryResponse(BaseModel):
    """뉴스 요약 응답 스키마"""
    total_news: int = Field(..., description="총 뉴스 수")
    processed_news: int = Field(..., description="AI 처리된 뉴스 수")
    controversial_news: int = Field(..., description="논쟁적 뉴스 수")
    by_category: Dict[str, int] = Field(..., description="카테고리별 뉴스 수")
    by_source: Dict[str, int] = Field(..., description="소스별 뉴스 수")


class CategoryNewsResponse(BaseModel):
    """카테고리별 뉴스 응답 스키마"""
    category_name: str = Field(..., description="카테고리 이름")
    news: List[NewsResponse] = Field(..., description="뉴스 목록")
    total_count: int = Field(..., description="해당 카테고리 총 뉴스 수")


class CompanySentimentResponse(BaseModel):
    """기업 감정분석 응답 스키마"""
    company: str = Field(..., description="기업명")
    period_days: int = Field(..., description="분석 기간")
    total_news: int = Field(..., description="총 뉴스 수")
    average_sentiment: float = Field(..., description="평균 감정 점수")
    sentiment_distribution: Dict[str, int] = Field(..., description="감정 분포")


class NewsSearchRequest(BaseModel):
    """뉴스 검색 요청 스키마"""
    keyword: str = Field(..., min_length=1, description="검색 키워드")
    category: Optional[str] = Field(None, description="카테고리")
    source: Optional[str] = Field(None, description="뉴스 출처")
    date_from: Optional[datetime] = Field(None, description="시작 날짜")
    date_to: Optional[datetime] = Field(None, description="종료 날짜")
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(20, ge=1, le=100, description="페이지 크기")


# AI 처리 관련 스키마
class AIProcessingRequest(BaseModel):
    """AI 처리 요청 스키마"""
    news_ids: Optional[List[int]] = Field(None, description="처리할 뉴스 ID 목록")
    batch_size: int = Field(20, ge=1, le=100, description="배치 크기")


class AIProcessingResponse(BaseModel):
    """AI 처리 응답 스키마"""
    success: bool = Field(..., description="처리 성공 여부")
    processed_count: int = Field(..., description="처리된 뉴스 수")
    total_found: Optional[int] = Field(None, description="발견된 총 뉴스 수")
    error: Optional[str] = Field(None, description="오류 메시지")


# 크롤링 관련 스키마
class CrawlingRequest(BaseModel):
    """크롤링 요청 스키마"""
    limit_per_category: int = Field(10, ge=1, le=50, description="카테고리별 최대 뉴스 수")


class CrawlingResponse(BaseModel):
    """크롤링 응답 스키마"""
    success: bool = Field(..., description="크롤링 성공 여부")
    crawled_count: Optional[int] = Field(None, description="크롤링된 뉴스 수")
    saved_count: Optional[int] = Field(None, description="저장된 뉴스 수")
    duration_seconds: float = Field(..., description="소요 시간")
    start_time: str = Field(..., description="시작 시간")
    end_time: str = Field(..., description="종료 시간")
    error: Optional[str] = Field(None, description="오류 메시지")


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