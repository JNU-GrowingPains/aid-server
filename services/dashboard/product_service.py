# services/dashboard/product_service.py

from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.dashboard import product_repository as repo

def range_from_days(days: int) -> tuple[date, date]:
    to_d = date.today()
    from_d = to_d - timedelta(days=days - 1)
    return from_d, to_d

async def get_kpi_summary(db: AsyncSession, days: int, product_id: Optional[int] = None, from_date: Optional[date] = None, to_date: Optional[date] = None):
    """
    상품 KPI 조회
    - from_date, to_date가 있으면 해당 기간 사용
    - 없으면 days로 계산
    """
    if from_date and to_date:
        from_d, to_d = from_date, to_date
    else:
        from_d, to_d = range_from_days(days)
    
    # 실제 일수 계산 (시작일 포함)
    actual_days = (to_d - from_d).days + 1
    
    sales, items, buyers = await repo.get_kpi_summary(db, from_d, to_d, product_id)
    return {"days": actual_days, "sales": int(sales or 0), "items": int(items or 0), "buyers": int(buyers or 0)}

async def get_daily_trend(db: AsyncSession, days: int, metric: str, product_id: Optional[int] = None, from_date: Optional[date] = None, to_date: Optional[date] = None):
    """
    일별 트렌드 조회
    - from_date, to_date가 있으면 해당 기간 사용
    - 없으면 days로 계산
    """
    if from_date and to_date:
        from_d, to_d = from_date, to_date
    else:
        from_d, to_d = range_from_days(days)
    
    rows = await repo.get_daily_trend(db, from_d, to_d, metric, product_id)
    return [{"date": r.date, "value": int(r.value) if r.value else 0} for r in rows]

async def get_top_products(db: AsyncSession, limit: int, from_date: Optional[date], to_date: Optional[date]):
    rows = await repo.get_top_products(db, limit, from_date, to_date)
    return {"items": [dict(r) for r in rows], "count": len(rows)}
