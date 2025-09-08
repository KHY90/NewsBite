"""
AI 처리 서비스
OpenAI/Gemini API를 이용한 뉴스 요약, 감정분석, 찬반정리
"""
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import openai
import google.generativeai as genai
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

# OpenAI 클라이언트 설정
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

# Gemini 클라이언트 설정
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


@dataclass
class AIProcessingResult:
    """AI 처리 결과 데이터 클래스"""
    ai_summary: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    pros_and_cons: Optional[str] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None


class AIService:
    """AI 처리 서비스 클래스"""
    
    def __init__(self):
        self.openai_available = bool(settings.OPENAI_API_KEY)
        self.gemini_available = bool(settings.GEMINI_API_KEY)
        
        if self.gemini_available:
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        logger.info(f"AI 서비스 초기화 - OpenAI: {self.openai_available}, Gemini: {self.gemini_available}")
    
    async def process_news_article(self, 
                                 title: str, 
                                 content: str, 
                                 category: str = "") -> AIProcessingResult:
        """뉴스 기사 전체 AI 처리"""
        start_time = datetime.now()
        result = AIProcessingResult()
        
        try:
            # 1. 뉴스 요약
            summary_task = self.summarize_news(title, content, category)
            
            # 2. 감정 분석
            sentiment_task = self.analyze_sentiment(title, content)
            
            # 3. 찬반 정리 (논쟁성 이슈인 경우)
            pros_cons_task = self.analyze_pros_and_cons(title, content, category)
            
            # 병렬 처리
            summary_result, sentiment_result, pros_cons_result = await asyncio.gather(
                summary_task, sentiment_task, pros_cons_task,
                return_exceptions=True
            )
            
            # 결과 통합
            if isinstance(summary_result, str):
                result.ai_summary = summary_result
            
            if isinstance(sentiment_result, dict):
                result.sentiment_score = sentiment_result.get('score')
                result.sentiment_label = sentiment_result.get('label')
            
            if isinstance(pros_cons_result, str) and pros_cons_result.strip():
                result.pros_and_cons = pros_cons_result
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            logger.info(f"뉴스 AI 처리 완료 - 소요시간: {processing_time:.2f}초")
            return result
            
        except Exception as e:
            result.error = str(e)
            logger.error(f"뉴스 AI 처리 오류: {e}")
            return result
    
    async def summarize_news(self, 
                           title: str, 
                           content: str, 
                           category: str = "") -> str:
        """뉴스 기사 요약"""
        try:
            # 긴 내용은 잘라내기 (토큰 제한)
            content_preview = content[:3000] if len(content) > 3000 else content
            
            prompt = f"""다음 뉴스 기사를 한국어로 3-4문장으로 요약해주세요. 
핵심 내용과 중요한 사실만 포함하고, 객관적이고 중립적으로 작성해주세요.

제목: {title}
카테고리: {category}
내용: {content_preview}

요약:"""
            
            # Gemini를 우선 사용, 실패 시 OpenAI 사용
            if self.gemini_available:
                try:
                    response = await self._call_gemini(prompt)
                    if response and len(response.strip()) > 10:
                        return response.strip()
                except Exception as e:
                    logger.warning(f"Gemini 요약 실패: {e}")
            
            if self.openai_available:
                try:
                    response = await self._call_openai(
                        prompt,
                        max_tokens=200,
                        temperature=0.3
                    )
                    return response.strip()
                except Exception as e:
                    logger.warning(f"OpenAI 요약 실패: {e}")
            
            # 두 API 모두 실패 시 간단한 요약
            return self._create_simple_summary(content_preview)
            
        except Exception as e:
            logger.error(f"뉴스 요약 오류: {e}")
            return ""
    
    async def analyze_sentiment(self, title: str, content: str) -> Dict:
        """감정 분석"""
        try:
            content_preview = content[:2000] if len(content) > 2000 else content
            
            prompt = f"""다음 뉴스 기사의 전체적인 감정과 톤을 분석해주세요.
            
제목: {title}
내용: {content_preview}

다음 중 하나로 분류하고 0.0-1.0 사이의 점수를 매겨주세요:
- 매우 긍정적 (0.8-1.0)
- 긍정적 (0.6-0.79)
- 중립적 (0.4-0.59)
- 부정적 (0.2-0.39)
- 매우 부정적 (0.0-0.19)

응답 형식: "분류|점수"
예시: "긍정적|0.65"

분석:"""
            
            # Gemini 또는 OpenAI로 감정 분석
            response = ""
            if self.gemini_available:
                try:
                    response = await self._call_gemini(prompt)
                except Exception as e:
                    logger.warning(f"Gemini 감정분석 실패: {e}")
            
            if not response and self.openai_available:
                try:
                    response = await self._call_openai(
                        prompt,
                        max_tokens=50,
                        temperature=0.1
                    )
                except Exception as e:
                    logger.warning(f"OpenAI 감정분석 실패: {e}")
            
            # 응답 파싱
            if response and "|" in response:
                parts = response.strip().split("|")
                if len(parts) >= 2:
                    label = parts[0].strip()
                    try:
                        score = float(parts[1].strip())
                        return {"label": label, "score": score}
                    except ValueError:
                        pass
            
            # 기본값 (중립)
            return {"label": "중립적", "score": 0.5}
            
        except Exception as e:
            logger.error(f"감정 분석 오류: {e}")
            return {"label": "중립적", "score": 0.5}
    
    async def analyze_pros_and_cons(self, 
                                  title: str, 
                                  content: str, 
                                  category: str = "") -> str:
        """찬반 정리 (논쟁성 이슈 대상)"""
        try:
            # 논쟁성 이슈 여부 확인
            controversial_keywords = [
                "논란", "논쟁", "갈등", "반대", "찬성", "비판", "항의", "시위",
                "정책", "법안", "규제", "개발", "환경", "노동", "인권"
            ]
            
            is_controversial = any(keyword in title or keyword in content 
                                 for keyword in controversial_keywords)
            
            if not is_controversial:
                return ""
            
            content_preview = content[:2500] if len(content) > 2500 else content
            
            prompt = f"""다음 뉴스가 논쟁적인 이슈를 다루고 있다면, 찬성 측과 반대 측의 주요 논점을 객관적으로 정리해주세요.
논쟁적이지 않은 일반 뉴스라면 "해당없음"으로 응답해주세요.

제목: {title}
카테고리: {category}
내용: {content_preview}

찬반 정리 (각각 2-3줄로):
찬성 측 주요 논점:
- 

반대 측 주요 논점:
- 

정리:"""
            
            response = ""
            if self.gemini_available:
                try:
                    response = await self._call_gemini(prompt)
                except Exception as e:
                    logger.warning(f"Gemini 찬반정리 실패: {e}")
            
            if not response and self.openai_available:
                try:
                    response = await self._call_openai(
                        prompt,
                        max_tokens=300,
                        temperature=0.4
                    )
                except Exception as e:
                    logger.warning(f"OpenAI 찬반정리 실패: {e}")
            
            if response and "해당없음" not in response and len(response.strip()) > 20:
                return response.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"찬반 정리 오류: {e}")
            return ""
    
    async def _call_gemini(self, prompt: str) -> str:
        """Gemini API 호출"""
        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            return response.text if response.text else ""
        except Exception as e:
            logger.error(f"Gemini API 오류: {e}")
            raise
    
    async def _call_openai(self, 
                          prompt: str, 
                          max_tokens: int = 150, 
                          temperature: float = 0.3) -> str:
        """OpenAI API 호출"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30
            )
            return response.choices[0].message.content if response.choices else ""
        except Exception as e:
            logger.error(f"OpenAI API 오류: {e}")
            raise
    
    def _create_simple_summary(self, content: str) -> str:
        """간단한 요약 생성 (API 실패 시 폴백)"""
        try:
            # 첫 3문장을 가져오거나 200자까지
            sentences = content.split('.')[:3]
            summary = '. '.join(sentences).strip()
            
            if len(summary) > 200:
                summary = summary[:200] + "..."
            
            return summary if summary else content[:200] + "..."
            
        except Exception:
            return content[:200] + "..." if len(content) > 200 else content


# AI 서비스 인스턴스
ai_service = AIService()


async def batch_process_news(news_items: List[Dict]) -> List[AIProcessingResult]:
    """뉴스 배치 처리"""
    results = []
    
    # 동시 처리 수 제한 (API 레이트 리밋 고려)
    semaphore = asyncio.Semaphore(3)
    
    async def process_single_news(news_item):
        async with semaphore:
            return await ai_service.process_news_article(
                title=news_item.get('title', ''),
                content=news_item.get('content', ''),
                category=news_item.get('category', '')
            )
    
    # 모든 뉴스 병렬 처리
    tasks = [process_single_news(item) for item in news_items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 예외 처리
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, AIProcessingResult):
            processed_results.append(result)
        else:
            error_result = AIProcessingResult(error=str(result))
            processed_results.append(error_result)
            logger.error(f"뉴스 {i} AI 처리 실패: {result}")
    
    return processed_results


if __name__ == "__main__":
    """테스트용 실행"""
    async def test():
        logging.basicConfig(level=logging.INFO)
        
        # 테스트 뉴스
        test_news = {
            'title': '정부, 부동산 규제 완화 정책 발표',
            'content': '정부가 오늘 부동산 시장 활성화를 위한 규제 완화 정책을 발표했다. 주요 내용은 LTV 비율 상향 조정과 종합부동산세 완화 등이다. 업계에서는 환영하는 분위기이지만 서민층은 집값 상승을 우려하고 있다.',
            'category': '경제'
        }
        
        service = AIService()
        result = await service.process_news_article(
            test_news['title'],
            test_news['content'], 
            test_news['category']
        )
        
        print(f"\n=== AI 처리 결과 ===")
        print(f"요약: {result.ai_summary}")
        print(f"감정: {result.sentiment_label} ({result.sentiment_score})")
        print(f"찬반: {result.pros_and_cons}")
        print(f"처리시간: {result.processing_time}초")
        print(f"오류: {result.error}")
    
    asyncio.run(test())