# services/dashboard/product_service.py

from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.dashboard import product_repository as repo

def range_from_days(days: int) -> tuple[date, date]:
    to_d = date.today()
    from_d = to_d - timedelta(days=days - 1)
    return from_d, to_d

async def get_kpi_summary(db: AsyncSession, days: int, product_id: Optional[int] = None):
    from_d, to_d = range_from_days(days)
    sales, items, buyers = await repo.fetch_kpi_summary(db, from_d, to_d, product_id)
    return {"days": days, "sales": int(sales or 0), "items": int(items or 0), "buyers": int(buyers or 0)}

async def get_daily_trend(db: AsyncSession, days: int, metric: str, product_id: Optional[int] = None):
    rows = await repo.fetch_daily_trend(db, days, metric, product_id)
    return [{"date": r.date, "value": int(r.value) if r.value else 0} for r in rows]

async def get_top_products(db: AsyncSession, limit: int, from_date: Optional[date], to_date: Optional[date]):
    rows = await repo.fetch_top_products(db, limit, from_date, to_date)
    return {"items": [dict(r) for r in rows], "count": len(rows)}
