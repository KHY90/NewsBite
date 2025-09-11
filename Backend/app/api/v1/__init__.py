"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1 import auth, subscriptions, admin, feedback
from app.api.v1.endpoints import users, categories, news

api_router = APIRouter()

# 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])