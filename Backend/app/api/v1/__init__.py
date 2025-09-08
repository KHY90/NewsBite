"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, categories, news

api_router = APIRouter()

# 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(news.router, prefix="/news", tags=["news"])