# repositories/dashboard/product_repository.py

from datetime import date
from typing import Optional
from sqlalchemy import select, func, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Product, OrderProduct, Order


# 매출/판매량 KPI
async def fetch_kpi_summary(db: AsyncSession, from_d: date, to_d: date, product_id: Optional[int] = None):
    q_sales = select(func.coalesce(func.sum(OrderProduct.order_product_amount), 0))
    q_items = select(func.coalesce(func.sum(OrderProduct.order_product_count), 0))
    # user_id가 있는 경우만 구매자로 카운트
    q_buyers = select(func.count(distinct(Order.user_id))).join(OrderProduct, OrderProduct.order_no == Order.order_no)

    def apply(q):
        q = q.where(OrderProduct.order_date >= from_d, OrderProduct.order_date <= to_d)
        if product_id: q = q.where(OrderProduct.product_id == product_id)
        return q

    sales = (await db.execute(apply(q_sales))).scalar_one()
    items = (await db.execute(apply(q_items))).scalar_one()
    buyers = (await db.execute(apply(q_buyers))).scalar_one()
    return sales, items, buyers


# 일별 추세 그래프
async def fetch_daily_trend(db: AsyncSession, days: int, metric: str, product_id: Optional[int] = None):
    if metric == "buyer":
        col = func.count(distinct(Order.user_id)).label("value")
    elif metric == "count":
        col = func.sum(OrderProduct.order_product_count).label("value")
    else:
        col = func.sum(OrderProduct.order_product_amount).label("value")

    q = select(OrderProduct.order_date.label("date"), col)
    if metric == "buyer": q = q.join(Order, OrderProduct.order_no == Order.order_no)
    if product_id: q = q.where(OrderProduct.product_id == product_id)

    q = q.group_by(OrderProduct.order_date).order_by(OrderProduct.order_date).limit(days)
    return (await db.execute(q)).all()


# 상품 목록 (Top Products)
async def fetch_top_products(db: AsyncSession, limit: int, from_date: Optional[date], to_date: Optional[date]):
    amount = func.coalesce(func.sum(OrderProduct.order_product_amount), 0).label("total_sales")
    qty = func.coalesce(func.sum(OrderProduct.order_product_count), 0).label("total_qty")
    last_dt = func.max(OrderProduct.order_date).label("last_order_date")

    q = (
        select(Product.product_id.label("product_id"), Product.product_no.label("product_code"),
               Product.product_name, Product.product_price.label("price"), qty, amount, last_dt)
        .select_from(Product)
        .join(OrderProduct, OrderProduct.product_id == Product.product_id, isouter=True)
    )
    if from_date: q = q.where(OrderProduct.order_date >= from_date)
    if to_date: q = q.where(OrderProduct.order_date <= to_date)

    q = q.group_by(Product.product_id, Product.product_no, Product.product_name, Product.product_price).order_by(
        desc("total_sales")).limit(limit)
    return (await db.execute(q)).mappings().all()

