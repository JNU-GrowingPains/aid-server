# repositories/dashboard/repurchase_repository.py

from typing import Optional, List
from sqlalchemy import select, func, desc, distinct, case, and_, or_, text, BigInteger, String, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Member, MemberGroup, Order, OrderProduct, Product
from config.product_groups import PRODUCT_GROUPS


async def get_repurchase_product_list(db: AsyncSession):
    """
    그룹화된 대표 상품 목록 반환
    PRODUCT_GROUPS의 키(대표 product_id)만 반환
    제외 상품(18, 19 등) 필터링 적용
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
        .where(Product.product_id.notin_(EXCLUDED_PRODUCTS))  # 명시적 제외
    )
    
    result = await db.execute(q)
    return result.all()


async def get_repurchase_kpis(db: AsyncSession, target_product_ids: List[int], product_to_group: dict):
    """
    재구매 KPI 계산 (Repository - DB 조회만 담당)
    
    Args:
        target_product_ids: 필터링할 상품 ID 리스트 (그룹 확장 완료)
        product_to_group: product_id → group_id 매핑 딕셔너리
    """
    # 쿼리 1: 고객별 구매 내역 조회
    purchases = await _get_customer_purchases(db, target_product_ids)
    
    if not purchases:
        return {
            "total_repurchase_count": 0,
            "avg_repurchase_rate": 0.0,
            "avg_repurchase_days": 0,
            "same_product_rate": 0.0,
            "sales_contribution": 0.0
        }
    
    # 쿼리 2: 전체 고객 수 조회
    total_customers = await _get_total_customers(db, target_product_ids)
    
    # Python에서 재구매 통계 계산
    stats = _calculate_repurchase_stats(purchases, product_to_group)
    
    # 쿼리 3: 매출 기여도 조회
    sales_contribution = await _get_sales_contribution(db, target_product_ids)
    
    # 최종 결과
    repurchase_rate = (stats['repurchase_count'] / total_customers * 100) if total_customers > 0 else 0.0
    same_product_rate = (stats['same_product_count'] / stats['total_pairs'] * 100) if stats['total_pairs'] > 0 else 0.0
    
    return {
        "total_repurchase_count": stats['repurchase_count'],
        "avg_repurchase_rate": round(repurchase_rate, 1),
        "avg_repurchase_days": stats['avg_days'],
        "same_product_rate": round(same_product_rate, 1),
        "sales_contribution": round(sales_contribution, 1)
    }


async def _get_customer_purchases(db: AsyncSession, product_ids: List[int]):
    """쿼리 1: 고객별 구매 내역 (SQLAlchemy ORM)"""
    from sqlalchemy import case, cast, String
    
    # customer_key 생성 (회원/비회원 구분)
    customer_key = case(
        (Order.member_id.like('__guest__%'), 
         func.concat(Order.billing_name, '|', Order.order_address_1)),
        else_=cast(Order.user_id, String)
    ).label('customer_key')
    
    # 기본 쿼리
    query = (
        select(
            customer_key,
            Order.order_date,
            OrderProduct.product_id
        )
        .select_from(Order)
        .join(OrderProduct, Order.order_id == OrderProduct.order_id)
    )
    
    # 상품 필터 적용
    if product_ids:
        query = query.where(OrderProduct.product_id.in_(product_ids))
    
    # 정렬
    query = query.order_by(customer_key, Order.order_date)
    
    result = await db.execute(query)
    return result.all()


async def _get_total_customers(db: AsyncSession, product_ids: List[int]) -> int:
    """쿼리 2: 전체 고객 수 (SQLAlchemy ORM)"""
    from sqlalchemy import case, cast, String
    
    # customer_key 생성 (회원/비회원 구분)
    customer_key = case(
        (Order.member_id.like('__guest__%'), 
         func.concat(Order.billing_name, '|', Order.order_address_1)),
        else_=cast(Order.user_id, String)
    )
    
    # 기본 쿼리
    query = (
        select(func.count(distinct(customer_key)))
        .select_from(Order)
        .join(OrderProduct, Order.order_id == OrderProduct.order_id)
    )
    
    # 상품 필터 적용
    if product_ids:
        query = query.where(OrderProduct.product_id.in_(product_ids))
    
    result = await db.execute(query)
    return result.scalar() or 0


def _calculate_repurchase_stats(purchases, product_to_group: dict) -> dict:
    """Python에서 재구매 통계 계산"""
    from collections import defaultdict
    from datetime import date
    
    # 고객별 주문 그룹화
    customer_orders = defaultdict(list)
    for row in purchases:
        customer_orders[row.customer_key].append({
            'date': row.order_date,
            'product_id': row.product_id,
            'group_id': product_to_group.get(row.product_id, row.product_id)
        })
    
    # 재구매 통계
    repurchase_count = 0
    total_days = 0
    same_product_count = 0
    total_pairs = 0
    
    for customer_key, orders in customer_orders.items():
        if len(orders) < 2:
            continue
        
        repurchase_count += 1
        orders_sorted = sorted(orders, key=lambda x: x['date'])
        
        # 재구매 쌍 생성
        for i in range(len(orders_sorted)):
            for j in range(i + 1, len(orders_sorted)):
                first = orders_sorted[i]
                second = orders_sorted[j]
                
                days_between = (second['date'] - first['date']).days
                total_days += days_between
                total_pairs += 1
                
                # 동일 그룹이면 동일 상품 재구매
                if first['group_id'] == second['group_id']:
                    same_product_count += 1
    
    return {
        'repurchase_count': repurchase_count,
        'avg_days': int(total_days / total_pairs) if total_pairs > 0 else 0,
        'same_product_count': same_product_count,
        'total_pairs': total_pairs
    }


async def _get_sales_contribution(db: AsyncSession, product_ids: List[int]) -> float:
    """쿼리 3: 매출 기여도 (간단한 방식으로 분리)"""
    from sqlalchemy import case, cast, String
    
    # 1. 고객별 구매 정보 조회
    purchases = await _get_customer_purchases(db, product_ids)
    
    if not purchases:
        return 0.0
    
    # 2. 재구매 고객 목록 추출 (Python)
    from collections import defaultdict
    customer_orders = defaultdict(list)
    
    for row in purchases:
        customer_orders[row.customer_key].append(row.order_date)
    
    # 재구매 고객 (2회 이상 구매)
    repurchase_customers = {
        customer_key 
        for customer_key, dates in customer_orders.items() 
        if len(dates) >= 2
    }
    
    if not repurchase_customers:
        return 0.0
    
    # 3. 전체 매출 조회 (ORM)
    total_sales_query = select(func.sum(Order.payment_amount))
    total_sales_result = await db.execute(total_sales_query)
    total_sales = total_sales_result.scalar() or 0
    
    if total_sales == 0:
        return 0.0
    
    # 4. 재구매 고객 매출 조회 (ORM)
    customer_key = case(
        (Order.member_id.like('__guest__%'), 
         func.concat(Order.billing_name, '|', Order.order_address_1)),
        else_=cast(Order.user_id, String)
    )
    
    # 재구매 고객의 주문만 필터링
    repurchase_sales_query = (
        select(func.sum(Order.payment_amount))
        .where(
            or_(*[
                and_(
                    Order.member_id.like('__guest__%'),
                    func.concat(Order.billing_name, '|', Order.order_address_1) == customer
                ) if '|' in customer else
                cast(Order.user_id, String) == customer
                for customer in repurchase_customers
            ])
        )
    )
    
    repurchase_sales_result = await db.execute(repurchase_sales_query)
    repurchase_sales = repurchase_sales_result.scalar() or 0
    
    return (repurchase_sales / total_sales * 100)


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
    """
    
    # 1. product_ids가 주어진 경우, 그룹 내 모든 상품 ID 포함
    target_product_ids = []
    if product_ids:
        for pid in product_ids:
            group_ids = PRODUCT_GROUPS.get(pid, [pid])
            target_product_ids.extend(group_ids)
    
    # 2. 재구매 고객 추출 (회원 + 비회원)
    # 회원 재구매 고객
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
        .where(Order.member_id.notlike('__guest__%'))
    )
    
    # product_ids 필터 적용
    if target_product_ids:
        # EXISTS 서브쿼리로 해당 상품 구매 고객만 필터링
        product_exists = (
            select(1)
            .select_from(OrderProduct)
            .where(
                and_(
                    OrderProduct.order_id == Order.order_id,
                    OrderProduct.product_id.in_(target_product_ids)
                )
            )
            .exists()
        )
        base_member_query = base_member_query.where(product_exists)
    
    if grade:
        base_member_query = base_member_query.where(MemberGroup.group_name == grade)
    
    member_query = base_member_query.group_by(
        Member.user_id, Member.member_id, MemberGroup.group_name, Member.available_points
    ).having(func.count(distinct(Order.order_id)) >= 2)
    
    # 비회원 재구매 고객
    base_guest_query = (
        select(
            func.cast(None, BigInteger).label("user_id"),
            func.concat(Order.billing_name, '|', func.trim(Order.order_address_1)).label("member_id"),  # "이름|주소" 형식
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
        .where(Order.member_id.like('__guest__%'))
    )
    
    # product_ids 필터 적용
    if target_product_ids:
        # EXISTS 서브쿼리로 해당 상품 구매 고객만 필터링
        product_exists = (
            select(1)
            .select_from(OrderProduct)
            .where(
                and_(
                    OrderProduct.order_id == Order.order_id,
                    OrderProduct.product_id.in_(target_product_ids)
                )
            )
            .exists()
        )
        base_guest_query = base_guest_query.where(product_exists)
    
    guest_query = base_guest_query.group_by(
        Order.billing_name, Order.order_address_1
    ).having(func.count(distinct(Order.order_id)) >= 2)
    
    # 정렬 적용
    if sort_by == "purchase_count":
        member_query = member_query.order_by(desc("purchase_count"))
        guest_query = guest_query.order_by(desc("purchase_count"))
    elif sort_by == "points":
        member_query = member_query.order_by(desc("point"))
        guest_query = guest_query.order_by(desc("point"))
    elif sort_by == "name":
        member_query = member_query.order_by("name")
        guest_query = guest_query.order_by("name")
    else:  # latest_repurchase (기본)
        member_query = member_query.order_by(desc("last_purchase_date"))
        guest_query = guest_query.order_by(desc("last_purchase_date"))
    
    # 쿼리 실행
    member_result = (await db.execute(member_query)).all()
    guest_result = (await db.execute(guest_query)).all() if not grade else []
    
    # 결과 합치기
    all_rows = list(member_result) + list(guest_result)
    
    # 정렬 (Python에서 다시 정렬)
    if sort_by == "purchase_count":
        all_rows.sort(key=lambda r: r.purchase_count, reverse=True)
    elif sort_by == "points":
        all_rows.sort(key=lambda r: r.point or 0, reverse=True)
    elif sort_by == "name":
        all_rows.sort(key=lambda r: r.name or "")
    else:
        all_rows.sort(key=lambda r: r.last_purchase_date or "", reverse=True)
    
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
    
    return customer_info, products, addresses