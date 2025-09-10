# 이 파일은 Pydantic의 BaseSettings를 사용하여 애플리케이션 전체의 설정을 관리합니다.
# .env 파일에서 환경 변수를 로드하며, 데이터베이스, CORS, Supabase, AI API 키 등
# 다양한 설정 값을 중앙에서 관리할 수 있도록 구조화되어 있습니다.
# 각 설정은 타입 어노테이션을 통해 유효성 검사를 받습니다.

"""
Pydantic 설정을 사용한 애플리케이션 구성
"""
from typing import List, Optional, Union
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 애플리케이션
    PROJECT_NAME: str = "NewsBite API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 8  # 8 days
    
    # 환경
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if v is None or v == "":
            return []
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 데이터베이스
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "newsbite"
    POSTGRES_PASSWORD: str = "newsbite_password"
    POSTGRES_DB: str = "newsbite_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if isinstance(v, str) and v:
            return v
        
        # 개발용 기본 연결 문자열
        return "postgresql://newsbite:newsbite_password@localhost:5432/newsbite_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # AI API
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # 이메일 (SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    # 뉴스 설정
    NEWS_CRAWL_START_TIME: str = "18:00"
    NEWS_CRAWL_END_TIME: str = "18:30"
    EMAIL_SEND_TIME: str = "19:00"
    
    # AWS (프로덕션)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-2"
    
    # Playwright
    PLAYWRIGHT_BROWSERS_PATH: str = "/app/browsers"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()