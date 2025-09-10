# 이 파일은 Playwright를 사용하여 외부 뉴스 웹사이트에서 뉴스 기사를
# 수집(크롤링)하는 로직을 담당합니다.
#
# - `NewsSource` 추상 클래스: 모든 뉴스 소스(네이버, 연합뉴스 등)가 상속받아야 할 기본 구조를 정의합니다.
# - `NaverNewsSource`, `YonhapNewsSource`: `NewsSource`를 상속받아 각 언론사의 웹사이트 구조에 맞게
#                                       실제 크롤링 로직을 구현합니다. HTML 선택자를 사용하여
#                                       기사 제목, 링크, 내용 등을 추출합니다.
# - `NewsCrawler` 클래스: 여러 뉴스 소스를 관리하고, Playwright 브라우저 인스턴스를 제어하며
#                         전체 크롤링 프로세스를 총괄합니다. 지정된 모든 카테고리에 대해
#                         각 뉴스 소스를 순회하며 기사를 수집합니다.
# - 비동기(asyncio) 방식으로 작동하여 여러 작업을 효율적으로 처리합니다.

"""
뉴스 크롤링 서비스
Playwright를 이용한 주요 뉴스사이트 크롤링
"""
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
import asyncio
import logging
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """뉴스 아이템 데이터 클래스"""
    title: str
    content: str
    summary: str
    url: str
    published_at: datetime
    source: str
    category: str
    thumbnail_url: Optional[str] = None


