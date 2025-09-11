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

from app.services.crawler import run_news_crawling
from app.services.ai_processor import process_unprocessed_news
from app.services.content_generator import generate_and_send_daily_emails
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsScheduler:
    """뉴스 수집 스케줄러"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
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
            
            # 1. 뉴스 크롤링 및 데이터베이스 저장
            crawl_result = await run_news_crawling(limit_per_category=15)
            
            if not crawl_result["success"]:
                logger.error(f"뉴스 크롤링 실패: {crawl_result.get('error')}")
                return
            
            logger.info(f"뉴스 크롤링 완료: {crawl_result['saved_count']}개 저장")
            
            # 2. AI 처리 (요약, 감정분석) - 백그라운드에서 진행
            asyncio.create_task(self._process_ai_analysis())
            
            logger.info(f"=== 뉴스 크롤링 완료 (소요시간: {crawl_result['duration_seconds']:.1f}초) ===")
            
        except Exception as e:
            logger.error(f"뉴스 크롤링 중 오류 발생: {e}")
    
    async def _process_ai_analysis(self):
        """AI 분석 처리 (요약, 감정분석)"""
        try:
            logger.info("=== AI 분석 시작 ===")
            
            # 처리되지 않은 뉴스들을 배치로 AI 처리
            result = await process_unprocessed_news(batch_size=20)
            
            if result["success"]:
                logger.info(f"=== AI 분석 완료 (처리: {result['processed_count']}개) ===")
            else:
                logger.error(f"AI 분석 실패: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"AI 분석 처리 중 오류: {e}")
    
    async def send_personalized_emails(self):
        """개인화된 뉴스 이메일 발송"""
        try:
            logger.info("=== 개인화된 이메일 발송 시작 ===")
            
            # 운영 환경에서는 모든 사용자에게, 개발 환경에서는 테스트 모드로 발송
            test_mode = settings.ENVIRONMENT == "development"
            test_limit = 5 if test_mode else None
            
            # 개인화된 뉴스 이메일 생성 및 발송
            results = await generate_and_send_daily_emails(
                test_mode=test_mode,
                test_limit=test_limit
            )
            
            logger.info(f"=== 개인화된 이메일 발송 완료 ===")
            logger.info(f"콘텐츠 생성: {results['generated']}명")
            logger.info(f"발송 성공: {results['success']}명")
            logger.info(f"발송 실패: {results['failed']}명")
            
            if test_mode:
                logger.info("⚠️ 테스트 모드로 실행됨 (최대 5명)")
            
        except Exception as e:
            logger.error(f"이메일 발송 중 오류: {e}")
    
    async def test_crawl(self):
        """테스트용 크롤링 (개발 환경에서만 실행)"""
        try:
            logger.info("=== 테스트 크롤링 시작 ===")
            
            # 소규모 테스트 크롤링
            result = await run_news_crawling(limit_per_category=5)
            
            if result["success"]:
                logger.info(f"테스트 크롤링 완료: {result['saved_count']}개 저장")
            else:
                logger.error(f"테스트 크롤링 실패: {result.get('error')}")
            
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