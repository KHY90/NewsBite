"""
Categories endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter()


@router.get("/")
async def get_categories() -> Any:
    """뉴스 카테고리 목록 조회"""
    # TODO: 뉴스 카테고리 목록 조회 구현
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{category_id}/news")
async def get_news_by_category(category_id: int) -> Any:
    """카테고리별 뉴스 조회"""
    # TODO: 카테고리별 뉴스 조회 구현
    raise HTTPException(status_code=501, detail="Not implemented yet")