# 엔드포인트
# HTTP, Query 처리 전담


from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.dashboard.dashboard_service import (
    get_kpi_summary,
    get_monthly_sales,
    get_top_products,
    get_device_share,
    get_orders_by_category,
    get_funnel,
)

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


# KPI Summary
@router.get("/kpis/summary")
async def kpi_summary(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    return await get_kpi_summary(db, days)


# Monthly Sales
@router.get("/charts/monthly-sales")
async def monthly_sales(
    months: int = Query(12, ge=1, le=36),
    db: AsyncSession = Depends(get_db),
):
    return await get_monthly_sales(db, months)


# Top Products
@router.get("/tables/top-products")
async def top_products(
    limit: int = Query(10, ge=1, le=100),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_top_products(db, limit, from_date, to_date, category_id)


# Device Share
@router.get("/tables/device-share")
async def device_share(
    metric: str = Query("amount", pattern="^(amount|count)$"),
    db: AsyncSession = Depends(get_db),
):
    return await get_device_share(db, metric)


# Orders by Category
@router.get("/charts/orders-by-category")
async def orders_by_category(
    metric: str = Query("amount", pattern="^(amount|count)$"),
    db: AsyncSession = Depends(get_db),
):
    return await get_orders_by_category(db, metric)


# Funnel
@router.get("/charts/funnel")
async def funnel(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_funnel(db, from_date, to_date)
