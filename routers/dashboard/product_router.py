from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

from services.dashboard.product_service import (
    get_top_products, get_kpi_summary, get_daily_trend
)
from services.dashboard.review_service import get_product_review_keywords
from repositories.dashboard.product_repository import get_product_by_id

router = APIRouter(prefix="/api/v1/product-analysis", tags=["Product Analysis"])

@router.get("/products")
async def product_list(
    limit: int = Query(10, ge=1), from_date: Optional[date] = Query(None), to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_top_products(db, limit, from_date, to_date)

@router.get("/products/{product_id}/stats")
async def product_detail_stats(
    product_id: int,
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 상품의 통계 조회 (프론트엔드 RESTful 방식)
    """
    # startDate, endDate를 days로 변환 (임시로 30일 기본값)
    days = 30  # 기본값
    
    return await get_kpi_summary(db, days, product_id)

@router.get("/stats")
async def product_stats(
    days: int = Query(30, ge=1), product_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_kpi_summary(db, days, product_id)

@router.get("/chart/trend")
async def product_trend_chart(
    days: int = Query(30, ge=7), metric: str = Query("amount"), product_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_daily_trend(db, days, metric, product_id)

@router.get("/products/{product_id}/review-keywords")
async def get_product_keywords(
    product_id: int,
    limit: int = Query(default=30, ge=1, le=50, description="반환할 키워드 개수 (최대 50)"),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 상품의 리뷰 키워드 조회 (워드클라우드용)
    
    **Parameters:**
    - product_id: 상품 내부 ID
    - limit: 반환할 키워드 개수 (기본 30, 최대 50)
    
    **Returns:**
    - 빈도수 기준 상위 키워드 목록
    - 리뷰가 없으면 빈 배열 반환
    
    **Example:**
    ```
    GET /api/v1/product-analysis/products/42/review-keywords?limit=30
    ```
    
    **Response:**
    ```json
    [
      {"text": "촉촉해요", "value": 45},
      {"text": "효과", "value": 38},
      {"text": "만족", "value": 32}
    ]
    ```
    """
    # 1. product_id로 상품 조회
    product = await get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    
    # 2. product_no로 리뷰 키워드 조회
    keywords = await get_product_review_keywords(db, product.product_no, limit)
    
    return keywords
