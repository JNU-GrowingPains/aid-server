# repositories/dashboard/repurchase_repository.py

from typing import Optional, List
from sqlalchemy import select, func, desc, distinct, and_, or_, text, BigInteger, String, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Member, MemberGroup, Order, OrderProduct, Product
from config.product_groups import PRODUCT_GROUPS, PRODUCT_GROUP_NAMES


async def get_repurchase_product_list(db: AsyncSession):
    """
    그룹화된 대표 상품 목록 반환
    PRODUCT_GROUPS의 키(대표 product_id)만 반환
    제외 상품(18, 19 등) 필터링 적용
    커스텀 상품명 적용
    """
    from config.product_groups import EXCLUDED_PRODUCTS
    representative_ids = [pid for pid in PRODUCT_GROUPS.keys() if pid not in EXCLUDED_PRODUCTS]
    
    q = (
        select(
            Product.product_id,
            Product.product_name,
            Product.product_price
        )
        .where(Product.product_id.in_(representative_ids))
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    # 커스텀 상품명 적용
    return [
        {
            "product_id": row.product_id,
            "product_name": PRODUCT_GROUP_NAMES.get(row.product_id, row.product_name),
            "product_price": row.product_price
        }
        for row in rows
    ]


async def get_repurchase_kpis(db: AsyncSession, product_ids: Optional[List[int]] = None):
    """
    재구매 KPI 계산
    - 비회원 포함: member_id가 __guest__:로 시작하면 billing_name + order_address_1로 식별
    - 그룹화 적용: product_ids에 해당하는 그룹 내 모든 상품 포함
    - 그룹 내 상품끼리의 재구매는 "동일 상품 재구매"로 계산
    
    반환 KPI:
    1. total_repurchase_count: 총 재구매 수 (첫 구매를 제외한 모든 주문 수)
    2. avg_repurchase_rate: 평균 재구매율 (재구매 고객 수 / 전체 고객 수 × 100)
    3. avg_repurchase_days: 재구매까지 걸린 평균 기간 (일)
    4. same_product_rate: 동일 상품 재구매 비율 (%)
    5. sales_contribution: 재구매 고객 매출 기여도 (%)
    """
    
    # 1. product_ids가 주어진 경우, 그룹 내 모든 상품 ID 포함
    target_product_ids = []
    if product_ids:
        for pid in product_ids:
            group_ids = PRODUCT_GROUPS.get(pid, [pid])
            target_product_ids.extend(group_ids)
    
    # 2. product_id → group_id 역매핑 생성 (그룹 내 상품끼리 동일 상품으로 판단하기 위함)
    product_to_group = {}
    for group_id, member_ids in PRODUCT_GROUPS.items():
        for member_id in member_ids:
            product_to_group[member_id] = group_id
    
    # 3. SQL CTE로 product_groups 매핑 테이블 생성
    if product_to_group:
        product_groups_cte = f"product_groups AS (\n{' UNION ALL '.join([f'SELECT {pid} AS product_id, {gid} AS group_id' for pid, gid in product_to_group.items()])}\n),"
    else:
        product_groups_cte = ""
    
    # 4. 고객별 주문-상품 조합 추출 (비회원 포함)
    # customer_key: 회원은 user_id, 비회원은 "billing_name|order_address_1"
    customer_purchases_query = text(f"""
        WITH {product_groups_cte}
        customer_purchases AS (
            SELECT 
                CAST(CASE 
                    WHEN o.member_id LIKE '__guest__%' 
                    THEN CONCAT(o.billing_name, '|', o.order_address_1)
                    ELSE CAST(o.user_id AS CHAR)
                END AS CHAR CHARSET utf8mb4) COLLATE utf8mb4_unicode_ci AS customer_key,
                o.order_id,
                o.order_date,
                op.product_id,
                {"COALESCE(pg.group_id, op.product_id)" if product_groups_cte else "op.product_id"} AS group_id,
                o.payment_amount,
                o.member_id
            FROM orders o
            JOIN order_products op ON o.order_id = op.order_id
            {"LEFT JOIN product_groups pg ON op.product_id = pg.product_id" if product_groups_cte else ""}
            WHERE 1=1
                {f"AND op.product_id IN ({','.join(map(str, target_product_ids))})" if target_product_ids else ""}
        ),
        -- 5. 재구매 쌍 생성 (첫 구매 → 재구매)
        repurchase_pairs AS (
            SELECT 
                cp1.customer_key,
                cp1.product_id AS first_product_id,
                cp2.product_id AS repurchase_product_id,
                cp1.group_id AS first_group_id,
                cp2.group_id AS repurchase_group_id,
                cp1.order_date AS first_order_date,
                cp2.order_date AS repurchase_order_date,
                DATEDIFF(cp2.order_date, cp1.order_date) AS days_between,
                cp2.payment_amount AS repurchase_amount,
                cp1.member_id,
                cp2.member_id AS repurchase_member_id
            FROM customer_purchases cp1
            JOIN customer_purchases cp2 
                ON cp1.customer_key = cp2.customer_key
                AND cp1.order_date < cp2.order_date
        )
        SELECT 
            -- A. 총 재구매 수 (첫 구매를 제외한 모든 주문 수)
            (SELECT COUNT(*) FROM customer_purchases) - (SELECT COUNT(DISTINCT customer_key) FROM customer_purchases) AS total_repurchase_count,
            
            -- B. 전체 고객 수 (재구매율 계산용)
            (SELECT COUNT(DISTINCT customer_key) FROM customer_purchases) AS total_customers,
            
            -- C. 재구매 고객 수 (재구매율 계산용)
            COUNT(DISTINCT customer_key) AS repurchase_customer_count,
            
            -- D. 평균 재구매 소요 기간
            AVG(days_between) AS avg_repurchase_days,
            
            -- E. 동일 상품 재구매 건수 (같은 그룹끼리도 동일 상품으로 계산)
            SUM(CASE WHEN first_group_id = repurchase_group_id THEN 1 ELSE 0 END) AS same_product_count,
            
            -- F. 전체 재구매 쌍 수
            COUNT(*) AS total_pairs
        FROM repurchase_pairs
    """)
    
    result = await db.execute(customer_purchases_query)
    row = result.first()
    
    if not row or row.repurchase_customer_count == 0:
        return {
            "total_repurchase_count": 0,
            "avg_repurchase_rate": 0.0,
            "avg_repurchase_days": 0,
            "same_product_rate": 0.0,
            "sales_contribution": 0.0
        }
    
    # 재구매율 계산 (재구매 고객 수 / 전체 고객 수)
    avg_repurchase_rate = (row.repurchase_customer_count / row.total_customers * 100) if row.total_customers > 0 else 0.0
    
    # 동일 상품 재구매 비율
    same_product_rate = (row.same_product_count / row.total_pairs * 100) if row.total_pairs > 0 else 0.0
    
    # 재구매 고객 매출 기여도 계산
    sales_contribution_query = text("""
        WITH customer_purchases AS (
            SELECT 
                CAST(CASE 
                    WHEN o.member_id LIKE '__guest__%' 
                    THEN CONCAT(o.billing_name, '|', o.order_address_1)
                    ELSE CAST(o.user_id AS CHAR)
                END AS CHAR CHARSET utf8mb4) COLLATE utf8mb4_unicode_ci AS customer_key,
                o.order_id,
                o.order_date,
                op.product_id,
                o.payment_amount
            FROM orders o
            JOIN order_products op ON o.order_id = op.order_id
            WHERE 1=1
                {product_filter}
        ),
        repurchase_customers AS (
            SELECT DISTINCT cp1.customer_key
            FROM customer_purchases cp1
            JOIN customer_purchases cp2 
                ON cp1.customer_key = cp2.customer_key
                AND cp1.order_date < cp2.order_date
        )
        SELECT 
            SUM(CASE WHEN rc.customer_key IS NOT NULL THEN o.payment_amount ELSE 0 END) AS repurchase_sales,
            SUM(o.payment_amount) AS total_sales
        FROM orders o
        LEFT JOIN (
            SELECT 
                CAST(CASE 
                    WHEN member_id LIKE '__guest__%' 
                    THEN CONCAT(billing_name, '|', order_address_1)
                    ELSE CAST(user_id AS CHAR)
                END AS CHAR CHARSET utf8mb4) COLLATE utf8mb4_unicode_ci AS customer_key,
                order_id
            FROM orders
        ) o_key ON o.order_id = o_key.order_id
        LEFT JOIN repurchase_customers rc ON o_key.customer_key = rc.customer_key
    """.replace(
        '{product_filter}',
        f"AND op.product_id IN ({','.join(map(str, target_product_ids))})" if target_product_ids else ""
    ))
    
    sales_result = await db.execute(sales_contribution_query)
    sales_row = sales_result.first()
    
    sales_contribution = (sales_row.repurchase_sales / sales_row.total_sales * 100) if sales_row and sales_row.total_sales > 0 else 0.0
    
    return {
        "total_repurchase_count": row.total_repurchase_count,
        "avg_repurchase_rate": round(avg_repurchase_rate, 1),
        "avg_repurchase_days": int(row.avg_repurchase_days or 0),
        "same_product_rate": round(same_product_rate, 1),
        "sales_contribution": round(sales_contribution, 1)
    }


async def get_repurchase_customer_list(
    db: AsyncSession,
    page: int,
    limit: int,
    grade: Optional[str],
    sort_by: str,
    product_ids: Optional[List[int]]
):
    """
    재구매 고객 리스트
    - 비회원 포함: member_id가 __guest__:로 시작하면 member_id 공백, 이름은 billing_name
    - 그룹화 적용
    - 등급 필터, 정렬 적용
    - 재구매 쌍 로직 적용: 실제로 재구매한 고객만 조회
    """
    
    # 1. product_ids가 주어진 경우, 그룹 내 모든 상품 ID 포함
    target_product_ids = []
    if product_ids:
        for pid in product_ids:
            group_ids = PRODUCT_GROUPS.get(pid, [pid])
            target_product_ids.extend(group_ids)
    
    # 2. 재구매 고객 customer_key 목록 추출 (재구매 쌍 로직)
    repurchase_customers_query = text(f"""
        WITH customer_purchases AS (
            SELECT 
                CAST(CASE 
                    WHEN o.member_id LIKE '__guest__%' 
                    THEN CONCAT(o.billing_name, '|', o.order_address_1)
                    ELSE CAST(o.user_id AS CHAR)
                END AS CHAR CHARSET utf8mb4) COLLATE utf8mb4_unicode_ci AS customer_key,
                o.order_id,
                o.order_date,
                o.user_id,
                o.member_id
            FROM orders o
            {"JOIN order_products op ON o.order_id = op.order_id" if target_product_ids else ""}
            WHERE 1=1
                {f"AND op.product_id IN ({','.join(map(str, target_product_ids))})" if target_product_ids else ""}
            {"GROUP BY o.order_id, o.user_id, o.member_id, o.billing_name, o.order_address_1, o.order_date" if target_product_ids else ""}
        ),
        repurchase_pairs AS (
            SELECT DISTINCT cp1.customer_key, cp1.user_id, cp1.member_id
            FROM customer_purchases cp1
            JOIN customer_purchases cp2 
                ON cp1.customer_key = cp2.customer_key
                AND cp1.order_date < cp2.order_date
        )
        SELECT customer_key, user_id, member_id
        FROM repurchase_pairs
    """)
    
    repurchase_result = await db.execute(repurchase_customers_query)
    repurchase_customers = repurchase_result.all()
    
    if not repurchase_customers:
        return [], 0
    
    # 3. 재구매 고객을 회원/비회원으로 분류
    repurchase_user_ids = []
    repurchase_guest_keys = []
    
    for row in repurchase_customers:
        if row.member_id and '__guest__' in row.member_id:
            repurchase_guest_keys.append(row.customer_key)
        elif row.user_id:
            repurchase_user_ids.append(row.user_id)
    
    # 4. 회원 재구매 고객 정보 조회
    member_query = None
    if repurchase_user_ids:
        base_member_query = (
            select(
                Member.user_id,
                Member.member_id,
                func.max(Order.billing_name).label("name"),
                MemberGroup.group_name.label("grade"),
                Member.available_points.label("point"),
                func.max(Order.order_phone_number).label("phone"),
                func.max(Order.order_email).label("email"),
                func.concat(func.max(Order.order_address_1), " ", func.max(Order.order_address_2)).label("address"),
                func.count(distinct(Order.order_id)).label("purchase_count"),
                func.max(Order.order_date).label("last_purchase_date"),
                func.min(Order.order_date).label("first_purchase_date")
            )
            .select_from(Member)
            .join(MemberGroup, Member.group_id == MemberGroup.group_id)
            .join(Order, Member.user_id == Order.user_id)
            .where(Member.user_id.in_(repurchase_user_ids))
        )
        
        if grade and grade != "전체":
            base_member_query = base_member_query.where(MemberGroup.group_name == grade)
        
        member_query = base_member_query.group_by(
            Member.user_id, Member.member_id, MemberGroup.group_name, Member.available_points
        )
    
    # 5. 비회원 재구매 고객 정보 조회
    guest_query = None
    if repurchase_guest_keys and (not grade or grade == "전체"):  # 비회원은 특정 등급 필터 시 제외
        # customer_key를 파싱하여 billing_name과 order_address_1 추출
        guest_conditions = []
        for guest_key in repurchase_guest_keys:
            if '|' in guest_key:
                parts = guest_key.split('|', 1)
                if len(parts) == 2:
                    billing_name, address_1 = parts
                    guest_conditions.append(
                        and_(
                            Order.billing_name == billing_name,
                            Order.order_address_1 == address_1
                        )
                    )
        
        if guest_conditions:
            base_guest_query = (
                select(
                    func.cast(None, BigInteger).label("user_id"),
                    func.concat(Order.billing_name, '|', func.trim(Order.order_address_1)).label("member_id"),
                    Order.billing_name.label("name"),
                    func.cast("전체", String).label("grade"),
                    func.cast(0, Integer).label("point"),
                    func.max(Order.order_phone_number).label("phone"),
                    func.max(Order.order_email).label("email"),
                    func.concat(func.max(Order.order_address_1), " ", func.max(Order.order_address_2)).label("address"),
                    func.count(distinct(Order.order_id)).label("purchase_count"),
                    func.max(Order.order_date).label("last_purchase_date"),
                    func.min(Order.order_date).label("first_purchase_date")
                )
                .select_from(Order)
                .where(
                    Order.member_id.like('__guest__%'),
                    or_(*guest_conditions)
                )
                .group_by(Order.billing_name, Order.order_address_1)
            )
            
            guest_query = base_guest_query
    
    # 6. 쿼리 실행
    member_result = (await db.execute(member_query)).all() if member_query is not None else []
    guest_result = (await db.execute(guest_query)).all() if guest_query is not None else []
    
    # 7. 결과 합치기 및 정렬 (Python에서 한 번만 정렬)
    all_rows = list(member_result) + list(guest_result)
    
    from datetime import date as date_type
    
    if sort_by == "purchase_count":
        all_rows.sort(key=lambda r: r.purchase_count or 0, reverse=True)
    elif sort_by == "points":
        all_rows.sort(key=lambda r: r.point or 0, reverse=True)
    elif sort_by == "name":
        all_rows.sort(key=lambda r: (r.name or "").lower())  # 대소문자 무시
    else:  # latest_repurchase (기본)
        all_rows.sort(key=lambda r: r.last_purchase_date or date_type.min, reverse=True)
    
    # 페이징
    total_count = len(all_rows)
    
    # limit=0이면 전체 데이터 반환
    if limit == 0:
        paged_rows = all_rows
    else:
        paged_rows = all_rows[(page - 1) * limit: page * limit]
    
    return paged_rows, total_count


async def get_customer_repurchase_detail(db: AsyncSession, customer_id: str):
    """
    특정 고객의 재구매 상세 정보 (상품 + 배송지)
    - customer_id: 회원은 member_id, 비회원은 "billing_name|order_address_1"
    """
    # customer_id에 "|"가 포함되어 있으면 비회원
    is_guest = "|" in customer_id
    
    if is_guest:
        # 비회원: billing_name|order_address_1 파싱
        parts = customer_id.split("|", 1)
        if len(parts) != 2:
            return None
        billing_name, address_1 = parts
        
        # 고객 기본 정보
        customer_info_query = (
            select(
                Order.billing_name.label("name"),
                func.cast("전체", String).label("grade"),
                func.cast(0, Integer).label("point"),
                func.count(distinct(Order.order_id)).label("total_order_count"),
                func.min(Order.order_date).label("first_order_date"),
                func.max(Order.order_date).label("last_order_date")
            )
            .where(
                and_(
                    Order.member_id.like('__guest__%'),
                    Order.billing_name == billing_name,
                    Order.order_address_1 == address_1
                )
            )
            .group_by(Order.billing_name)
        )
        
        # 재구매 상품 목록
        products_query = (
            select(
                Product.product_id,
                Product.product_name,
                func.count(distinct(Order.order_id)).label("repurchase_count"),
                func.min(Order.order_date).label("first_purchase_date"),
                func.max(Order.order_date).label("last_purchase_date")
            )
            .select_from(Order)
            .join(OrderProduct, Order.order_id == OrderProduct.order_id)
            .join(Product, OrderProduct.product_id == Product.product_id)
            .where(
                and_(
                    Order.member_id.like('__guest__%'),
                    Order.billing_name == billing_name,
                    Order.order_address_1 == address_1
                )
            )
            .group_by(Product.product_id, Product.product_name)
            .order_by(desc("repurchase_count"))
            .limit(10)
        )
        
        # 재구매 배송지 목록
        addresses_query = (
            select(
                Order.order_address_1.label("address"),
                func.count(distinct(Order.order_id)).label("order_count"),
                func.min(Order.order_date).label("first_order_date"),
                func.max(Order.order_date).label("last_order_date")
            )
            .where(
                and_(
                    Order.member_id.like('__guest__%'),
                    Order.billing_name == billing_name,
                    Order.order_address_1 == address_1
                )
            )
            .group_by(Order.order_address_1)
            .order_by(desc("order_count"))
            .limit(5)
        )
    else:
        # 회원: member_id
        # 고객 기본 정보
        customer_info_query = (
            select(
                Member.member_id,
                func.max(Order.billing_name).label("name"),
                MemberGroup.group_name.label("grade"),
                Member.available_points.label("point"),
                func.count(distinct(Order.order_id)).label("total_order_count"),
                func.min(Order.order_date).label("first_order_date"),
                func.max(Order.order_date).label("last_order_date")
            )
            .select_from(Member)
            .join(MemberGroup, Member.group_id == MemberGroup.group_id)
            .join(Order, Member.user_id == Order.user_id)
            .where(Member.member_id == customer_id)
            .group_by(Member.member_id, MemberGroup.group_name, Member.available_points)
        )
        
        # 재구매 상품 목록
        products_query = (
            select(
                Product.product_id,
                Product.product_name,
                func.count(distinct(Order.order_id)).label("repurchase_count"),
                func.min(Order.order_date).label("first_purchase_date"),
                func.max(Order.order_date).label("last_purchase_date")
            )
            .select_from(Member)
            .join(Order, Member.user_id == Order.user_id)
            .join(OrderProduct, Order.order_id == OrderProduct.order_id)
            .join(Product, OrderProduct.product_id == Product.product_id)
            .where(Member.member_id == customer_id)
            .group_by(Product.product_id, Product.product_name)
            .order_by(desc("repurchase_count"))
            .limit(10)
        )
        
        # 재구매 배송지 목록
        addresses_query = (
            select(
                Order.order_address_1.label("address"),
                func.count(distinct(Order.order_id)).label("order_count"),
                func.min(Order.order_date).label("first_order_date"),
                func.max(Order.order_date).label("last_order_date")
            )
            .select_from(Member)
            .join(Order, Member.user_id == Order.user_id)
            .where(Member.member_id == customer_id)
            .group_by(Order.order_address_1)
            .order_by(desc("order_count"))
            .limit(5)
        )
    
    # 쿼리 실행
    customer_info = (await db.execute(customer_info_query)).first()
    if not customer_info:
        return None
    
    products = (await db.execute(products_query)).all()
    addresses = (await db.execute(addresses_query)).all()
    
    # 상품 목록에 커스텀 상품명 적용
    products_with_custom_names = [
        {
            "product_id": p.product_id,
            "product_name": PRODUCT_GROUP_NAMES.get(p.product_id, p.product_name),
            "repurchase_count": p.repurchase_count,
            "first_purchase_date": p.first_purchase_date,
            "last_purchase_date": p.last_purchase_date
        }
        for p in products
    ]
    
    return customer_info, products_with_custom_names, addresses