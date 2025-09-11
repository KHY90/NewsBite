"""
AI 처리 서비스
뉴스 요약, 감정분석, 찬반정리, 임베딩 생성
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import re
from dataclasses import dataclass

import openai
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.news import News

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """AI 처리 결과"""
    summary: str
    sentiment_score: float
    sentiment_label: str
    keywords: List[str]
    is_controversial: bool
    pros_summary: Optional[str] = None
    cons_summary: Optional[str] = None
    mentioned_companies: List[str] = None
    embedding: List[float] = None


class AIProcessor:
    """AI 뉴스 처리 메인 클래스"""
    
    def __init__(self):
        # API 키 설정
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # 임베딩 모델 로드 (한국어 특화)
        self.embedding_model = None
        self._load_embedding_model()
        
        # 한국 주요 기업 리스트 (확장 가능)
        self.korean_companies = [
            "삼성전자", "SK하이닉스", "LG에너지솔루션", "삼성바이오로직스",
            "NAVER", "카카오", "셀트리온", "현대차", "기아", "포스코홀딩스",
            "LG화학", "SK이노베이션", "한국전력", "삼성물산", "LG전자",
            "한화솔루션", "SK", "현대모비스", "POSCO", "아모레퍼시픽"
        ]
    
    def _load_embedding_model(self):
        """임베딩 모델 로드"""
        try:
            # 한국어 특화 임베딩 모델
            self.embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
            logger.info("한국어 임베딩 모델 로드 완료")
        except Exception as e:
            logger.error(f"임베딩 모델 로드 실패: {e}")
            # 폴백 모델
            try:
                self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("영어 임베딩 모델 로드 완료")
            except Exception as e2:
                logger.error(f"폴백 임베딩 모델 로드도 실패: {e2}")
    
    async def summarize_news(self, title: str, content: str, use_gemini: bool = True) -> str:
        """
        뉴스 요약 생성
        
        Args:
            title: 뉴스 제목
            content: 뉴스 본문
            use_gemini: Gemini API 사용 여부 (False면 OpenAI 사용)
            
        Returns:
            요약 텍스트
        """
        prompt = f"""
다음 뉴스를 3-4문장으로 요약해주세요. 핵심 사실만 간결하게 정리하고, 객관적이고 중립적인 톤을 유지해주세요.

제목: {title}

본문: {content[:1500]}

