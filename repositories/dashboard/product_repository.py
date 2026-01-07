# repositories/dashboard/product_repository.py

from datetime import date
from typing import Optional
from sqlalchemy import select, func, desc, distinct, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Product, OrderProduct, Order
from config.product_groups import PRODUCT_GROUPS


# 매출/판매량 KPI (그룹화 적용, 회원만)
async def get_kpi_summary(db: AsyncSession, from_d: date, to_d: date, product_id: Optional[int] = None):
    """
    상품 그룹별 판매 통계 조회 (회원만)
    - product_id가 주어지면 해당 그룹의 모든 상품 통계를 합산
    - 총 매출액: SUM(order_product_amount)
    - 총 판매수: SUM(order_quantity)
    - 총 구매자 수: COUNT(DISTINCT user_id) - 회원만
    """
    # product_id가 주어진 경우, 그룹 내 모든 product_id 가져오기
    if product_id:
        group_ids = PRODUCT_GROUPS.get(product_id, [product_id])
    else:
        group_ids = None
    
    # 총 매출액 (그룹 내 각 상품의 가격×수량 합산)
    # product_price는 문자열이므로 숫자로 변환 후 계산
    q_sales = (
        select(func.coalesce(
            func.sum(
                OrderProduct.order_quantity * 
                func.cast(func.replace(OrderProduct.product_price, ',', ''), Integer)
            ), 0))
        .select_from(OrderProduct)
        .where(OrderProduct.order_date >= from_d, OrderProduct.order_date <= to_d)
    )
    if group_ids:
        q_sales = q_sales.where(OrderProduct.product_id.in_(group_ids))
    
    # 총 판매수 (전체 주문)
    q_items = (
        select(func.coalesce(func.sum(OrderProduct.order_quantity), 0))
        .select_from(OrderProduct)
        .where(OrderProduct.order_date >= from_d, OrderProduct.order_date <= to_d)
    )
    if group_ids:
        q_items = q_items.where(OrderProduct.product_id.in_(group_ids))
    
    # 총 구매자 수 (회원만 - user_id가 있는 주문만)
    q_buyers = (
        select(func.count(distinct(Order.user_id)))
        .select_from(OrderProduct)
        .join(Order, OrderProduct.order_id == Order.order_id)
        .where(
            OrderProduct.order_date >= from_d,
            OrderProduct.order_date <= to_d,
            Order.user_id.isnot(None)  # 회원만 (비회원 제외)
        )
    )
    if group_ids:
        q_buyers = q_buyers.where(OrderProduct.product_id.in_(group_ids))

    sales = (await db.execute(q_sales)).scalar_one()
    items = (await db.execute(q_items)).scalar_one()
    buyers = (await db.execute(q_buyers)).scalar_one()
    return sales, items, buyers


# 일별 추세 그래프 (그룹화 적용)
async def get_daily_trend(db: AsyncSession, from_d: date, to_d: date, metric: str, product_id: Optional[int] = None):
    """
    일별 판매 추세 조회 (그룹화 적용)
    - product_id가 주어지면 해당 그룹의 모든 상품 통계를 합산
    - metric: "buyers" (구매자 수), "quantity" (판매 수량), "amount" (매출액)
    - from_d, to_d: 조회 기간
    """
    # product_id가 주어진 경우, 그룹 내 모든 product_id 가져오기
    if product_id:
        group_ids = PRODUCT_GROUPS.get(product_id, [product_id])
    else:
        group_ids = None
    
    # metric에 따라 집계 컬럼 선택
    if metric == "buyers":  # 구매자 수 (회원만)
        col = func.count(distinct(Order.user_id)).label("value")
    elif metric == "quantity":  # 판매 수량
        col = func.sum(OrderProduct.order_quantity).label("value")
    else:  # amount (매출액, 기본값) - 가격×수량으로 계산
        col = func.sum(
            OrderProduct.order_quantity * 
            func.cast(func.replace(OrderProduct.product_price, ',', ''), Integer)
        ).label("value")

    q = select(OrderProduct.order_date.label("date"), col)
    
    # buyers의 경우 Order 테이블 JOIN 및 회원만 필터링
    if metric == "buyers":
        q = q.join(Order, OrderProduct.order_id == Order.order_id)
        q = q.where(Order.user_id.isnot(None))  # 회원만
    
    # 날짜 범위 필터 (필수!)
    q = q.where(OrderProduct.order_date >= from_d)
    q = q.where(OrderProduct.order_date <= to_d)
    
    # 그룹 내 모든 상품 필터 (그룹화 적용)
    if group_ids:
        q = q.where(OrderProduct.product_id.in_(group_ids))

    q = q.group_by(OrderProduct.order_date).order_by(OrderProduct.order_date)
    return (await db.execute(q)).all()


# 상품 목록 (Top Products) - 그룹 대표 상품만 (판매 통계 제외)
async def get_top_products(db: AsyncSession, limit: int, from_date: Optional[date], to_date: Optional[date]):
    """
    그룹화된 대표 상품 목록만 조회 (판매 통계 제외)
    - 각 그룹의 대표 product_id
    - 대표 상품의 이름은 config에서, 가격은 DB에서 가져옴
    - 판매 분석은 별도 API에서 처리
    """
    # 1. 모든 그룹의 대표 product_id 목록 (제외 상품 필터링)
    from config.product_groups import EXCLUDED_PRODUCTS, PRODUCT_GROUP_NAMES
    representative_ids = [pid for pid in PRODUCT_GROUPS.keys() if pid not in EXCLUDED_PRODUCTS]
    
    # 2. 대표 상품 정보 조회 (가격만 DB에서 가져옴)
    query = (
        select(
            Product.product_id,
            Product.product_no.label("product_code"),
            Product.product_price.label("price")
        )
        .where(Product.product_id.in_(representative_ids))
    )
    
    result = await db.execute(query)
    products = []
    
    for row in result.all():
        # 상품명은 config에서 가져오고, 가격은 DB에서 가져옴
        display_name = PRODUCT_GROUP_NAMES.get(row.product_id, f"상품 {row.product_id}")
        products.append({
            "product_id": row.product_id,
            "product_code": row.product_code,
            "product_name": display_name,  # config에서 설정한 이름 사용
            "price": row.price
        })
    
    # 3. limit 적용 (기본적으로 10개 그룹이므로 모두 반환)
    return products[:limit]


async def get_product_by_id(db: AsyncSession, product_id: int):
    """product_id로 상품 조회"""
    query = select(Product).where(Product.product_id == product_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

