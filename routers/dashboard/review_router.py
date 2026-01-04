# routers/dashboard/review_router.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

from services.dashboard.review_service import (
    get_review_analysis, get_review_keywords, get_review_list
)

router = APIRouter(prefix="/api/v1/review-analysis", tags=["Review Analysis"])


# 1. 리뷰 통계 & 부정 리뷰 Top 3
@router.get("/stats")
async def review_stats(
    db: AsyncSession = Depends(get_db),
):
    return await get_review_analysis(db)


# 2. 워드클라우드 데이터
@router.get("/keywords")
async def review_keywords(
    db: AsyncSession = Depends(get_db),
):
    return await get_review_keywords(db)


# 3. 전체 리뷰 리스트
@router.get("/list")
async def review_list(
    page: int = Query(1, ge=1),  # 페이지 번호
    limit: int = Query(10, ge=1, le=100),  # 페이지당 개수
    rating: Optional[int] = Query(None),   # 별점 필터
    db: AsyncSession = Depends(get_db),
):
    return await get_review_list(db, page, limit, rating)