요약:
"""
        
        try:
            if use_gemini and hasattr(self, 'gemini_model'):
                response = await self._call_gemini(prompt)
                return response.strip()
            else:
                response = await self._call_openai(prompt, max_tokens=200)
                return response.strip()
                
        except Exception as e:
            logger.error(f"뉴스 요약 생성 실패: {e}")
            # 폴백: 첫 2문장 추출
            sentences = content.split('.')[:2]
            return '. '.join(sentences) + '.'
    
    async def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        감정 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            (감정 점수, 감정 라벨) 튜플
        """
        prompt = f"""
다음 뉴스 텍스트의 감정을 분석해주세요. 

텍스트: {text[:1000]}

다음 형식으로만 답변해주세요:
점수: [---1.0에서 1.0 사이의 숫자]
라벨: [positive/negative/neutral 중 하나]

분석 기준:
- 긍정적 내용, 호재, 성장, 성공 → positive (0.1~1.0)
- 부정적 내용, 악재, 감소, 실패 → negative (-1.0~-0.1)  
- 중립적, 단순 사실 전달 → neutral (-0.1~0.1)
"""
        
        try:
            response = await self._call_gemini(prompt)
            
            # 응답 파싱
            score_match = re.search(r'점수:\s*([+-]?\d*\.?\d+)', response)
            label_match = re.search(r'라벨:\s*(positive|negative|neutral)', response)
            
            if score_match and label_match:
                score = float(score_match.group(1))
                label = label_match.group(1)
                
                # 점수 범위 검증
                score = max(-1.0, min(1.0, score))
                
                return score, label
            else:
                # 파싱 실패시 기본값
                return 0.0, "neutral"
                
        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            return 0.0, "neutral"
    
    async def detect_controversy(self, title: str, content: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        논쟁 이슈 탐지 및 찬반 의견 추출
        
        Args:
            title: 뉴스 제목
            content: 뉴스 본문
            
        Returns:
            (논쟁성 여부, 찬성 의견 요약, 반대 의견 요약)
        """
        prompt = f"""
다음 뉴스가 논쟁적 이슈인지 판단하고, 만약 논쟁적이라면 찬반 의견을 정리해주세요.

제목: {title}
본문: {content[:1200]}

다음 형식으로만 답변해주세요:

논쟁성: [true/false]
찬성 의견: [찬성 측 주장 요약 또는 "없음"]
반대 의견: [반대 측 주장 요약 또는 "없음"]

논쟁적 이슈 기준:
- 정치적 갈등, 정책 논란
- 사회적 갈등, 가치관 충돌
- 경제 정책, 규제 관련 논란
- 찬반이 나뉘는 사회 이슈
"""
        
        try:
            response = await self._call_gemini(prompt)
            
            # 응답 파싱
            controversy_match = re.search(r'논쟁성:\s*(true|false)', response)
            pros_match = re.search(r'찬성 의견:\s*(.+?)(?=반대 의견:|$)', response, re.DOTALL)
            cons_match = re.search(r'반대 의견:\s*(.+?)$', response, re.DOTALL)
            
            is_controversial = False
            if controversy_match:
                is_controversial = controversy_match.group(1) == "true"
            
            pros_summary = None
            cons_summary = None
            
            if is_controversial:
                if pros_match:
                    pros_text = pros_match.group(1).strip()
                    if pros_text and pros_text != "없음":
                        pros_summary = pros_text
                
                if cons_match:
                    cons_text = cons_match.group(1).strip()
                    if cons_text and cons_text != "없음":
                        cons_summary = cons_text
            
            return is_controversial, pros_summary, cons_summary
            
        except Exception as e:
            logger.error(f"논쟁 탐지 실패: {e}")
            return False, None, None
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        키워드 추출 (간단한 TF-IDF 기반)
        
        Args:
            text: 키워드를 추출할 텍스트
            max_keywords: 최대 키워드 수
            
        Returns:
            키워드 리스트
        """
        try:
            # 한국어 불용어
            stopwords = {
                '이', '가', '을', '를', '에', '의', '는', '은', '도', '과', '와', '로', '으로',
                '있다', '있는', '하다', '한다', '된다', '되다', '것', '수', '때', '등',
                '그', '이런', '저런', '그런', '여러', '많은', '또한', '하지만', '그러나'
            }
            
            # 단어 추출 (한글, 영문, 숫자만)
            words = re.findall(r'[가-힣a-zA-Z0-9]+', text)
            
            # 불용어 제거 및 길이 필터링
            filtered_words = [
                word for word in words 
                if len(word) >= 2 and word not in stopwords
            ]
            
            # 빈도 계산
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 빈도순 정렬 후 상위 키워드 반환
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in keywords[:max_keywords]]
            
        except Exception as e:
            logger.error(f"키워드 추출 실패: {e}")
            return []
    
    def extract_companies(self, text: str) -> List[str]:
        """
        기업명 추출
        
        Args:
            text: 기업명을 추출할 텍스트
            
        Returns:
            언급된 기업 리스트
        """
        mentioned = []
        
        for company in self.korean_companies:
            if company in text:
                mentioned.append(company)
        
        return list(set(mentioned))  # 중복 제거
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        텍스트 임베딩 생성
        
        Args:
            text: 임베딩을 생성할 텍스트
            
        Returns:
            임베딩 벡터
        """
        if not self.embedding_model:
            return None
        
        try:
            # 텍스트 길이 제한
            text = text[:512]
            
            # 임베딩 생성
            embedding = self.embedding_model.encode(text)
            
            # numpy array를 리스트로 변환
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            return None
    
    async def process_news(self, news_item: Dict[str, Any]) -> ProcessingResult:
        """
        단일 뉴스 항목에 대한 전체 AI 처리
        
        Args:
            news_item: 뉴스 데이터
            
        Returns:
            처리 결과
        """
        title = news_item.get("title", "")
        content = news_item.get("content_snippet", "") or news_item.get("raw_content", "")
        full_text = f"{title}\n{content}"
        
        try:
            # 병렬 처리
            summary_task = self.summarize_news(title, content)
            sentiment_task = self.analyze_sentiment(full_text)
            controversy_task = self.detect_controversy(title, content)
            
            # 결과 수집
            summary = await summary_task
            sentiment_score, sentiment_label = await sentiment_task
            is_controversial, pros_summary, cons_summary = await controversy_task
            
            # 동기 처리
            keywords = self.extract_keywords(full_text)
            companies = self.extract_companies(full_text)
            embedding = self.generate_embedding(full_text)
            
            return ProcessingResult(
                summary=summary,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                keywords=keywords,
                is_controversial=is_controversial,
                pros_summary=pros_summary,
                cons_summary=cons_summary,
                mentioned_companies=companies,
                embedding=embedding
            )
            
        except Exception as e:
            logger.error(f"뉴스 처리 실패: {e}")
            # 기본값 반환
            return ProcessingResult(
                summary=content[:200] if content else title,
                sentiment_score=0.0,
                sentiment_label="neutral",
                keywords=self.extract_keywords(full_text),
                is_controversial=False,
                mentioned_companies=self.extract_companies(full_text),
                embedding=self.generate_embedding(full_text)
            )
    
    async def _call_openai(self, prompt: str, max_tokens: int = 300) -> str:
        """OpenAI API 호출"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {e}")
            raise
    
    async def _call_gemini(self, prompt: str) -> str:
        """Gemini API 호출"""
        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, 
                prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API 호출 실패: {e}")
            raise