class NewsSource:
    """뉴스 소스 기본 클래스"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
    
    async def crawl(self, page: Page, category: str) -> List[NewsItem]:
        """뉴스 크롤링 추상 메서드"""
        raise NotImplementedError


class NaverNewsSource(NewsSource):
    """네이버 뉴스 크롤러"""
    
    def __init__(self):
        super().__init__("네이버뉴스", "https://news.naver.com")
        self.categories = {
            "정치": "politics",
            "경제": "economy", 
            "사회": "society",
            "생활/문화": "culture",
            "세계": "world",
            "IT/과학": "it"
        }
    
    async def crawl(self, page: Page, category: str) -> List[NewsItem]:
        """네이버 뉴스 크롤링"""
        try:
            category_code = self.categories.get(category, "politics")
            url = f"{self.base_url}/main/main.naver?mode=LSD&mid=shm&sid1=100"
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 뉴스 기사 목록 선택자
            news_items = await page.query_selector_all(".cluster_body .cluster_text a")
            
            results = []
            for item in news_items[:10]:  # 상위 10개만 수집
                try:
                    # 제목 추출
                    title_element = await item.query_selector(".cluster_text_headline")
                    if not title_element:
                        continue
                        
                    title = await title_element.inner_text()
                    link = await item.get_attribute("href")
                    
                    if not link or not title:
                        continue
                    
                    # 절대 URL로 변환
                    if link.startswith("//"):
                        link = "https:" + link
                    elif link.startswith("/"):
                        link = self.base_url + link
                    
                    # 개별 기사 페이지로 이동하여 내용 수집
                    article_content = await self._get_article_content(page, link)
                    
                    news_item = NewsItem(
                        title=title.strip(),
                        content=article_content.get("content", ""),
                        summary=article_content.get("summary", ""),
                        url=link,
                        published_at=article_content.get("published_at", datetime.now()),
                        source=self.name,
                        category=category,
                        thumbnail_url=article_content.get("thumbnail")
                    )
                    
                    results.append(news_item)
                    
                except Exception as e:
                    logger.warning(f"뉴스 아이템 처리 중 오류: {e}")
                    continue
            
            logger.info(f"네이버 뉴스 {category} 카테고리에서 {len(results)}개 기사 수집")
            return results
            
        except Exception as e:
            logger.error(f"네이버 뉴스 크롤링 오류: {e}")
            return []
    
    async def _get_article_content(self, page: Page, url: str) -> Dict:
        """개별 기사 내용 추출"""
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            # 기사 내용 추출
            content_element = await page.query_selector(".newsct_article, #articleBodyContents, .article_body")
            content = ""
            if content_element:
                content = await content_element.inner_text()
                content = content.strip()[:2000]  # 2000자까지만
            
            # 썸네일 추출
            thumbnail_element = await page.query_selector(".end_photo_org img, .article_img img")
            thumbnail_url = None
            if thumbnail_element:
                thumbnail_url = await thumbnail_element.get_attribute("src")
            
            # 발행시간 추출 (간단한 처리)
            time_element = await page.query_selector(".media_end_head_info_datestamp_time")
            published_at = datetime.now()
            if time_element:
                try:
                    time_text = await time_element.inner_text()
                    # 시간 파싱 로직 (추후 개선 필요)
                    published_at = datetime.now()
                except:
                    pass
            
            return {
                "content": content,
                "summary": content[:200] + "..." if len(content) > 200 else content,
                "thumbnail": thumbnail_url,
                "published_at": published_at
            }
            
        except Exception as e:
            logger.warning(f"기사 내용 추출 오류 {url}: {e}")
            return {"content": "", "summary": "", "thumbnail": None, "published_at": datetime.now()}


class YonhapNewsSource(NewsSource):
    """연합뉴스 크롤러"""
    
    def __init__(self):
        super().__init__("연합뉴스", "https://www.yna.co.kr")
        self.categories = {
            "정치": "politics",
            "경제": "economy",
            "사회": "society", 
            "국제": "international",
            "IT/과학": "technology"
        }
    
    async def crawl(self, page: Page, category: str) -> List[NewsItem]:
        """연합뉴스 크롤링"""
        try:
            category_path = self.categories.get(category, "politics")
            url = f"{self.base_url}/view/AKR"
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 뉴스 기사 목록 선택자 (연합뉴스 구조에 맞게 조정)
            news_items = await page.query_selector_all(".news-con .item-box01")
            
            results = []
            for item in news_items[:8]:  # 상위 8개만 수집
                try:
                    title_element = await item.query_selector(".news-tl")
                    link_element = await item.query_selector("a")
                    
                    if not title_element or not link_element:
                        continue
                    
                    title = await title_element.inner_text()
                    link = await link_element.get_attribute("href")
                    
                    if not link or not title:
                        continue
                    
                    # 절대 URL로 변환
                    if link.startswith("/"):
                        link = self.base_url + link
                    
                    # 간단한 내용 추출 (연합뉴스는 목록에서 요약 제공)
                    summary_element = await item.query_selector(".news-sm")
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                    
                    news_item = NewsItem(
                        title=title.strip(),
                        content=summary,  # 연합뉴스는 목록에서 요약만 가져옴
                        summary=summary[:200] + "..." if len(summary) > 200 else summary,
                        url=link,
                        published_at=datetime.now(),
                        source=self.name,
                        category=category
                    )
                    
                    results.append(news_item)
                    
                except Exception as e:
                    logger.warning(f"연합뉴스 아이템 처리 중 오류: {e}")
                    continue
            
            logger.info(f"연합뉴스 {category} 카테고리에서 {len(results)}개 기사 수집")
            return results
            
        except Exception as e:
            logger.error(f"연합뉴스 크롤링 오류: {e}")
            return []


class NewsCrawler:
    """뉴스 크롤러 메인 클래스"""
    
    def __init__(self):
        self.sources = [
            NaverNewsSource(),
            YonhapNewsSource()
        ]
    
    async def crawl_all_categories(self, categories: List[str] = None) -> List[NewsItem]:
        """모든 카테고리의 뉴스 크롤링"""
        if categories is None:
            categories = ["정치", "경제", "사회", "IT/과학", "세계"]
        
        all_news = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                for source in self.sources:
                    page = await browser.new_page()
                    
                    # User-Agent 설정
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    for category in categories:
                        try:
                            logger.info(f"{source.name}에서 {category} 카테고리 크롤링 시작")
                            news_items = await source.crawl(page, category)
                            all_news.extend(news_items)
                            
                            # 요청 간 간격
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"{source.name} {category} 크롤링 오류: {e}")
                            continue
                    
                    await page.close()
                    
            finally:
                await browser.close()
        
        logger.info(f"총 {len(all_news)}개의 뉴스 기사 수집 완료")
        return all_news
    
    async def crawl_category(self, category: str) -> List[NewsItem]:
        """특정 카테고리 뉴스 크롤링"""
        return await self.crawl_all_categories([category])


# 크롤러 인스턴스 생성
news_crawler = NewsCrawler()


async def main():
    """테스트용 메인 함수"""
    logging.basicConfig(level=logging.INFO)
    crawler = NewsCrawler()
    news_items = await crawler.crawl_category("정치")
    
    for item in news_items[:3]:
        print(f"\n제목: {item.title}")
        print(f"출처: {item.source}")
        print(f"요약: {item.summary}")
        print(f"URL: {item.url}")


if __name__ == "__main__":
    asyncio.run(main())