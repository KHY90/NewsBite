"""
개인화된 뉴스 콘텐츠 생성 서비스
사용자별 맞춤형 뉴스 데이터 생성 및 최적화
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.personalization import get_personalized_news_for_user
from app.services.email_service import send_daily_news_email

logger = logging.getLogger(__name__)


class ContentGenerator:
    """개인화된 뉴스 콘텐츠 생성기"""
    
    def __init__(self):
        pass
    
    async def generate_user_content(
        self,
        user_id: int,
        db: Session = None
    ) -> Optional[Dict[str, Any]]:
        """
        단일 사용자를 위한 개인화된 뉴스 콘텐츠 생성
        
        Args:
            user_id: 사용자 ID
            db: 데이터베이스 세션
            
        Returns:
            개인화된 뉴스 데이터 또는 None
        """
        if not db:
            db = next(get_db())
        
        try:
            # 사용자 정보 조회
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"사용자를 찾을 수 없습니다: {user_id}")
                return None
            
            # 이메일 알림이 비활성화된 사용자 건너뛰기
            if not user.email_notifications_enabled:
                logger.info(f"이메일 알림 비활성화 사용자 건너뛰기: {user.email}")
                return None
            
            # 개인화된 뉴스 조회
            personalized_data = await get_personalized_news_for_user(
                user_id=user_id,
                limit=20,  # 충분한 뉴스 수집
                days=1,    # 최근 1일
                db=db
            )
            
            # 에러 처리
            if "error" in personalized_data:
                logger.error(f"개인화 뉴스 조회 실패 (user_id: {user_id}): {personalized_data['error']}")
                return None
            
            # 뉴스가 없는 경우
            if personalized_data.get("total_news", 0) == 0:
                logger.warning(f"사용자 {user_id}에 대한 개인화 뉴스가 없습니다")
                return None
            
            # 콘텐츠 최적화
            optimized_content = await self._optimize_content(personalized_data, user)
            
            return {
                "user_id": user_id,
                "user_email": user.email,
                "user_name": user.name or "사용자",
                "news_data": optimized_content,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"사용자 콘텐츠 생성 실패 (user_id: {user_id}): {e}")
            return None
    
    async def _optimize_content(
        self, 
        personalized_data: Dict[str, Any], 
        user: User
    ) -> Dict[str, Any]:
        """
        뉴스 콘텐츠 최적화
        - 카테고리별 뉴스 개수 조정
        - 중요도에 따른 정렬
        - 이메일 길이 최적화
        """
        try:
            optimized = personalized_data.copy()
            
            # 카테고리별 뉴스 개수 제한 (최대 3개씩)
            if "news_by_category" in optimized:
                for category, news_list in optimized["news_by_category"].items():
                    if len(news_list) > 3:
                        # 최신순으로 정렬 후 상위 3개만 유지
                        sorted_news = sorted(
                            news_list, 
                            key=lambda x: x.get("published_at", ""), 
                            reverse=True
                        )
                        optimized["news_by_category"][category] = sorted_news[:3]
            
            # 기업별 뉴스 개수 제한 (최대 2개씩)
            if "news_by_company" in optimized:
                for company, news_list in optimized["news_by_company"].items():
                    if len(news_list) > 2:
                        sorted_news = sorted(
                            news_list,
                            key=lambda x: x.get("published_at", ""),
                            reverse=True
                        )
                        optimized["news_by_company"][company] = sorted_news[:2]
            
            # 논쟁 이슈 제한 (최대 3개)
            if "controversial_news" in optimized:
                controversial = optimized["controversial_news"]
                if len(controversial) > 3:
                    # 최신순으로 정렬 후 상위 3개만 유지
                    sorted_controversial = sorted(
                        controversial,
                        key=lambda x: x.get("published_at", ""),
                        reverse=True
                    )
                    optimized["controversial_news"] = sorted_controversial[:3]
            
            # 총 뉴스 개수 재계산
            total_category_news = sum(
                len(news_list) 
                for news_list in optimized.get("news_by_category", {}).values()
            )
            total_company_news = sum(
                len(news_list) 
                for news_list in optimized.get("news_by_company", {}).values()
            )
            controversial_count = len(optimized.get("controversial_news", []))
            
            optimized["total_news"] = total_category_news + total_company_news + controversial_count
            
            # 사용자별 추가 최적화 (시간대 등)
            optimized = await self._apply_user_preferences(optimized, user)
            
            return optimized
            
        except Exception as e:
            logger.error(f"콘텐츠 최적화 실패: {e}")
            return personalized_data
    
    async def _apply_user_preferences(
        self, 
        content: Dict[str, Any], 
        user: User
    ) -> Dict[str, Any]:
        """사용자 선호도에 따른 추가 최적화"""
        try:
            # 사용자 이메일 발송 시간에 따른 뉴스 시간대 조정
            if user.email_send_time:
                # 여기서는 기본적으로 그대로 반환
                # 추후 시간대별 뉴스 중요도 조정 등 구현 가능
                pass
            
            return content
            
        except Exception as e:
            logger.error(f"사용자 선호도 적용 실패: {e}")
            return content
    
    async def generate_bulk_content(
        self,
        limit: Optional[int] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        모든 활성 사용자를 위한 일괄 콘텐츠 생성
        
        Args:
            limit: 처리할 사용자 수 제한 (테스트용)
            db: 데이터베이스 세션
            
        Returns:
            생성된 콘텐츠 목록
        """
        if not db:
            db = next(get_db())
        
        try:
            # 이메일 알림이 활성화된 사용자 조회
            query = db.query(User).filter(
                User.is_active == True,
                User.email_notifications_enabled == True
            )
            
            if limit:
                query = query.limit(limit)
            
            active_users = query.all()
            
            logger.info(f"일괄 콘텐츠 생성 시작 - 대상 사용자: {len(active_users)}명")
            
            generated_contents = []
            
            for user in active_users:
                try:
                    content = await self.generate_user_content(
                        user_id=user.id,
                        db=db
                    )
                    
                    if content:
                        generated_contents.append(content)
                        logger.debug(f"콘텐츠 생성 성공: {user.email}")
                    else:
                        logger.warning(f"콘텐츠 생성 실패: {user.email}")
                        
                except Exception as e:
                    logger.error(f"사용자 {user.email} 콘텐츠 생성 중 오류: {e}")
                    continue
            
            logger.info(f"일괄 콘텐츠 생성 완료 - 성공: {len(generated_contents)}명")
            return generated_contents
            
        except Exception as e:
            logger.error(f"일괄 콘텐츠 생성 실패: {e}")
            return []
    
    async def generate_and_send_daily_emails(
        self,
        test_mode: bool = False,
        test_limit: int = 5,
        db: Session = None
    ) -> Dict[str, int]:
        """
        일일 뉴스 이메일 생성 및 발송
        
        Args:
            test_mode: 테스트 모드 (제한된 사용자에게만 발송)
            test_limit: 테스트 모드에서 발송할 사용자 수
            db: 데이터베이스 세션
            
        Returns:
            발송 결과 통계
        """
        try:
            # 콘텐츠 생성
            limit = test_limit if test_mode else None
            generated_contents = await self.generate_bulk_content(limit=limit, db=db)
            
            if not generated_contents:
                logger.warning("생성된 콘텐츠가 없습니다")
                return {"success": 0, "failed": 0, "generated": 0}
            
            # 이메일 발송 준비
            recipients = []
            for content in generated_contents:
                recipients.append({
                    "email": content["user_email"],
                    "name": content["user_name"],
                    "news_data": content["news_data"]
                })
            
            # 일괄 이메일 발송
            from app.services.email_service import send_bulk_daily_news
            send_results = await send_bulk_daily_news(recipients)
            
            # 결과 통계
            results = {
                "generated": len(generated_contents),
                "success": send_results.get("success", 0),
                "failed": send_results.get("failed", 0)
            }
            
            logger.info(f"일일 이메일 발송 완료 - 생성: {results['generated']}, 성공: {results['success']}, 실패: {results['failed']}")
            
            return results
            
        except Exception as e:
            logger.error(f"일일 이메일 생성 및 발송 실패: {e}")
            return {"success": 0, "failed": 0, "generated": 0}
    
    async def get_content_preview(
        self,
        user_id: int,
        db: Session = None
    ) -> Optional[Dict[str, Any]]:
        """
        사용자의 이메일 콘텐츠 미리보기 생성
        
        Args:
            user_id: 사용자 ID
            db: 데이터베이스 세션
            
        Returns:
            미리보기 콘텐츠
        """
        try:
            content = await self.generate_user_content(user_id=user_id, db=db)
            
            if not content:
                return None
            
            # 미리보기용으로 일부 정보만 반환
            preview = {
                "user_name": content["user_name"],
                "total_news": content["news_data"].get("total_news", 0),
                "categories": list(content["news_data"].get("news_by_category", {}).keys()),
                "companies": list(content["news_data"].get("news_by_company", {}).keys()),
                "controversial_count": len(content["news_data"].get("controversial_news", [])),
                "sample_news": []
            }
            
            # 샘플 뉴스 추가 (각 카테고리에서 1개씩)
            for category, news_list in content["news_data"].get("news_by_category", {}).items():
                if news_list:
                    preview["sample_news"].append({
                        "category": category,
                        "title": news_list[0].get("title", ""),
                        "summary": news_list[0].get("summary", "")[:100] + "..."
                    })
            
            return preview
            
        except Exception as e:
            logger.error(f"콘텐츠 미리보기 생성 실패 (user_id: {user_id}): {e}")
            return None


# 전역 콘텐츠 생성기 인스턴스
content_generator = ContentGenerator()


# 편의 함수들
async def generate_user_content(user_id: int, db: Session = None) -> Optional[Dict[str, Any]]:
    """사용자 콘텐츠 생성 편의 함수"""
    return await content_generator.generate_user_content(user_id=user_id, db=db)


async def generate_bulk_content(limit: Optional[int] = None, db: Session = None) -> List[Dict[str, Any]]:
    """일괄 콘텐츠 생성 편의 함수"""
    return await content_generator.generate_bulk_content(limit=limit, db=db)


async def generate_and_send_daily_emails(
    test_mode: bool = False,
    test_limit: int = 5,
    db: Session = None
) -> Dict[str, int]:
    """일일 이메일 생성 및 발송 편의 함수"""
    return await content_generator.generate_and_send_daily_emails(
        test_mode=test_mode,
        test_limit=test_limit,
        db=db
    )


async def get_content_preview(user_id: int, db: Session = None) -> Optional[Dict[str, Any]]:
    """콘텐츠 미리보기 편의 함수"""
    return await content_generator.get_content_preview(user_id=user_id, db=db)