async def process_unprocessed_news(batch_size: int = 10) -> Dict[str, Any]:
    """
    처리되지 않은 뉴스들을 배치로 AI 처리
    
    Args:
        batch_size: 배치 크기
        
    Returns:
        처리 결과 정보
    """
    db = next(get_db())
    processor = AIProcessor()
    
    try:
        # 처리되지 않은 뉴스 조회
        unprocessed_news = db.query(News).filter(
            News.is_processed == False
        ).limit(batch_size).all()
        
        if not unprocessed_news:
            return {"success": True, "message": "처리할 뉴스가 없습니다", "processed_count": 0}
        
        processed_count = 0
        
        for news in unprocessed_news:
            try:
                # 뉴스 데이터 준비
                news_data = {
                    "title": news.title,
                    "content_snippet": news.content_snippet,
                    "raw_content": getattr(news, 'raw_content', None)
                }
                
                # AI 처리
                result = await processor.process_news(news_data)
                
                # 결과 저장
                news.summary = result.summary
                news.sentiment_score = result.sentiment_score
                news.sentiment_label = result.sentiment_label
                news.keywords = result.keywords
                news.is_controversial = result.is_controversial
                news.pros_summary = result.pros_summary
                news.cons_summary = result.cons_summary
                news.mentioned_companies = result.mentioned_companies
                news.embedding = result.embedding
                news.is_processed = True
                
                processed_count += 1
                logger.info(f"뉴스 처리 완료: {news.title[:50]}...")
                
                # API 요청 제한 방지
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"개별 뉴스 처리 실패 (ID: {news.id}): {e}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "processed_count": processed_count,
            "total_found": len(unprocessed_news)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"배치 처리 실패: {e}")
        return {"success": False, "error": str(e)}
        
    finally:
        db.close()