"""
간단한 Playwright 테스트
"""
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimpleNews:
    title: str
    url: str
    source: str


async def simple_news_test():
    """간단한 뉴스 크롤링 테스트"""
    print("=== 간단한 뉴스 크롤링 테스트 ===")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # User-Agent 설정
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # 네이버 뉴스 정치 섹션 접속
            print("네이버 뉴스 접속 중...")
            await page.goto("https://news.naver.com/section/100", wait_until="networkidle", timeout=30000)
            
            # 페이지 제목 확인
            title = await page.title()
            print(f"페이지 제목: {title}")
            
            # 주요 뉴스 제목들 수집
            print("주요 뉴스 제목 수집 중...")
            
            # 다양한 선택자 시도 (네이버 뉴스 섹션용)
            selectors = [
                ".sa_text_strong",        # 네이버 뉴스 섹션 제목
                ".sa_text_title",         # 네이버 뉴스 타이틀
                ".sa_item_title",         # 아이템 제목
                ".sa_text",               # 일반 텍스트
                "strong.sa_text_strong",  # 강조 제목
                "a.sa_text_title",        # 링크된 제목
                "a[href*='/article/']",   # 기사 링크
            ]
            
            news_items = []
            
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"선택자 '{selector}'로 {len(elements)}개 요소 발견")
                    
                    if elements:
                        for i, element in enumerate(elements[:5]):  # 처음 5개만
                            try:
                                title_text = await element.inner_text()
                                link = await element.get_attribute('href') or ""
                                
                                if title_text and len(title_text.strip()) > 10:
                                    news_items.append(SimpleNews(
                                        title=title_text.strip(),
                                        url=link,
                                        source="네이버뉴스"
                                    ))
                                    
                            except Exception as e:
                                continue
                        
                        if news_items:
                            break  # 뉴스를 찾았으면 중단
                            
                except Exception as e:
                    print(f"선택자 '{selector}' 처리 오류: {e}")
                    continue
            
            await browser.close()
            
            # 결과 출력
            print(f"\n총 {len(news_items)}개 뉴스 수집:")
            for i, item in enumerate(news_items[:10]):
                print(f"{i+1}. {item.title}")
                print(f"   URL: {item.url[:80]}...")
            
            return len(news_items) > 0
            
        except Exception as e:
            print(f"크롤링 오류: {e}")
            return False


async def simple_ai_test():
    """간단한 AI 테스트 (Gemini)"""
    print("\n=== 간단한 AI 테스트 ===")
    
    try:
        import google.generativeai as genai
        from app.core.config import settings

        # API 키 확인
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            print("Gemini API 키가 .env 파일에 설정되지 않았습니다.")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 간단한 테스트 요약 요청
        test_content = """
        정부가 오늘 부동산 시장 활성화를 위한 규제 완화 정책을 발표했다.
        주요 내용은 LTV 비율 상향 조정과 종합부동산세 완화 등이다.
        업계에서는 환영하는 분위기이지만 서민층은 집값 상승을 우려하고 있다.
        """
        
        prompt = f"""다음 뉴스를 한국어로 2-3문장으로 요약해주세요:
        {test_content}
        
        요약:"""
        
        print("AI 요약 생성 중...")
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        if response.text:
            print(f"AI 요약 결과: {response.text}")
            return True
        else:
            print("AI 응답이 비어있습니다.")
            return False
            
    except Exception as e:
        print(f"AI 테스트 오류: {e}")
        return False


async def main():
    """메인 테스트"""
    print("NewsBite Phase 3 - 간단한 기능 테스트")
    print("=" * 50)
    
    # 1. 웹 크롤링 테스트
    crawler_ok = await simple_news_test()
    
    # 2. AI 처리 테스트
    ai_ok = await simple_ai_test()
    
    print("\n" + "=" * 50)
    print("테스트 결과:")
    print(f"웹 크롤링: {'성공' if crawler_ok else '실패'}")
    print(f"AI 처리: {'성공' if ai_ok else '실패'}")
    
    if crawler_ok and ai_ok:
        print("\nPhase 3 핵심 기능이 정상 작동합니다!")
    else:
        print("\n일부 기능에서 문제가 발견되었습니다.")


if __name__ == "__main__":
    asyncio.run(main())