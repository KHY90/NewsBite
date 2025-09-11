"""
뉴스 크롤링 서비스
Playwright를 사용한 주요 뉴스 사이트 크롤링
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re

from playwright.async_api import async_playwright, Browser, Page
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.news import News
from app.models.category import Category
from app.services.ai_processor import AIProcessor

logger = logging.getLogger(__name__)


class NewsSource:
    """뉴스 소스 설정 클래스"""
    def __init__(
        self, 
        name: str, 
        base_url: str, 
        category_urls: Dict[str, str],
        selectors: Dict[str, str]
    ):
        self.name = name
        self.base_url = base_url
        self.category_urls = category_urls
        self.selectors = selectors


class NewsCrawler:
    """뉴스 크롤링 메인 클래스"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.ai_processor = AIProcessor()
        
        # 주요 뉴스 사이트 설정
        self.news_sources = [
            NewsSource(
                name="연합뉴스",
                base_url="https://www.yna.co.kr",
                category_urls={
                    "정치": "/politics/all",
                    "경제": "/economy/all", 
                    "사회": "/society/all",
                    "과학기술": "/science/all",
                    "국제": "/international/all"
                },
                selectors={
                    "article_list": ".news-con .item-box01",
                    "title": ".news-tl",
                    "summary": ".news-sm",
                    "link": ".news-tl a",
                    "time": ".txt-time",
                    "content": ".story-news .article"
                }
            ),
            NewsSource(
                name="KBS뉴스",
                base_url="https://news.kbs.co.kr",
                category_urls={
                    "정치": "/news/pc/view/politics",
                    "경제": "/news/pc/view/economy",
                    "사회": "/news/pc/view/society", 
                    "과학기술": "/news/pc/view/digital",
                    "국제": "/news/pc/view/world"
                },
                selectors={
                    "article_list": ".list-news li",
                    "title": ".news-title",
                    "summary": ".news-text",
                    "link": ".news-title a",
                    "time": ".date",
                    "content": ".detail-body"
                }
            )
        ]
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.browser:
            await self.browser.close()
    
    async def crawl_category(
        self, 
        source: NewsSource, 
        category: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        특정 카테고리의 뉴스 크롤링
        
        Args:
            source: 뉴스 소스 정보
            category: 카테고리명
            limit: 최대 수집 뉴스 수
            
        Returns:
            뉴스 데이터 리스트
        """
        if category not in source.category_urls:
            logger.warning(f"{source.name}에서 '{category}' 카테고리를 찾을 수 없습니다")
            return []
        
        page = await self.browser.new_page()
        
        try:
            url = urljoin(source.base_url, source.category_urls[category])
            logger.info(f"크롤링 시작: {source.name} - {category} ({url})")
            
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(2000)  # 2초 대기
            
            # 뉴스 목록 추출
            articles = await page.query_selector_all(source.selectors["article_list"])
            news_data = []
            
            for i, article in enumerate(articles[:limit]):
                try:
                    # 제목 추출
                    title_element = await article.query_selector(source.selectors["title"])
                    if not title_element:
                        continue
                        
                    title = await title_element.inner_text()
                    title = title.strip()
                    
                    # 링크 추출
                    link_element = await article.query_selector(source.selectors["link"])
                    if not link_element:
                        continue
                        
                    link = await link_element.get_attribute("href")
                    if link and not link.startswith("http"):
                        link = urljoin(source.base_url, link)
                    
                    # 요약/미리보기 텍스트
                    summary_element = await article.query_selector(source.selectors.get("summary"))
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                        summary = summary.strip()
                    
                    # 시간 정보
                    time_element = await article.query_selector(source.selectors.get("time"))
                    published_time = None
                    if time_element:
                        time_text = await time_element.inner_text()
                        published_time = self._parse_time(time_text)
                    
                    if not published_time:
                        published_time = datetime.now()
                    
                    news_item = {
                        "title": title,
                        "source_name": source.name,
                        "source_url": link,
                        "content_snippet": summary,
                        "published_at": published_time,
                        "category": category,
                        "raw_content": None  # 본문은 별도로 크롤링
                    }
                    
                    news_data.append(news_item)
                    logger.debug(f"뉴스 수집: {title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"개별 뉴스 처리 중 오류: {e}")
                    continue
            
            logger.info(f"{source.name} - {category}: {len(news_data)}개 뉴스 수집 완료")
            return news_data
            
        except Exception as e:
            logger.error(f"{source.name} - {category} 크롤링 오류: {e}")
            return []
        
        finally:
            await page.close()
    
    async def crawl_article_content(self, url: str, source: NewsSource) -> Optional[str]:
        """
        개별 뉴스 기사 본문 크롤링
        
        Args:
            url: 기사 URL
            source: 뉴스 소스 정보
            
        Returns:
            기사 본문 텍스트
        """
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(1000)
            
            # 본문 추출
            content_element = await page.query_selector(source.selectors.get("content"))
            if content_element:
                content = await content_element.inner_text()
                return content.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"본문 크롤링 오류 ({url}): {e}")
            return None
            
        finally:
            await page.close()
    
    async def crawl_all_categories(self, limit_per_category: int = 10) -> List[Dict[str, Any]]:
        """
        모든 소스의 모든 카테고리에서 뉴스 크롤링
        
        Args:
            limit_per_category: 카테고리별 최대 뉴스 수
            
        Returns:
            전체 뉴스 데이터 리스트
        """
        all_news = []
        
        for source in self.news_sources:
            for category in source.category_urls.keys():
                try:
                    category_news = await self.crawl_category(
                        source, 
                        category, 
                        limit_per_category
                    )
                    all_news.extend(category_news)
                    
                    # 요청 간 지연
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"{source.name} - {category} 크롤링 실패: {e}")
                    continue
        
        logger.info(f"전체 크롤링 완료: {len(all_news)}개 뉴스 수집")
        return all_news
    
    def _parse_time(self, time_text: str) -> Optional[datetime]:
        """
        시간 텍스트를 datetime 객체로 변환
        
        Args:
            time_text: 시간 텍스트 (예: "2시간 전", "2024-01-15 14:30")
            
        Returns:
            파싱된 datetime 객체
        """
        try:
            time_text = time_text.strip()
            
            # "X시간 전", "X분 전" 패턴
            if "시간 전" in time_text:
                hours = re.search(r'(\d+)시간', time_text)
                if hours:
                    return datetime.now() - timedelta(hours=int(hours.group(1)))
            
            elif "분 전" in time_text:
                minutes = re.search(r'(\d+)분', time_text)
                if minutes:
                    return datetime.now() - timedelta(minutes=int(minutes.group(1)))
            
            elif "일 전" in time_text:
                days = re.search(r'(\d+)일', time_text)
                if days:
                    return datetime.now() - timedelta(days=int(days.group(1)))
            
            # ISO 형식 시도
            elif "-" in time_text and ":" in time_text:
                # 다양한 날짜 형식 시도
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y.%m.%d %H:%M"]:
                    try:
                        return datetime.strptime(time_text, fmt)
                    except ValueError:
                        continue
            
            return None
            
        except Exception:
            return None
    
    async def save_news_to_db(self, news_data: List[Dict[str, Any]]) -> int:
        """
        크롤링한 뉴스 데이터를 데이터베이스에 저장
        
        Args:
            news_data: 뉴스 데이터 리스트
            
        Returns:
            저장된 뉴스 수
        """
        db = next(get_db())
        saved_count = 0
        
        try:
            for news_item in news_data:
                # 중복 확인
                existing = db.query(News).filter(
                    News.source_url == news_item["source_url"]
                ).first()
                
                if existing:
                    logger.debug(f"중복 뉴스 스킵: {news_item['title'][:50]}...")
                    continue
                
                # 새 뉴스 생성
                news = News(
                    title=news_item["title"],
                    source_name=news_item["source_name"],
                    source_url=news_item["source_url"],
                    content_snippet=news_item.get("content_snippet"),
                    published_at=news_item["published_at"],
                    is_processed=False
                )
                
                db.add(news)
                saved_count += 1
            
            db.commit()
            logger.info(f"데이터베이스 저장 완료: {saved_count}개 뉴스")
            
        except Exception as e:
            db.rollback()
            logger.error(f"데이터베이스 저장 오류: {e}")
            
        finally:
            db.close()
        
        return saved_count


# 크롤링 실행 함수
async def run_news_crawling(limit_per_category: int = 15) -> Dict[str, Any]:
    """
    뉴스 크롤링 실행
    
    Args:
        limit_per_category: 카테고리별 최대 뉴스 수
        
    Returns:
        실행 결과 정보
    """
    start_time = datetime.now()
    
    try:
        async with NewsCrawler() as crawler:
            # 뉴스 크롤링
            news_data = await crawler.crawl_all_categories(limit_per_category)
            
            # 데이터베이스 저장
            saved_count = await crawler.save_news_to_db(news_data)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "crawled_count": len(news_data),
                "saved_count": saved_count,
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
            logger.info(f"크롤링 완료: {result}")
            return result
            
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        error_result = {
            "success": False,
            "error": str(e),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        logger.error(f"크롤링 실패: {error_result}")
        return error_result