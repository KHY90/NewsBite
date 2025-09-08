"""
뉴스 크롤러 테스트 스크립트
"""
import asyncio
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.news_crawler import news_crawler, NewsItem
from app.services.ai_service import ai_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def test_news_crawler():
    """뉴스 크롤러 테스트"""
    print("=== 뉴스 크롤러 테스트 시작 ===")
    
    try:
        # 정치 카테고리 뉴스 크롤링
        news_items = await news_crawler.crawl_category("정치")
        
        print(f"\n크롤링된 뉴스 수: {len(news_items)}")
        
        # 처음 3개 뉴스 출력
        for i, item in enumerate(news_items[:3]):
            print(f"\n[{i+1}] 제목: {item.title}")
            print(f"    출처: {item.source}")
            print(f"    카테고리: {item.category}")
            print(f"    URL: {item.url}")
            print(f"    요약: {item.summary[:100]}...")
            print(f"    발행시간: {item.published_at}")
        
        return news_items[:2]  # 처음 2개 반환
        
    except Exception as e:
        print(f"크롤링 테스트 오류: {e}")
        return []


async def test_ai_service(news_items):
    """AI 서비스 테스트"""
    if not news_items:
        print("테스트할 뉴스가 없습니다.")
        return
    
    print("\n=== AI 서비스 테스트 시작 ===")
    
    for i, item in enumerate(news_items):
        print(f"\n[{i+1}] 뉴스 AI 처리 중: {item.title[:50]}...")
        
        try:
            result = await ai_service.process_news_article(
                title=item.title,
                content=item.content,
                category=item.category
            )
            
            print(f"    AI 요약: {result.ai_summary}")
            print(f"    감정 분석: {result.sentiment_label} (점수: {result.sentiment_score})")
            print(f"    찬반 정리: {result.pros_and_cons or '없음'}")
            print(f"    처리 시간: {result.processing_time:.2f}초")
            
            if result.error:
                print(f"    오류: {result.error}")
                
        except Exception as e:
            print(f"    AI 처리 오류: {e}")


async def test_scheduler():
    """스케줄러 테스트"""
    print("\n=== 스케줄러 테스트 시작 ===")
    
    try:
        from app.services.scheduler import NewsScheduler
        
        scheduler = NewsScheduler()
        
        # 테스트 크롤링 실행
        await scheduler.test_crawl()
        
        print("스케줄러 테스트 완료")
        
    except Exception as e:
        print(f"스케줄러 테스트 오류: {e}")


async def main():
    """메인 테스트 함수"""
    print("NewsBite Phase 3 - 뉴스 처리 파이프라인 테스트")
    print("=" * 50)
    
    # 1. 뉴스 크롤링 테스트
    news_items = await test_news_crawler()
    
    # 2. AI 서비스 테스트  
    await test_ai_service(news_items)
    
    # 3. 스케줄러 테스트
    await test_scheduler()
    
    print("\n" + "=" * 50)
    print("모든 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())