"""
건의사항 관리 API 엔드포인트
사용자 건의사항 제출 및 관리자 응답
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User
from app.models.feedback import Feedback, FeedbackStatus, FeedbackCategory
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackResponse,
    FeedbackUpdateRequest,
    AdminFeedbackResponse,
    FeedbackListResponse,
    FeedbackStatsResponse
)

router = APIRouter()


@router.post("/", response_model=Dict[str, Any])
async def create_feedback(
    request: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    건의사항 생성
    """
    try:
        # 새 건의사항 생성
        feedback = Feedback(
            user_id=current_user.id,
            title=request.title,
            content=request.content,
            category=request.category,
            contact_email=request.contact_email,
            status=FeedbackStatus.PENDING
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return {
            "success": True,
            "message": "건의사항이 성공적으로 제출되었습니다",
            "feedback_id": feedback.id,
            "status": feedback.status.value
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"건의사항 제출 실패: {str(e)}")


@router.get("/my", response_model=List[FeedbackResponse])
async def get_my_feedbacks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[FeedbackResponse]:
    """
    내 건의사항 목록 조회
    """
    try:
        feedbacks = db.query(Feedback).filter(
            Feedback.user_id == current_user.id,
            Feedback.is_active == True
        ).order_by(desc(Feedback.created_at)).all()
        
        result = []
        for feedback in feedbacks:
            result.append(FeedbackResponse(
                id=feedback.id,
                title=feedback.title,
                content=feedback.content,
                category=feedback.category,
                status=feedback.status,
                contact_email=feedback.contact_email,
                admin_response=feedback.admin_response,
                responded_at=feedback.responded_at,
                created_at=feedback.created_at,
                updated_at=feedback.updated_at,
                user_email=current_user.email,
                user_name=current_user.name
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건의사항 조회 실패: {str(e)}")


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_detail(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FeedbackResponse:
    """
    건의사항 상세 조회
    """
    try:
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.is_active == True
        ).first()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="건의사항을 찾을 수 없습니다")
        
        # 작성자나 관리자만 조회 가능
        if feedback.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        return FeedbackResponse(
            id=feedback.id,
            title=feedback.title,
            content=feedback.content,
            category=feedback.category,
            status=feedback.status,
            contact_email=feedback.contact_email,
            admin_response=feedback.admin_response,
            responded_at=feedback.responded_at,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            user_email=feedback.user.email,
            user_name=feedback.user.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건의사항 조회 실패: {str(e)}")


@router.put("/{feedback_id}", response_model=Dict[str, Any])
async def update_feedback(
    feedback_id: int,
    request: FeedbackUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    건의사항 수정 (사용자)
    """
    try:
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.user_id == current_user.id,
            Feedback.is_active == True
        ).first()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="건의사항을 찾을 수 없습니다")
        
        # 이미 응답된 건의사항은 수정 불가
        if feedback.status != FeedbackStatus.PENDING:
            raise HTTPException(status_code=400, detail="이미 처리된 건의사항은 수정할 수 없습니다")
        
        # 수정 가능한 필드만 업데이트
        if request.title is not None:
            feedback.title = request.title
        if request.content is not None:
            feedback.content = request.content
        if request.category is not None:
            feedback.category = request.category
        if request.contact_email is not None:
            feedback.contact_email = request.contact_email
        
        db.commit()
        
        return {
            "success": True,
            "message": "건의사항이 수정되었습니다",
            "feedback_id": feedback.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"건의사항 수정 실패: {str(e)}")


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    건의사항 삭제 (비활성화)
    """
    try:
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.user_id == current_user.id,
            Feedback.is_active == True
        ).first()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="건의사항을 찾을 수 없습니다")
        
        # 이미 응답된 건의사항은 삭제 불가
        if feedback.status != FeedbackStatus.PENDING:
            raise HTTPException(status_code=400, detail="이미 처리된 건의사항은 삭제할 수 없습니다")
        
        feedback.is_active = False
        db.commit()
        
        return {"message": "건의사항이 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"건의사항 삭제 실패: {str(e)}")


# 관리자 전용 엔드포인트들
@router.get("/admin/list", response_model=FeedbackListResponse)
async def get_admin_feedbacks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[FeedbackStatus] = Query(None),
    category: Optional[FeedbackCategory] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> FeedbackListResponse:
    """
    모든 건의사항 목록 조회 (관리자)
    """
    try:
        # 기본 쿼리
        query = db.query(Feedback).filter(Feedback.is_active == True)
        
        # 필터링
        if status:
            query = query.filter(Feedback.status == status)
        if category:
            query = query.filter(Feedback.category == category)
        
        # 전체 개수
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * size
        feedbacks = query.order_by(desc(Feedback.created_at)).offset(offset).limit(size).all()
        
        # 응답 데이터 구성
        feedback_responses = []
        for feedback in feedbacks:
            feedback_responses.append(FeedbackResponse(
                id=feedback.id,
                title=feedback.title,
                content=feedback.content,
                category=feedback.category,
                status=feedback.status,
                contact_email=feedback.contact_email,
                admin_response=feedback.admin_response,
                responded_at=feedback.responded_at,
                created_at=feedback.created_at,
                updated_at=feedback.updated_at,
                user_email=feedback.user.email,
                user_name=feedback.user.name
            ))
        
        return FeedbackListResponse(
            feedbacks=feedback_responses,
            pagination={
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건의사항 목록 조회 실패: {str(e)}")


@router.post("/{feedback_id}/respond", response_model=Dict[str, Any])
async def respond_to_feedback(
    feedback_id: int,
    request: AdminFeedbackResponse,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    건의사항에 관리자 응답 (관리자)
    """
    try:
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.is_active == True
        ).first()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="건의사항을 찾을 수 없습니다")
        
        # 관리자 응답 업데이트
        feedback.admin_response = request.admin_response
        feedback.status = request.status
        feedback.admin_id = current_user.id
        feedback.responded_at = func.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "건의사항에 응답했습니다",
            "feedback_id": feedback.id,
            "status": feedback.status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"건의사항 응답 실패: {str(e)}")


@router.get("/admin/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> FeedbackStatsResponse:
    """
    건의사항 통계 (관리자)
    """
    try:
        # 전체 통계
        total_feedbacks = db.query(Feedback).filter(Feedback.is_active == True).count()
        
        # 상태별 통계
        pending_count = db.query(Feedback).filter(
            Feedback.is_active == True,
            Feedback.status == FeedbackStatus.PENDING
        ).count()
        
        in_review_count = db.query(Feedback).filter(
            Feedback.is_active == True,
            Feedback.status == FeedbackStatus.IN_REVIEW
        ).count()
        
        resolved_count = db.query(Feedback).filter(
            Feedback.is_active == True,
            Feedback.status == FeedbackStatus.RESOLVED
        ).count()
        
        rejected_count = db.query(Feedback).filter(
            Feedback.is_active == True,
            Feedback.status == FeedbackStatus.REJECTED
        ).count()
        
        # 카테고리별 분포
        category_distribution = db.query(
            Feedback.category,
            func.count(Feedback.id).label('count')
        ).filter(
            Feedback.is_active == True
        ).group_by(Feedback.category).all()
        
        category_data = [
            {"category": cat.category.value, "count": cat.count}
            for cat in category_distribution
        ]
        
        # 최근 건의사항
        recent_feedbacks = db.query(Feedback).filter(
            Feedback.is_active == True
        ).order_by(desc(Feedback.created_at)).limit(5).all()
        
        recent_data = []
        for feedback in recent_feedbacks:
            recent_data.append(FeedbackResponse(
                id=feedback.id,
                title=feedback.title,
                content=feedback.content[:100] + "..." if len(feedback.content) > 100 else feedback.content,
                category=feedback.category,
                status=feedback.status,
                contact_email=feedback.contact_email,
                admin_response=feedback.admin_response,
                responded_at=feedback.responded_at,
                created_at=feedback.created_at,
                updated_at=feedback.updated_at,
                user_email=feedback.user.email,
                user_name=feedback.user.name
            ))
        
        return FeedbackStatsResponse(
            total_feedbacks=total_feedbacks,
            pending_count=pending_count,
            in_review_count=in_review_count,
            resolved_count=resolved_count,
            rejected_count=rejected_count,
            category_distribution=category_data,
            recent_feedbacks=recent_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건의사항 통계 조회 실패: {str(e)}")