# 비즈니스 로직
# 날짜 계산
# repository 호출


from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from . import repository


def range_from_days(days: int) -> tuple[date, date]:
    to_d = date.today()
    from_d = to_d - timedelta(days=days - 1)
    return from_d, to_d


# ---------- KPI Summary ----------
async def get_kpi_summary(db: AsyncSession, days: int):
    from_d, to_d = range_from_days(days)
    sales, items, visits = await repository.fetch_kpi_summary(db, from_d, to_d)

    return {
        "days": days,
        "sales": int(sales or 0),
        "items": int(items or 0),
        "visits": int(visits or 0)
    }


# ---------- Monthly Sales ----------
async def get_monthly_sales(db: AsyncSession, months: int):
    rows = await repository.fetch_monthly_sales(db, months)
    return list(reversed([dict(r) for r in rows]))


# ---------- Top Products ----------
async def get_top_products(db, limit, from_date, to_date, category_no):
    rows = await repository.fetch_top_products(db, limit, from_date, to_date, category_no)
    return {"items": [dict(r) for r in rows], "count": len(rows)}


# ---------- Device Share ----------
async def get_device_share(db, metric):
    rows = await repository.fetch_device_share(db, metric)
    return [dict(r) for r in rows]


# ---------- Orders By Category ----------
async def get_orders_by_category(db, metric):
    rows = await repository.fetch_orders_by_category(db, metric)
    return [dict(r) for r in rows]


# ---------- Funnel ----------
async def get_funnel(db, from_date, to_date):
    rows = await repository.fetch_funnel(db, from_date, to_date)
    data = [{"step": r["step"], "count": int(r["count"])} for r in rows]

    # 날짜 없으면 visit 추가
    if not from_date and not to_date:
        visits = await repository.fetch_visits(db)
        data.insert(0, {"step": "visit", "count": int(visits)})

    return data
