# 이 파일은 Supabase와의 통신을 위한 클라이언트 인스턴스를 생성하고 관리합니다.
# 애플리케이션 전역에서 Supabase 기능(인증, 데이터베이스 등)을 일관되게
# 사용할 수 있도록 중앙 집중화된 클라이언트 객체를 제공합니다.
#
# - `get_supabase_client`: 일반적인 클라이언트 측 상호작용을 위한 클라이언트를 생성합니다.
#                          주로 사용자의 권한으로 수행되는 작업에 사용됩니다.
# - `get_supabase_admin_client`: 'service_role' 키를 사용하여 모든 권한을 가진 관리자용
#                                클라이언트를 생성합니다. 사용자의 권한을 넘어서는
#                                백엔드 내부 작업(예: 사용자 정보 조회)에 사용됩니다.
# - 생성된 클라이언트는 전역 변수 `supabase_client`와 `supabase_admin_client`에 할당되어
#   다른 모듈에서 쉽게 가져와 사용할 수 있습니다.

"""
Supabase 클라이언트 구성 및 유틸리티
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