"""
이메일 발송 서비스
SMTP를 통한 HTML/텍스트 이메일 전송
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """이메일 발송 서비스"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME or "뉴스한입"
        
        # Jinja2 템플릿 환경 설정
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # 스레드 풀 실행기 (비동기 이메일 발송용)
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """SMTP 연결 생성"""
        try:
            if self.smtp_port == 465:
                # SSL 연결
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # TLS 연결
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.smtp_username, self.smtp_password)
            return server
            
        except Exception as e:
            logger.error(f"SMTP 연결 실패: {e}")
            raise
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """템플릿 렌더링"""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"템플릿 렌더링 실패 ({template_name}): {e}")
            raise
    
    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """동기 이메일 발송"""
        try:
            # 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 텍스트 및 HTML 파트 추가
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # 첨부파일 추가 (선택사항)
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # SMTP 연결 및 발송
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"이메일 발송 성공: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패 ({to_email}): {e}")
            return False
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """비동기 이메일 발송"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._send_email_sync,
            to_email,
            subject,
            html_content,
            text_content,
            attachments
        )
    
    async def send_daily_news_email(
        self,
        user_email: str,
        user_name: str,
        personalized_data: Dict[str, Any]
    ) -> bool:
        """일일 뉴스 이메일 발송"""
        try:
            # 날짜 포맷팅
            today = datetime.now()
            date_str = today.strftime("%Y년 %m월 %d일")
            
            # 템플릿 컨텍스트 준비
            context = {
                "user_name": user_name,
                "date": date_str,
                "total_news": personalized_data.get("total_news", 0),
                "categories_count": len(personalized_data.get("news_by_category", {})),
                "companies_count": len(personalized_data.get("news_by_company", {})),
                "controversial_count": len(personalized_data.get("controversial_news", [])),
                "news_by_category": personalized_data.get("news_by_category", {}),
                "news_by_company": personalized_data.get("news_by_company", {}),
                "controversial_news": personalized_data.get("controversial_news", []),
                "webapp_url": settings.WEBAPP_URL or "https://newsbite.kr",
                "preferences_url": f"{settings.WEBAPP_URL}/preferences",
                "feedback_url": f"{settings.WEBAPP_URL}/feedback",
                "unsubscribe_url": f"{settings.WEBAPP_URL}/unsubscribe?email={user_email}",
            }
            
            # HTML 및 텍스트 콘텐츠 생성
            html_content = self._render_template("daily_news.html", context)
            text_content = self._render_template("daily_news.txt", context)
            
            # 이메일 제목
            subject = f"🗞️ {date_str} 뉴스한입 - 개인 맞춤 뉴스 ({context['total_news']}개)"
            
            # 이메일 발송
            return await self.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"일일 뉴스 이메일 발송 실패 ({user_email}): {e}")
            return False
    
    async def send_bulk_daily_news(
        self,
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """일괄 일일 뉴스 이메일 발송"""
        results = {"success": 0, "failed": 0}
        
        # 동시 발송 제한 (5개씩)
        semaphore = asyncio.Semaphore(5)
        
        async def send_to_user(recipient):
            async with semaphore:
                success = await self.send_daily_news_email(
                    user_email=recipient["email"],
                    user_name=recipient["name"],
                    personalized_data=recipient["news_data"]
                )
                return success
        
        # 모든 사용자에게 병렬 발송
        tasks = [send_to_user(recipient) for recipient in recipients]
        send_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 집계
        for result in send_results:
            if isinstance(result, Exception):
                logger.error(f"이메일 발송 예외: {result}")
                results["failed"] += 1
            elif result:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"일괄 이메일 발송 완료 - 성공: {results['success']}, 실패: {results['failed']}")
        return results
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """환영 이메일 발송"""
        try:
            context = {
                "user_name": user_name,
                "webapp_url": settings.WEBAPP_URL or "https://newsbite.kr",
                "preferences_url": f"{settings.WEBAPP_URL}/preferences"
            }
            
            # 간단한 환영 메시지 (템플릿 추가 가능)
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #667eea;">🗞️ 뉴스한입에 오신 것을 환영합니다!</h1>
                    <p>안녕하세요, {user_name}님!</p>
                    <p>뉴스한입 회원이 되어주셔서 감사합니다. 매일 저녁 7시에 개인 맞춤형 뉴스를 이메일로 받아보실 수 있습니다.</p>
                    <p>먼저 <a href="{context['preferences_url']}" style="color: #667eea;">관심사 설정</a>에서 원하는 뉴스 카테고리와 기업을 선택해 주세요.</p>
                    <p>감사합니다!</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #888;">
                        © 2024 뉴스한입. 모든 권리 보유.
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            뉴스한입에 오신 것을 환영합니다!
            
            안녕하세요, {user_name}님!
            
            뉴스한입 회원이 되어주셔서 감사합니다. 매일 저녁 7시에 개인 맞춤형 뉴스를 이메일로 받아보실 수 있습니다.
            
            먼저 관심사 설정({context['preferences_url']})에서 원하는 뉴스 카테고리와 기업을 선택해 주세요.
            
            감사합니다!
            
            © 2024 뉴스한입. 모든 권리 보유.
            """
            
            return await self.send_email(
                to_email=user_email,
                subject="🗞️ 뉴스한입에 오신 것을 환영합니다!",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"환영 이메일 발송 실패 ({user_email}): {e}")
            return False
    
    async def send_test_email(self, to_email: str) -> bool:
        """테스트 이메일 발송"""
        try:
            html_content = """
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h1 style="color: #667eea;">📧 테스트 이메일</h1>
                <p>뉴스한입 이메일 시스템이 정상적으로 작동합니다!</p>
                <p>발송 시간: {}</p>
            </body>
            </html>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            text_content = f"""
            📧 테스트 이메일
            
            뉴스한입 이메일 시스템이 정상적으로 작동합니다!
            
            발송 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """
            
            return await self.send_email(
                to_email=to_email,
                subject="📧 뉴스한입 테스트 이메일",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"테스트 이메일 발송 실패 ({to_email}): {e}")
            return False


# 전역 이메일 서비스 인스턴스
email_service = EmailService()


# 편의 함수들
async def send_daily_news_email(
    user_email: str,
    user_name: str,
    personalized_data: Dict[str, Any]
) -> bool:
    """일일 뉴스 이메일 발송 편의 함수"""
    return await email_service.send_daily_news_email(
        user_email=user_email,
        user_name=user_name,
        personalized_data=personalized_data
    )


async def send_bulk_daily_news(
    recipients: List[Dict[str, Any]]
) -> Dict[str, int]:
    """일괄 일일 뉴스 이메일 발송 편의 함수"""
    return await email_service.send_bulk_daily_news(recipients)


async def send_welcome_email(user_email: str, user_name: str) -> bool:
    """환영 이메일 발송 편의 함수"""
    return await email_service.send_welcome_email(user_email, user_name)


async def send_test_email(to_email: str) -> bool:
    """테스트 이메일 발송 편의 함수"""
    return await email_service.send_test_email(to_email)