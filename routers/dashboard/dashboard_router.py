# 엔드포인트
# HTTP, Query 처리 전담
# dashboard_router.py

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db

from services.dashboard.dashboard_service import (
    get_kpi_summary,
    get_daily_trend,
    get_top_products,
    get_funnel,
    get_review_analysis,
    get_review_keywords
)

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


# KPI Summary
@router.get("/kpis/summary")
async def kpi_summary(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    return await get_kpi_summary(db, days)


# Daily Trend Chart
@router.get("/charts/daily-trend")
async def daily_trend_chart(
    days: int = Query(30, ge=7, le=90),
    metric: str = Query("amount", pattern="^(amount|count|buyer)$"), # 유효성 검사
    db: AsyncSession = Depends(get_db),
):
    return await get_daily_trend(db, days, metric)


# Top Products
@router.get("/tables/top-products")
async def top_products(
    limit: int = Query(10, ge=1, le=100),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):

    return await get_top_products(db, limit, from_date, to_date)


# Review Analysis
@router.get("/reviews/analysis")
async def review_analysis(
    db: AsyncSession = Depends(get_db),
):
    return await get_review_analysis(db)


# Word Cloud
@router.get("/reviews/keywords")
async def review_keywords(
    db: AsyncSession = Depends(get_db),
):
    return await get_review_keywords(db)


# Funnel
@router.get("/charts/funnel")
async def funnel(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_funnel(db, from_date, to_date)
