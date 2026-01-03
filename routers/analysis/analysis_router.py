from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services.analysis import analysis_service

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# 임시 site_id 의존성 (나중에 Auth랑 합치세요)
async def get_current_site_id():
    return 1

# 1. 고객 분석 대시보드 데이터
@router.get("/customers")
async def customer_dashboard(
    db: AsyncSession = Depends(get_db),
    site_id: int = Depends(get_current_site_id)
):
    return await analysis_service.get_customer_analysis(db, site_id)

# 2. 재구매 분석 대시보드 데이터
@router.get("/repurchase")
async def repurchase_dashboard(
    db: AsyncSession = Depends(get_db),
    site_id: int = Depends(get_current_site_id)
):
    return await analysis_service.get_repurchase_analysis(db, site_id)

# 3. 특정 고객 상세 분석 (모달창용)
@router.get("/repurchase/user/{user_id}")
async def user_detail_modal(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await analysis_service.get_user_detail_analysis(db, user_id)