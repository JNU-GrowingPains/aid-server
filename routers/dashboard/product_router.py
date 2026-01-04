from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

from services.dashboard.product_service import (
    get_top_products, get_kpi_summary, get_daily_trend
)

router = APIRouter(prefix="/api/v1/product-analysis", tags=["Product Analysis"])

@router.get("/products")
async def product_list(
    limit: int = Query(10, ge=1), from_date: Optional[date] = Query(None), to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_top_products(db, limit, from_date, to_date)

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
