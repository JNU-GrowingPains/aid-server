# services/dashboard/repurchase_service.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.dashboard import repurchase_repository as repo


async def get_repurchase_product_list(db: AsyncSession):
    """
    그룹화된 대표 상품 목록 반환
    """
    rows = await repo.get_repurchase_product_list(db)
    return [
        {
            "product_id": r.product_id,
            "product_name": r.product_name,
            "price": r.product_price
        } 
        for r in rows
    ]


async def get_repurchase_kpis(db: AsyncSession, product_ids: Optional[List[int]] = None):
    """
    재구매 KPI 조회
    - 비회원 포함
    - 그룹화 적용
    - 교차 재구매 포함
    
    반환:
    - total_repurchase_count: 총 재구매 수 (첫 구매 제외한 주문 수)
    - avg_repurchase_rate: 평균 재구매율 (%)
    - avg_repurchase_days: 재구매까지 걸린 평균 기간 (일)
    - same_product_rate: 동일 상품 재구매 비율 (%)
    - sales_contribution: 재구매 고객 매출 기여도 (%)
    """
    return await repo.get_repurchase_kpis(db, product_ids)


async def get_repurchase_customer_list(
    db: AsyncSession,
    page: int,
    limit: int,
    grade: Optional[str],
    sort_by: str,
    product_ids: Optional[List[int]] = None
):
    """
    재구매 고객 리스트
    - 비회원 포함 (customer_id는 "이름|주소" 형식, 이름은 billing_name)
    - 그룹화 적용
    - 등급 필터, 정렬 적용
    """
    rows, total_count = await repo.get_repurchase_customer_list(
        db, page, limit, grade, sort_by, product_ids
    )
    
    items = []
    for r in rows:
        # 평균 재구매 주기 계산
        period = 0
        if r.purchase_count > 1 and r.last_purchase_date and r.first_purchase_date:
            period = (r.last_purchase_date - r.first_purchase_date).days // (r.purchase_count - 1)
        
        # 비회원 판별: member_id에 "|"가 포함되어 있으면 비회원
        is_guest = r.member_id and "|" in r.member_id
        display_customer_id = "비회원" if is_guest else (r.member_id or "")
        
        items.append({
            "user_id": r.user_id,
            "customer_id": display_customer_id,  # 회원: member_id, 비회원: "비회원"
            "name": r.name or "-",
            "grade": r.grade,
            "purchase_count": f"{r.purchase_count}회",
            "address": r.address or "-",
            "phone": r.phone or "-",
            "email": r.email or "-",
            "point": f"{r.point or 0:,}P",
            "avg_period": f"{period}일"
        })
    
    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "items": items
    }


async def get_customer_repurchase_detail(db: AsyncSession, customer_id: str):
    """
    특정 고객의 재구매 상세 정보 (상품 + 배송지)
    """
    result = await repo.get_customer_repurchase_detail(db, customer_id)
    
    if not result:
        return None
    
    customer_info, products, addresses = result
    
    # 고객 기본 정보
    total_order_count = customer_info.total_order_count
    
    # 재구매 상품 목록
    product_items = []
    for p in products:
        percentage = (p.repurchase_count / total_order_count * 100) if total_order_count > 0 else 0
        product_items.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "repurchase_count": p.repurchase_count,
            "percentage": round(percentage, 1),
            "first_purchase_date": p.first_purchase_date.strftime("%Y-%m-%d") if p.first_purchase_date else None,
            "last_purchase_date": p.last_purchase_date.strftime("%Y-%m-%d") if p.last_purchase_date else None
        })
    
    # 재구매 배송지 목록
    address_items = []
    for a in addresses:
        percentage = (a.order_count / total_order_count * 100) if total_order_count > 0 else 0
        address_items.append({
            "address": a.address or "-",
            "order_count": a.order_count,
            "percentage": round(percentage, 1),
            "first_order_date": a.first_order_date.strftime("%Y-%m-%d") if a.first_order_date else None,
            "last_order_date": a.last_order_date.strftime("%Y-%m-%d") if a.last_order_date else None
        })
    
    # 평균 재구매 기간 계산
    avg_period = 0
    if total_order_count > 1 and customer_info.first_order_date and customer_info.last_order_date:
        avg_period = (customer_info.last_order_date - customer_info.first_order_date).days // (total_order_count - 1)
    
    return {
        "customer": {
            "customer_id": customer_id,
            "name": customer_info.name or "-",
            "grade": customer_info.grade,
            "point": customer_info.point or 0,
            "total_order_count": total_order_count,
            "avg_repurchase_days": avg_period,
            "first_order_date": customer_info.first_order_date.strftime("%Y-%m-%d") if customer_info.first_order_date else None,
            "last_order_date": customer_info.last_order_date.strftime("%Y-%m-%d") if customer_info.last_order_date else None
        },
        "products": product_items,
        "addresses": address_items
    }