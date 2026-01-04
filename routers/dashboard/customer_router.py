# routers/dashboard/customer_router.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db

from services.dashboard.customer_service import (
    get_customer_kpi, get_customer_grade_counts, get_customer_list
)

router = APIRouter(prefix="/api/v1/customer-analysis", tags=["Customer Analysis"])
async def get_current_site_id(): return 1


# -----------------------------------------------------------
# 1. 고객 분석 KPI
# -----------------------------------------------------------
@router.get("/kpis")
async def customer_kpis(
    db: AsyncSession = Depends(get_db),
    site_id: int = Depends(get_current_site_id)
):
    return await get_customer_kpi(db, site_id)


# -----------------------------------------------------------
# 2. 등급별 고객 수
# -----------------------------------------------------------
@router.get("/grades")
async def customer_grade_counts(
    db: AsyncSession = Depends(get_db),
    site_id: int = Depends(get_current_site_id)
):
    return await get_customer_grade_counts(db, site_id)


# -----------------------------------------------------------
# 3. 고객 리스트
# -----------------------------------------------------------
@router.get("/list")
async def customer_list(
    page: int = Query(1, ge=1),  # 페이지 번호
    limit: int = Query(10, ge=1, le=100),   # 페이지당 개수
    grade: Optional[str] = Query(None),   # 등급 필터
    sort_by: str = Query("latest_purchase", pattern="^(latest_purchase|purchase_count|points|name)$"),  # 정렬 기준
    db: AsyncSession = Depends(get_db),
    site_id: int = Depends(get_current_site_id)
):
    return await get_customer_list(db, site_id, page, limit, grade, sort_by)