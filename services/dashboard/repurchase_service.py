# services/dashboard/repurchase_service.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.dashboard import repurchase_repository as repo
from schemas.dashboard.repurchase_schema import (
    RepurchaseProductItem,
    RepurchaseProductListResponse
)
from config.product_groups import PRODUCT_GROUPS


async def get_repurchase_product_list(db: AsyncSession) -> RepurchaseProductListResponse:
    """
    그룹화된 대표 상품 목록 반환
    """
    rows = await repo.get_repurchase_product_list(db)
    
    items = [
        RepurchaseProductItem(
            produdt_id=r.product_id,
            product_name=r.product_name,
            price=r.product_price
        )
        for r in rows
    ]
    
    return RepurchaseProductListResponse(items=items, count=len(items))




async def get_repurchase_kpis_v2(db: AsyncSession, product_ids: Optional[List[int]] = None):
    # 결제 테이블에서 회원 수  =   repo.get_login_user_count()
    console.log("user count:", userCount);
    # 결제 테이블에서 비회원 수  =   repo.get_not_login_user_count()


    # 전체 회원 수 = 가입 회원 수 + 비가입 회원 수
    # repo.count   order by
    # list  .
    #   select    ->   where 조건, order by ,  join ,   group by + having  ,
    return  ResponseDto(재구매율 = )



    # 회원
        # 유저 아이디가 있으면  재구매
    # 비회원 (결제 이름 + 주소 => 같은 사람으로 그룹)
        # 재구매한 고객 수 ( 주문 수가 2 이상인 고객 수 )
        #  재구매 고객 수 /  전체 구매 고개 수

    # 최근 재구매일 - 첫 구매일
    #
        # 평균 재구매율
    # 동일 상품 재구매
        #

    # 재구매 고객수  /  전체 고객 수   * 100 =>

    # repo select
    # return result

async def get_repurchase_kpis(db: AsyncSession, product_ids: Optional[List[int]] = None):
    """
    재구매 KPI 조회
    - 비회원 포함
    - 그룹화 적용
    - 교차 재구매 포함
    
    반환:
    - total_repurchase_count: 총 재구매 고객 수
    - avg_repurchase_rate: 평균 재구매율 (%)
    - avg_repurchase_days: 재구매까지 걸린 평균 기간 (일)
    - same_product_rate: 동일 상품 재구매 비율 (%)
    - sales_contribution: 재구매 고객 매출 기여도 (%)
    """
    # 1. 상품 그룹 필터 준비 (비즈니스 로직)
    target_product_ids = []
    if product_ids:
        for pid in product_ids:
            group_ids = PRODUCT_GROUPS.get(pid, [pid])
            target_product_ids.extend(group_ids)
    
    # 2. product_id → group_id 매핑 (비즈니스 로직)
    product_to_group = {}
    for group_id, member_ids in PRODUCT_GROUPS.items():
        for member_id in member_ids:
            product_to_group[member_id] = group_id

    # 3. Repository 호출 (준비된 데이터 전달)
    return await repo.get_repurchase_kpis(db, target_product_ids, product_to_group)


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
        
        items.append({
            "user_id": r.user_id,
            "customer_id": r.member_id or "",  # 회원: member_id, 비회원: "이름|주소" 형식
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