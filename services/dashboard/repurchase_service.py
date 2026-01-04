# services/dashboard/repurchase_service.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.dashboard import repurchase_repository as repo

async def get_repurchase_product_list(db: AsyncSession, site_id: int):
    rows = await repo.fetch_repurchase_product_list(db, site_id)
    return [{"product_id": r.product_id, "product_name": r.product_name} for r in rows]

async def get_repurchase_kpis(db: AsyncSession, site_id: int, product_ids: Optional[List[int]] = None):
    total, re_cnt = await repo.fetch_repurchase_kpi(db, site_id, product_ids)
    rate = round((re_cnt / total * 100), 1) if total > 0 else 0
    return {"total_repurchase_count": re_cnt, "avg_repurchase_rate": rate,
            # 밑에 세개는 일단 하드코딩 유지 (초기 개발 단계에서 소프트코딩 하기에 시간 오래걸림)
            "avg_repurchase_days": 30, "same_product_rate": 49.1, "sales_contribution": 75.0}

async def get_repurchase_customer_list(db: AsyncSession, site_id: int, page: int, limit: int, grade: Optional[str], sort_by: str, product_ids: Optional[List[int]] = None):
    rows, total_count = await repo.fetch_repurchase_user_list(db, site_id, page, limit, grade, sort_by, product_ids)
    items = []
    for r in rows:
        period = 0
        if r.purchase_count > 1 and r.last_purchase_date and r.first_purchase_date:
            period = (r.last_purchase_date - r.first_purchase_date).days // (r.purchase_count - 1)
        items.append({
            "user_id": r.user_id, "customer_id": r.member_id, "name": r.member_id, "grade": r.grade,
            "purchase_count": f"{r.purchase_count}회", "address": r.address or "-", "phone": r.phone or "-",
            "email": r.email or "-", "point": f"{r.point or 0:,}P", "avg_period": f"{period}일"
        })
    return {"total_count": total_count, "page": page, "limit": limit, "items": items}

async def get_user_detail_analysis(db: AsyncSession, user_id: int):
    row = await repo.fetch_user_detail(db, user_id)
    if not row: return None
    member, group = row
    products = await repo.fetch_user_top_products(db, user_id)
    return {
        "user_info": {"name": member.member_id, "grade": group.group_name, "point": member.available_points, "purchase_count": 0},
        "top_products": [{"name": p.product_name, "count": p.cnt} for p in products],
        "location_stat": [{"name": "등록된 주소 없음", "value": 100}]
    }