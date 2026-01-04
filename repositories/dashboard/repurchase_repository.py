# repositories/dashboard/repurchase_repository.py

from typing import Optional, List
from sqlalchemy import select, func, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Member, MemberGroup, Order, OrderProduct, Product


async def fetch_repurchase_product_list(db: AsyncSession, site_id: int):
    q = (
        select(distinct(Product.product_id), Product.product_name)
        .join(OrderProduct, Product.product_id == OrderProduct.product_id)
        .where(Product.site_id == site_id)
    )
    return (await db.execute(q)).all()


async def fetch_repurchase_kpi(db: AsyncSession, site_id: int, product_ids: Optional[List[int]] = None):
    # 전체 회원 수
    q_total = select(func.count(Member.user_id)).where(Member.site_id == site_id)

    # 재구매 회원 수 (숫자인 user_id로 조인)
    q_re = (
        select(Order.user_id)
        .join(Member, Order.user_id == Member.user_id)
        .where(Member.site_id == site_id)
    )
    if product_ids:
        q_re = q_re.join(OrderProduct, Order.order_no == OrderProduct.order_no).where(
            OrderProduct.product_id.in_(product_ids))

    q_re = q_re.group_by(Order.member_id).having(func.count(distinct(Order.order_no)) >= 2)

    total = (await db.execute(q_total)).scalar() or 1
    re_cnt = len((await db.execute(q_re)).all())
    return total, re_cnt


async def fetch_repurchase_user_list(
        db: AsyncSession, site_id: int, page: int, limit: int,
        grade: Optional[str], sort_by: str, product_ids: Optional[List[int]]
):
    subq_phone = select(Order.order_phone_number).where(Order.user_id == Member.user_id).order_by(
        desc(Order.order_date)).limit(1).scalar_subquery()
    subq_email = select(Order.order_email).where(Order.user_id == Member.user_id).order_by(
        desc(Order.order_date)).limit(1).scalar_subquery()
    subq_addr = select(func.concat(Order.order_address_1, " ", Order.order_address_2)).where(
        Order.user_id == Member.user_id).order_by(desc(Order.order_date)).limit(1).scalar_subquery()

    q = (
        select(
            Member.user_id, Member.member_id.label("name"), MemberGroup.group_name.label("grade"),
            Member.available_points.label("point"), subq_phone.label("phone"), subq_email.label("email"),
            subq_addr.label("address"),
            func.count(distinct(Order.order_no)).label("purchase_count"),
            func.max(Order.order_date).label("last_purchase_date"),
            func.min(Order.order_date).label("first_purchase_date")
        )
        .join(MemberGroup, Member.group_id == MemberGroup.group_id)
        .join(Order, Member.user_id == Order.user_id)
        .where(Member.site_id == site_id)
    )

    if product_ids:
        q = q.join(OrderProduct, Order.order_no == OrderProduct.order_no).where(
            OrderProduct.product_id.in_(product_ids))

    q = q.group_by(Member.user_id, Member.member_id, MemberGroup.group_name, Member.available_points).having(
        func.count(distinct(Order.order_no)) >= 2)

    if sort_by == "purchase_count":
        q = q.order_by(desc("purchase_count"))
    elif sort_by == "points":
        q = q.order_by(desc("point"))
    elif sort_by == "name":
        q = q.order_by(Member.member_id)
    else:
        q = q.order_by(desc("last_purchase_date"))

    full_rows = (await db.execute(q)).all()
    paged_rows = full_rows[(page - 1) * limit: (page - 1) * limit + limit]
    return paged_rows, len(full_rows)


async def fetch_user_detail(db: AsyncSession, user_id: int):
    q = select(Member, MemberGroup).join(MemberGroup, Member.group_id == MemberGroup.group_id).where(
        Member.user_id == user_id)
    return (await db.execute(q)).first()


async def fetch_user_top_products(db: AsyncSession, user_id: int):
    q = (
        select(Product.product_name, func.count(OrderProduct.order_product_no).label("cnt"))
        .join(OrderProduct, Product.product_id == OrderProduct.product_id)
        .join(Order, OrderProduct.order_no == Order.order_no)
        .where(Order.user_id == user_id)
        .group_by(Product.product_name).order_by(desc("cnt")).limit(5)
    )
    return (await db.execute(q)).all()