# 이 파일은 뉴스 카테고리 관련 API 엔드포인트를 정의합니다.
# 전체 카테고리 목록을 조회하거나 특정 카테고리에 속한 뉴스 목록을
# 조회하는 기능을 제공할 예정입니다. (현재는 미구현 상태)

"""
카테고리 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter()


@router.get("/")
async def get_categories() -> Any:
    """뉴스 카테고리 목록 조회"""
    # TODO: 뉴스 카테고리 목록 조회 구현
    raise HTTPException(status_code=501, detail="아직 구현되지 않았습니다")


@router.get("/{category_id}/news")
async def get_news_by_category(category_id: int) -> Any:
    """카테고리별 뉴스 조회"""
    # TODO: 카테고리별 뉴스 조회 구현
    raise HTTPException(status_code=501, detail="아직 구현되지 않았습니다")