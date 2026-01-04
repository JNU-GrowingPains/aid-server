from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db

from services.dashboard.repurchase_service import (
    get_repurchase_product_list,
    get_repurchase_kpis,
    get_repurchase_customer_list
)

router = APIRouter(prefix="/api/v1/repurchase-analysis", tags=["Repurchase Analysis"])

async def get_current_site_id(): return 1

@router.get("/products")
async def repurchase_product_list(db: AsyncSession = Depends(get_db), site_id: int = Depends(get_current_site_id)):
    return await get_repurchase_product_list(db, site_id)

@router.get("/kpis")
async def repurchase_kpis(
    product_ids: Optional[List[int]] = Query(None),
    db: AsyncSession = Depends(get_db),
    site_id: int = Depends(get_current_site_id)
):
    return await get_repurchase_kpis(db, site_id, product_ids)

@router.get("/customers")
async def repurchase_customer_list(
    page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
    grade: Optional[str] = Query(None), sort_by: str = Query("latest_repurchase"),
    product_ids: Optional[List[int]] = Query(None),
    db: AsyncSession = Depends(get_db), site_id: int = Depends(get_current_site_id)
):
    return await get_repurchase_customer_list(db, site_id, page, limit, grade, sort_by, product_ids)