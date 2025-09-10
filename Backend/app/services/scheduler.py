# 이 파일은 APScheduler를 사용하여 주기적인 작업을 자동화하는 스케줄러를 정의합니다.
# 정해진 시간에 뉴스 크롤링, AI 처리, 이메일 발송 등의 작업을 실행하는 역할을 합니다.
# FastAPI 애플리케이션의 라이프사이클과 연동되어 앱 시작 시 스케줄러가 실행되고,
# 종료 시 안전하게 중지됩니다.
#
# - `NewsScheduler` 클래스: 스케줄링 로직을 관리합니다.
#   - `start`/`stop`: 스케줄러를 시작하고 중지합니다.
#   - `crawl_and_process_news`: 매일 정해진 시간(18:00)에 뉴스 크롤링, 중복 제거,
#                               데이터베이스 저장, AI 분석 시작 등의 전체 파이프라인을 실행합니다.
#   - `send_personalized_emails`: (구현 예정) 매일 정해진 시간(19:00)에 사용자에게
#                                 맞춤 뉴스 이메일을 발송하는 작업을 수행합니다.
# - 개발 환경에서는 10분마다 테스트 크롤링을 실행하는 디버깅용 작업이 추가됩니다.

"""
뉴스 수집 스케줄러
APScheduler를 이용한 자동 뉴스 크롤링 (18:00-18:30)
"""
import asyncio
import logging
from datetime import datetime, time
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.news_crawler import news_crawler, NewsItem
from app.services.news_service import NewsService
from app.services.ai_service import ai_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsScheduler:
    """뉴스 수집 스케줄러"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.news_service = NewsService()
        self.is_running = False
    
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return
        
        # 매일 18:00에 뉴스 크롤링 시작
        self.scheduler.add_job(
            self.crawl_and_process_news,
            CronTrigger(hour=18, minute=0),  # 18:00
            id='news_crawling',
            name='뉴스 크롤링 및 처리',
            replace_existing=True
        )
        
        # 매일 19:00에 이메일 발송
        self.scheduler.add_job(
            self.send_personalized_emails,
            CronTrigger(hour=19, minute=0),  # 19:00
            id='email_sending',
            name='개인화된 뉴스 이메일 발송',
            replace_existing=True
        )
        
        # 테스트용: 매 10분마다 실행 (개발 중에만 사용)
        if settings.ENVIRONMENT == "development":
            self.scheduler.add_job(
                self.test_crawl,
                CronTrigger(minute='*/10'),  # 매 10분
                id='test_crawling',
                name='테스트 크롤링',
                replace_existing=True
            )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("뉴스 스케줄러가 시작되었습니다.")
        logger.info("뉴스 크롤링: 매일 18:00")
        logger.info("이메일 발송: 매일 19:00")
        
        if settings.ENVIRONMENT == "development":
            logger.info("테스트 크롤링: 매 10분")
    
    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            logger.warning("스케줄러가 실행되지 않았습니다.")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("뉴스 스케줄러가 중지되었습니다.")
    
    async def crawl_and_process_news(self):
        """뉴스 크롤링 및 AI 처리"""
        try:
            logger.info("=== 뉴스 크롤링 시작 ===")
            start_time = datetime.now()
            
            # 1. 뉴스 크롤링
            categories = ["정치", "경제", "사회", "IT/과학", "세계"]
            news_items = await news_crawler.crawl_all_categories(categories)
            
            if not news_items:
                logger.warning("크롤링된 뉴스가 없습니다.")
                return
            
            logger.info(f"{len(news_items)}개의 뉴스 기사를 수집했습니다.")
            
            # 2. 중복 제거
            unique_news = await self._remove_duplicates(news_items)
            logger.info(f"중복 제거 후 {len(unique_news)}개의 뉴스 기사")
            
            # 3. 데이터베이스 저장 (AI 처리 전)
            saved_count = 0
            for news_item in unique_news:
                try:
                    # 뉴스 기사를 데이터베이스에 저장
                    await self.news_service.create_news_article(news_item)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"뉴스 저장 오류: {e}")
                    continue
            
            logger.info(f"{saved_count}개의 뉴스 기사가 데이터베이스에 저장되었습니다.")
            
            # 4. AI 처리 (요약, 감정분석) - 백그라운드에서 진행
            asyncio.create_task(self._process_ai_analysis(unique_news))
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"=== 뉴스 크롤링 완료 (소요시간: {duration:.1f}초) ===")
            
        except Exception as e:
            logger.error(f"뉴스 크롤링 중 오류 발생: {e}")
    
    async def _remove_duplicates(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """중복 뉴스 제거"""
        seen_titles = set()
        unique_news = []
        
        for news_item in news_items:
            # 제목 기반 중복 체크 (간단한 버전)
            title_key = news_item.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news_item)
        
        return unique_news
    
    async def _process_ai_analysis(self, news_items: List[NewsItem]):
        """AI 분석 처리 (요약, 감정분석)"""
        try:
            logger.info("=== AI 분석 시작 ===")
            
            processed_count = 0
            failed_count = 0
            
            # 동시 처리 수 제한 (API 레이트 리밋 고려)
            semaphore = asyncio.Semaphore(2)
            
            async def process_single_item(news_item: NewsItem):
                async with semaphore:
                    try:
                        # AI 처리
                        result = await ai_service.process_news_article(
                            title=news_item.title,
                            content=news_item.content,
                            category=news_item.category
                        )
                        
                        if not result.error:
                            # 데이터베이스 업데이트 (임시 - 추후 news_service에 메서드 추가)
                            return {
                                'title': news_item.title,
                                'ai_summary': result.ai_summary,
                                'sentiment_score': result.sentiment_score,
                                'pros_and_cons': result.pros_and_cons,
                                'success': True
                            }
                        else:
                            logger.error(f"AI 처리 실패 - {news_item.title}: {result.error}")
                            return {'title': news_item.title, 'success': False}
                            
                    except Exception as e:
                        logger.error(f"AI 분석 오류 - {news_item.title}: {e}")
                        return {'title': news_item.title, 'success': False}
            
            # 모든 뉴스 아이템을 병렬 처리 (제한된 동시성)
            tasks = [process_single_item(item) for item in news_items[:20]]  # 최대 20개까지만
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 집계
            for result in results:
                if isinstance(result, dict) and result.get('success'):
                    processed_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"=== AI 분석 완료 (성공: {processed_count}, 실패: {failed_count}) ===")
            
        except Exception as e:
            logger.error(f"AI 분석 처리 중 오류: {e}")
    
    async def send_personalized_emails(self):
        """개인화된 뉴스 이메일 발송"""
        try:
            logger.info("=== 개인화된 이메일 발송 시작 ===")
            
            # 사용자별 개인화된 뉴스 이메일 생성 및 발송 (추후 구현)
            # users = await self.user_service.get_active_users()
            # for user in users:
            #     personalized_news = await self.news_service.get_personalized_news(user.id)
            #     await self.email_service.send_news_email(user.email, personalized_news)
            
            logger.info("=== 개인화된 이메일 발송 완료 ===")
            
        except Exception as e:
            logger.error(f"이메일 발송 중 오류: {e}")
    
    async def test_crawl(self):
        """테스트용 크롤링 (개발 환경에서만 실행)"""
        try:
            logger.info("=== 테스트 크롤링 시작 ===")
            
            # 테스트용으로 정치 카테고리만 크롤링
            news_items = await news_crawler.crawl_category("정치")
            logger.info(f"테스트 크롤링: {len(news_items)}개 기사 수집")
            
            # 첫 번째 기사 정보 출력
            if news_items:
                first_news = news_items[0]
                logger.info(f"첫 번째 기사: {first_news.title[:50]}...")
            
        except Exception as e:
            logger.error(f"테스트 크롤링 오류: {e}")
    
    def get_next_run_times(self):
        """다음 실행 시간 조회"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time
            })
        return jobs_info


# 전역 스케줄러 인스턴스
news_scheduler = NewsScheduler()


async def start_scheduler():
    """스케줄러 시작 (FastAPI 시작 시 호출)"""
    news_scheduler.start()


async def stop_scheduler():
    """스케줄러 중지 (FastAPI 종료 시 호출)"""
    news_scheduler.stop()


if __name__ == "__main__":
    """테스트용 실행"""
    async def test():
        logging.basicConfig(level=logging.INFO)
        
        scheduler = NewsScheduler()
        scheduler.start()
        
        # 즉시 테스트 실행
        await scheduler.test_crawl()
        
        # 스케줄 정보 출력
        jobs = scheduler.get_next_run_times()
        for job in jobs:
            print(f"작업: {job['name']}, 다음 실행: {job['next_run_time']}")
        
        # 10초 후 종료
        await asyncio.sleep(10)
        scheduler.stop()
    
    asyncio.run(test())