# repositories/dashboard/customer_repository.py

from typing import Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Member, MemberGroup, Order


async def fetch_customer_kpi(db: AsyncSession, site_id: int):
    q_total = select(func.count(Member.member_id)).where(Member.site_id == site_id)
    q_vip = (
        select(func.count(Member.member_id))
        .join(MemberGroup, Member.group_id == MemberGroup.group_id)
        .where(Member.site_id == site_id, MemberGroup.group_name == 'VIP')
    )
    total = (await db.execute(q_total)).scalar() or 0
    vip = (await db.execute(q_vip)).scalar() or 0
    return total, 0, vip


async def fetch_customer_grade_dist(db: AsyncSession, site_id: int):
    q = (
        select(MemberGroup.group_name.label("grade"), func.count(Member.member_id).label("count"))
        .join(Member, Member.group_id == MemberGroup.group_id)
        .where(Member.site_id == site_id)
        .group_by(MemberGroup.group_name)
    )
    return (await db.execute(q)).all()


async def fetch_customer_list(db: AsyncSession, site_id: int, page: int, limit: int, grade: Optional[str],
                              sort_by: str):
    q = (
        select(
            Member.user_id, Member.member_id.label("name"), MemberGroup.group_name.label("grade"),
            Member.available_points.label("point"),
            func.count(Order.order_no).label("purchase_count"),
            func.max(Order.order_date).label("last_purchase"),
            func.min(Order.order_date).label("first_purchase"),
        )
        .join(MemberGroup, Member.group_id == MemberGroup.group_id)
        .outerjoin(Order, Member.user_id == Order.user_id)
        .where(Member.site_id == site_id)
        .group_by(Member.user_id, Member.member_id, MemberGroup.group_name, Member.available_points)
    )
    if grade and grade != "전체": q = q.where(MemberGroup.group_name == grade)

    if sort_by == "purchase_count":
        q = q.order_by(desc("purchase_count"))
    elif sort_by == "points":
        q = q.order_by(desc("point"))
    elif sort_by == "name":
        q = q.order_by(Member.member_id)
    else:
        q = q.order_by(desc("last_purchase"))

    full_rows = (await db.execute(q)).all()
    paged_rows = full_rows[(page - 1) * limit: (page - 1) * limit + limit]
    return paged_rows, len(full_rows)