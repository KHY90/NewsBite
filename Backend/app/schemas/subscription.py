"""
사용자 구독 관련 Pydantic 스키마
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CategorySubscriptionResponse(BaseModel):
    """카테고리 구독 응답 스키마"""
    category_id: int
    category_name: str
    category_description: Optional[str] = None
    is_subscribed: bool


class CompanySubscriptionResponse(BaseModel):
    """기업 구독 응답 스키마"""
    company_id: int
    company_name: str
    company_description: Optional[str] = None
    stock_code: Optional[str] = None
    is_subscribed: bool
    sentiment_alerts_enabled: bool = False


class SubscriptionUpdateRequest(BaseModel):
    """구독 업데이트 요청 스키마"""
    category_ids: Optional[List[int]] = Field(None, description="구독할 카테고리 ID 목록")
    company_ids: Optional[List[int]] = Field(None, description="구독할 기업 ID 목록")


class UserPreferencesResponse(BaseModel):
    """사용자 전체 설정 응답 스키마"""
    user_id: int
    email: str
    name: Optional[str] = None
    email_notifications_enabled: bool
    email_send_time: str
    subscribed_category_ids: List[int]
    subscribed_company_ids: List[int]
    total_categories: int
    total_companies: int


class PersonalizedNewsItem(BaseModel):
    """개인화 뉴스 아이템 스키마"""
    id: int
    title: str
    summary: Optional[str] = None
    source_name: str
    source_url: str
    published_at: datetime
    category_name: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    mentioned_companies: Optional[List[str]] = None
    is_controversial: bool = False
    pros_summary: Optional[str] = None
    cons_summary: Optional[str] = None


class PersonalizedNewsResponse(BaseModel):
    """개인화 뉴스 응답 스키마"""
    user_id: int
    total_news: int
    news_by_category: dict
    news_by_company: dict
    controversial_news: List[PersonalizedNewsItem]
    generated_at: datetime