"""
건의사항 관련 Pydantic 스키마
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.feedback import FeedbackStatus, FeedbackCategory


class FeedbackCreateRequest(BaseModel):
    """건의사항 생성 요청 스키마"""
    title: str = Field(..., min_length=1, max_length=200, description="건의사항 제목")
    content: str = Field(..., min_length=10, description="건의사항 내용")
    category: FeedbackCategory = Field(default=FeedbackCategory.OTHER, description="건의사항 카테고리")
    contact_email: Optional[str] = Field(None, description="별도 연락처 이메일 (선택사항)")


class FeedbackResponse(BaseModel):
    """건의사항 응답 스키마"""
    id: int
    title: str
    content: str
    category: FeedbackCategory
    status: FeedbackStatus
    contact_email: Optional[str] = None
    admin_response: Optional[str] = None
    responded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # 사용자 정보 (간단)
    user_email: str
    user_name: Optional[str] = None


class FeedbackUpdateRequest(BaseModel):
    """건의사항 수정 요청 스키마 (사용자용)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[FeedbackCategory] = None
    contact_email: Optional[str] = None


class AdminFeedbackResponse(BaseModel):
    """관리자 건의사항 응답 스키마"""
    admin_response: str = Field(..., min_length=1, description="관리자 응답")
    status: FeedbackStatus = Field(..., description="건의사항 상태")


class FeedbackListResponse(BaseModel):
    """건의사항 목록 응답 스키마"""
    feedbacks: list[FeedbackResponse]
    pagination: dict


class FeedbackStatsResponse(BaseModel):
    """건의사항 통계 응답 스키마"""
    total_feedbacks: int
    pending_count: int
    in_review_count: int
    resolved_count: int
    rejected_count: int
    category_distribution: list[dict]
    recent_feedbacks: list[FeedbackResponse]