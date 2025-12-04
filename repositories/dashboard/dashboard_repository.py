# select· join 등 SQLAlchemy ORM 쿼리 담당
# db에서 실제로 데이터를 읽고 합쳐서 쿼리하는 곳 (어떻게 가져올지)


from datetime import date
from typing import Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    OrderProduct, VisitSource, Product, Category, Event
)


# ---------- KPI Summary ----------
async def fetch_kpi_summary(db: AsyncSession, from_d: date, to_d: date):
    q_sales = (
        select(func.coalesce(func.sum(OrderProduct.order_product_amount), 0))
        .where(
            OrderProduct.order_product_date >= from_d,
            OrderProduct.order_product_date <= to_d,
        )
    )

    q_items = (
        select(func.coalesce(func.sum(OrderProduct.order_product_count), 0))
        .where(
            OrderProduct.order_product_date >= from_d,
            OrderProduct.order_product_date <= to_d,
        )
    )

    q_visits = select(func.coalesce(func.sum(VisitSource.visit_count), 0))

    sales = (await db.execute(q_sales)).scalar_one()
    items = (await db.execute(q_items)).scalar_one()
    visits = (await db.execute(q_visits)).scalar_one()

    return sales, items, visits


# ---------- Monthly Sales ----------
async def fetch_monthly_sales(db: AsyncSession, months: int):
    ym = func.date_format(OrderProduct.order_product_date, "%Y-%m")

    q = (
        select(
            ym.label("ym"),
            func.round(
                func.sum(OrderProduct.order_product_amount), 0
            ).label("sales"),
        )
        .group_by(ym)
        .order_by(desc("ym"))
        .limit(months)
    )

    return (await db.execute(q)).mappings().all()


# ---------- Top Products ----------
async def fetch_top_products(
    db: AsyncSession,
    limit: int,
    from_date: Optional[date],
    to_date: Optional[date],
    category_id: Optional[int],
):
    amount_sum = func.coalesce(
        func.sum(OrderProduct.order_product_amount), 0
    ).label("total_sales")
    qty_sum = func.coalesce(
        func.sum(OrderProduct.order_product_count), 0
    ).label("total_qty")
    last_dt = func.max(
        OrderProduct.order_product_date
    ).label("last_order_date")

    q = (
        select(
            Product.product_id.label("product_id"),
            Product.product_code,
            Product.product_name,
            Product.device,
            qty_sum,
            amount_sum,
            last_dt,
        )
        .select_from(Product)
        .join(
            OrderProduct,
            OrderProduct.product_id == Product.product_id,
            isouter=True,
        )
    )

    if from_date:
        q = q.where(OrderProduct.order_product_date >= from_date)
    if to_date:
        q = q.where(OrderProduct.order_product_date <= to_date)
    if category_id is not None:
        q = q.where(Product.category_id == category_id)

    q = (
        q.group_by(
            Product.product_id,
            Product.product_code,
            Product.product_name,
            Product.device,
        )
        .order_by(desc("total_sales"))
        .limit(limit)
    )

    return (await db.execute(q)).mappings().all()


# ---------- Device Share ----------
async def fetch_device_share(db: AsyncSession, metric: str):
    value = (
        func.coalesce(func.sum(OrderProduct.order_product_amount), 0)
        if metric == "amount"
        else func.coalesce(func.sum(OrderProduct.order_product_count), 0)
    ).label("value")

    q = (
        select(Product.device, value)
        .join(OrderProduct, OrderProduct.product_id == Product.product_id)
        .group_by(Product.device)
        .order_by(desc("value"))
    )

    return (await db.execute(q)).mappings().all()


# ---------- Orders By Category ----------
async def fetch_orders_by_category(db: AsyncSession, metric: str):
    value = (
        func.coalesce(func.sum(OrderProduct.order_product_amount), 0)
        if metric == "amount"
        else func.coalesce(func.sum(OrderProduct.order_product_count), 0)
    ).label("value")

    q = (
        select(Category.category_name, value)
        .join(Product, Product.category_id == Category.category_id)
        .join(OrderProduct, OrderProduct.product_id == Product.product_id)
        .group_by(Category.category_name)
        .order_by(desc("value"))
    )

    return (await db.execute(q)).mappings().all()


# ---------- Funnel ----------
async def fetch_funnel(
    db: AsyncSession,
    from_date: Optional[date],
    to_date: Optional[date],
):
    q = select(
        Event.event_category.label("step"),
        func.coalesce(func.sum(Event.event_count), 0).label("count"),
    ).group_by(Event.event_category)

    if from_date:
        q = q.where(Event.event_day >= from_date)
    if to_date:
        q = q.where(Event.event_day <= to_date)

    return (await db.execute(q)).mappings().all()


async def fetch_visits(db: AsyncSession):
    q = select(func.coalesce(func.sum(VisitSource.visit_count), 0))
    return (await db.execute(q)).scalar_one()
