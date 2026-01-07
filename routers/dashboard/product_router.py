from datetime import date, datetime
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
    """
    상품 목록 조회 (그룹화된 대표 상품)
    
    반환:
    - product_id: 대표 상품 ID
    - product_code: 상품 코드
    - product_name: 커스텀 상품명
    - price: 가격
    - category: 카테고리
    """
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
    
    기간 선택 방법:
    - startDate, endDate 사용: 달력으로 직접 선택한 기간 (YYYY-MM-DD 형식)
    - 미제공 시: 최근 30일 기본값
    """
    # startDate, endDate를 date 객체로 변환
    from_date = None
    to_date = None
    
    if startDate:
        from_date = datetime.strptime(startDate, "%Y-%m-%d").date()
    if endDate:
        to_date = datetime.strptime(endDate, "%Y-%m-%d").date()
    
    # from_date, to_date 전달 (있으면 우선 사용, 없으면 days=30 기본값)
    return await get_kpi_summary(db, days=30, product_id=product_id, 
                                 from_date=from_date, to_date=to_date)

@router.get("/stats")
async def product_stats(
    days: int = Query(30, ge=1), 
    product_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None, description="시작 날짜 (달력 직접 선택 시)"),
    to_date: Optional[date] = Query(None, description="종료 날짜 (달력 직접 선택 시)"),
    db: AsyncSession = Depends(get_db)
):
    """
    상품 KPI 통계
    
    기간 선택 방법:
    1. 최근 7일/30일/90일: days 파라미터 사용
    2. 달력 직접 선택: from_date, to_date 사용 (우선순위 높음)
    """
    return await get_kpi_summary(db, days, product_id, from_date, to_date)

@router.get("/chart/trend")
async def product_trend_chart(
    days: int = Query(30, ge=7), 
    metric: str = Query("amount"), 
    product_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None, description="시작 날짜 (달력 직접 선택 시)"),
    to_date: Optional[date] = Query(None, description="종료 날짜 (달력 직접 선택 시)"),
    db: AsyncSession = Depends(get_db)
):
    """
    일별 트렌드 차트
    
    기간 선택 방법:
    1. 최근 7일/30일/90일: days 파라미터 사용
    2. 달력 직접 선택: from_date, to_date 사용 (우선순위 높음)
    """
    return await get_daily_trend(db, days, metric, product_id, from_date, to_date)

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
