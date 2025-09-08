"""
Supabase client configuration and utilities
"""
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Supabase 클라이언트 인스턴스 생성
    """
    try:
        supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        return supabase
    except Exception as e:
        logger.error(f"Supabase 클라이언트 생성 실패: {e}")
        raise

def get_supabase_admin_client() -> Client:
    """
    Supabase 관리자 클라이언트 인스턴스 생성 (service_role 키 사용)
    """
    try:
        supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY
        )
        return supabase
    except Exception as e:
        logger.error(f"Supabase 관리자 클라이언트 생성 실패: {e}")
        raise

# 글로벌 클라이언트 인스턴스
supabase_client = get_supabase_client()
supabase_admin_client = get_supabase_admin_client()