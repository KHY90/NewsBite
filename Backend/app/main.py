"""
NewsBite FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import api_router
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting NewsBite API...")
    await init_db()
    print("✅ Database initialized")
    
    # 스케줄러 시작
    await start_scheduler()
    print("⏰ News scheduler started")
    
    yield
    
    # Shutdown
    print("📴 Shutting down NewsBite API...")
    await stop_scheduler()
    print("⏸️ News scheduler stopped")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="뉴스한입 - 개인 맞춤형 뉴스 요약 서비스 API",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS 설정
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # API 라우터 포함
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"])
    async def root():
        """API 상태 확인"""
        return {
            "message": "NewsBite API is running!",
            "version": "1.0.0",
            "docs_url": "/docs" if settings.DEBUG else None,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """헬스 체크 엔드포인트"""
        return {"status": "healthy", "service": "newsbite-api"}

    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception):
        """내부 서버 오류 핸들러"""
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": str(exc) if settings.DEBUG else None}
        )

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )