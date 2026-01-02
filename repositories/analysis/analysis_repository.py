from sqlalchemy import select, func, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User, Order, OrderProduct, Product


# -----------------------------
# 1. 고객 분석 (Customer Analysis)
# -----------------------------

# 고객 등급 분포 (막대 그래프)
async def fetch_customer_grade_dist(db: AsyncSession, site_id: int):
    q = (
        select(User.grade, func.count(User.user_id).label("count"))
        .where(User.site_id == site_id)
        .group_by(User.grade)
    )
    return (await db.execute(q)).all()


# 포인트 상위 고객 (Top 3)
async def fetch_top_point_users(db: AsyncSession, site_id: int):
    # 구매 횟수도 같이 가져오기 위해 Order 조인
    q = (
        select(
            User.name,
            User.email,
            User.grade,
            User.point,
            func.count(Order.order_id).label("order_count")
        )
        .outerjoin(Order, User.user_id == Order.user_id)
        .where(User.site_id == site_id)
        .group_by(User.user_id)
        .order_by(desc(User.point))
        .limit(3)
    )
    return (await db.execute(q)).all()


# 고객 리스트 (테이블)
async def fetch_customer_list(db: AsyncSession, site_id: int, limit: int = 20):
    # 유저별 구매횟수, 최근구매일 등 집계
    q = (
        select(
            User.user_id,
            User.name,
            User.grade,
            User.point,
            func.count(Order.order_id).label("purchase_count"),
            func.max(Order.order_date).label("last_purchase"),
            func.min(Order.order_date).label("first_purchase"),
        )
        .outerjoin(Order, User.user_id == Order.user_id)
        .where(User.site_id == site_id)
        .group_by(User.user_id)
        .order_by(desc("last_purchase"))  # 최근 구매일 순
        .limit(limit)
    )
    return (await db.execute(q)).all()


# -----------------------------
# 2. 재구매 분석 (Repurchase Analysis)
# -----------------------------

# 재구매 KPI (총 재구매 수, 재구매율 등)
async def fetch_repurchase_kpi(db: AsyncSession, site_id: int):
    # 1. 전체 구매자 수
    q_total_users = select(func.count(User.user_id)).where(User.site_id == site_id)

    # 2. 재구매 유저 수 (구매 횟수 2회 이상)
    # Having 절 사용
    q_re_users = (
        select(User.user_id)
        .join(Order, User.user_id == Order.user_id)
        .where(User.site_id == site_id)
        .group_by(User.user_id)
        .having(func.count(Order.order_id) >= 2)
    )

    total_cnt = (await db.execute(q_total_users)).scalar() or 1
    re_users_result = (await db.execute(q_re_users)).all()
    re_cnt = len(re_users_result)

    return total_cnt, re_cnt


# 재구매 고객 리스트 (화면 하단 테이블)
async def fetch_repurchase_user_list(db: AsyncSession, site_id: int):
    # 구매 횟수가 2회 이상인 사람만 필터링
    q = (
        select(
            User.user_id,
            User.name,
            User.grade,
            User.phone,
            User.email,
            User.point,
            User.address,  # 거주지
            func.count(Order.order_id).label("purchase_count"),
            func.max(Order.order_date).label("last_purchase_date"),
            func.min(Order.order_date).label("first_purchase_date")
        )
        .join(Order, User.user_id == Order.user_id)
        .where(User.site_id == site_id)
        .group_by(User.user_id)
        .having(func.count(Order.order_id) >= 2)  # 재구매 조건
        .order_by(desc("last_purchase_date"))
        .limit(10)
    )
    return (await db.execute(q)).all()


# -----------------------------
# 3. 개인별 상세 분석 (Modal)
# -----------------------------
# 특정 고객의 재구매 상품 TOP 5
async def fetch_user_top_products(db: AsyncSession, user_id: int):
    q = (
        select(Product.product_name, func.count(OrderProduct.order_product_id).label("cnt"))
        .join(OrderProduct, Product.product_id == OrderProduct.product_id)
        .join(Order, OrderProduct.order_id == Order.order_id)
        .where(Order.user_id == user_id)
        .group_by(Product.product_name)
        .order_by(desc("cnt"))
        .limit(7)  # 화면에 7개 정도 나옴
    )
    return (await db.execute(q)).all()


# 특정 고객 정보 (모달 상단용)
async def fetch_user_detail(db: AsyncSession, user_id: int):
    q = select(User).where(User.user_id == user_id)
    return (await db.execute(q)).scalar_one_or_none()