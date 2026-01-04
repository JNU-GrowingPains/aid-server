# services/dashboard/customer_service.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.dashboard import customer_repository as repo

async def get_customer_kpi(db: AsyncSession, site_id: int):
    total, new_u, vip = await repo.fetch_customer_kpi(db, site_id)
    return {"total_customers": total, "new_customers": new_u, "vip_customers": vip}

async def get_customer_grade_counts(db: AsyncSession, site_id: int):
    rows = await repo.fetch_customer_grade_dist(db, site_id)
    result = {"ALL": 0}
    for r in rows:
        result[r.grade] = r.count
        result["ALL"] += r.count
    return result

async def get_customer_list(db: AsyncSession, site_id: int, page: int, limit: int, grade: Optional[str], sort_by: str):
    rows, total_count = await repo.fetch_customer_list(db, site_id, page, limit, grade, sort_by)
    items = [{
        "user_id": r.user_id, "customer_id": r.name, "name": r.name, "grade": r.grade,
        "purchase_count": f"{r.purchase_count}회", "first_purchase": r.first_purchase or "-",
        "last_purchase": r.last_purchase or "-", "coupon_used": "미사용", "points": f"{r.point or 0:,}P"
    } for r in rows]
    return {"total_count": total_count, "page": page, "limit": limit, "items": items}