# services/dashboard_service.py : 날짜계산,리스트/딕셔너리 가공,레포지토리 호출


from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.dashboard import dashboard_repository as repo


def range_from_days(days: int) -> tuple[date, date]:
    to_d = date.today()
    from_d = to_d - timedelta(days=days - 1)
    return from_d, to_d


# KPI Summary
async def get_kpi_summary(db: AsyncSession, days: int):
    from_d, to_d = range_from_days(days)
    sales, items, visits = await repo.fetch_kpi_summary(db, from_d, to_d)

    return {
        "days": days,
        "sales": int(sales or 0),
        "items": int(items or 0),
        "visits": int(visits or 0),
    }


# Monthly Sales
async def get_monthly_sales(db: AsyncSession, months: int):
    rows = await repo.fetch_monthly_sales(db, months)
    return list(reversed([dict(r) for r in rows]))


# Top Products
async def get_top_products(
    db: AsyncSession,
    limit: int,
    from_date: Optional[date],
    to_date: Optional[date],
    category_id: Optional[int],
):
    rows = await repo.fetch_top_products(
        db, limit, from_date, to_date, category_id
    )
    return {"items": [dict(r) for r in rows], "count": len(rows)}


# Device Share
async def get_device_share(db: AsyncSession, metric: str):
    rows = await repo.fetch_device_share(db, metric)
    return [dict(r) for r in rows]


# Orders By Category
async def get_orders_by_category(db: AsyncSession, metric: str):
    rows = await repo.fetch_orders_by_category(db, metric)
    return [dict(r) for r in rows]


# Funnel
async def get_funnel(
    db: AsyncSession,
    from_date: Optional[date],
    to_date: Optional[date],
):
    rows = await repo.fetch_funnel(db, from_date, to_date)
    data = [{"step": r["step"], "count": int(r["count"])} for r in rows]

    if not from_date and not to_date:
        visits = await repo.fetch_visits(db)
        data.insert(0, {"step": "visit", "count": int(visits)})

    return data
