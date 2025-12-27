# select· join 등 SQLAlchemy ORM 쿼리 담당
# db에서 실제로 데이터를 읽고 합쳐서 쿼리하는 곳 (어떻게 가져올지)


from datetime import date
from typing import Optional

from sqlalchemy import select, func, desc, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    OrderProduct, VisitSource, Product, Category, Event, Review, Order
)


# ---------- KPI Summary ----------
async def fetch_kpi_summary(db: AsyncSession, from_d: date, to_d: date):
    # 1. 총 매출액
    q_sales = (
        select(func.coalesce(func.sum(OrderProduct.order_product_amount), 0))
        .where(
            OrderProduct.order_product_date >= from_d,
            OrderProduct.order_product_date <= to_d,
        )
    )

    # 2. 총 판매 수
    q_items = (
        select(func.coalesce(func.sum(OrderProduct.order_product_count), 0))
        .where(
            OrderProduct.order_product_date >= from_d,
            OrderProduct.order_product_date <= to_d,
        )
    )

    # 3. 총 구매자 수
    q_buyers = (
        select(func.count(distinct(Order.user_id)))
        .join(OrderProduct, OrderProduct.order_id == Order.order_id)
        .where(
            OrderProduct.order_product_date >= from_d,
            OrderProduct.order_product_date <= to_d,
        )
    )

    sales = (await db.execute(q_sales)).scalar_one()
    items = (await db.execute(q_items)).scalar_one()
    buyers = (await db.execute(q_buyers)).scalar_one()

    return sales, items, buyers


# ---------- Daily Trend ----------
async def fetch_daily_trend(db: AsyncSession, days: int, metric: str):

    # 1. 컬럼 선택
    if metric == "buyer":
        target_col = func.count(distinct(Order.user_id)).label("value")
    elif metric == "count":
        target_col = func.sum(OrderProduct.order_product_count).label("value")
    else:
        target_col = func.sum(OrderProduct.order_product_amount).label("value")

    # 2. 쿼리 생성
    q = select(
        OrderProduct.order_product_date.label("date"),
        target_col
    )

    if metric == "buyer":
        q = q.join(Order, OrderProduct.order_id == Order.order_id)

    q = (
        q.group_by(OrderProduct.order_product_date)
        .order_by(OrderProduct.order_product_date)
        .limit(days) # 최근 N일
    )

    return (await db.execute(q)).all()


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
            Product.price,
            Product.stock,
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
            Product.price,
            Product.stock,
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


# ---------- Review Stats ----------
async def fetch_review_stats(db: AsyncSession):
    # 1. 전체 통계
    q_stats = select(
        func.count(Review.review_id).label("total_reviews"),
        func.avg(Review.rating).label("avg_rating"),
        func.sum(case((Review.sentiment == '긍정', 1), else_=0)).label("positive_cnt"),
        func.sum(case((Review.sentiment == '부정', 1), else_=0)).label("negative_cnt")
    )

    # 2. 부정 리뷰 Top 3 (최신순)
    q_bad_reviews = (
        select(Review)
        .where(Review.sentiment == '부정')
        .order_by(Review.created_at.desc())
        .limit(3)
    )

    stats = (await db.execute(q_stats)).one()
    bad_reviews = (await db.execute(q_bad_reviews)).scalars().all()

    return stats, bad_reviews


# ---------- All Review Texts (워드클라우드) ----------
async def fetch_all_review_texts(db: AsyncSession):
    q = select(Review.content)
    return (await db.execute(q)).scalars().all()

