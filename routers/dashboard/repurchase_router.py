from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

from services.dashboard.repurchase_service import (
    get_repurchase_product_list,
    get_repurchase_kpis,
    get_repurchase_customer_list,
    get_customer_repurchase_detail
)

router = APIRouter(prefix="/api/v1/repurchase-analysis", tags=["Repurchase Analysis"])


@router.get("/products")
async def repurchase_product_list(db: AsyncSession = Depends(get_db)):
    """
    재구매 분석 - 상품 목록 (그룹화된 대표 상품)
    
    반환:
    - product_id: 대표 상품 ID
    - product_name: 상품명
    - price: 가격
    """
    return await get_repurchase_product_list(db)


@router.get("/kpis")
async def repurchase_kpis(
    product_ids: Optional[List[int]] = Query(None, description="상품 ID 목록 (복수 선택 가능, 미선택 시 전체)"),
    db: AsyncSession = Depends(get_db)
):
    """
    재구매 KPI 조회
    
    Query Parameters:
    - product_ids: 상품 ID 목록 (선택)
      - 없음: 전체 상품
      - 1개: 해당 상품(그룹 포함) → 동일 상품 재구매만
      - 2개 이상: 교차 재구매 포함 (A→A, A→B, B→B 등)
    
    반환:
    - total_repurchase_count: 총 재구매 고객 수
    - avg_repurchase_rate: 평균 재구매율 (%)
    - avg_repurchase_days: 재구매까지 걸린 평균 기간 (일)
    - same_product_rate: 동일 상품 재구매 비율 (%)
    - sales_contribution: 재구매 고객 매출 기여도 (%)
    
    특징:
    - 비회원 포함: member_id가 __guest__:로 시작하면 billing_name + order_address_1로 식별
    - 그룹화 적용: 대표 상품 선택 시 그룹 내 모든 상품 포함
    """
    return await get_repurchase_kpis(db, product_ids)


@router.get("/customers")
async def repurchase_customer_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=0, le=100),  # limit=0 허용 (전체 조회)
    grade: Optional[str] = Query(None, description="등급 필터 (예: VIP, GOLD, 전체)"),
    sort_by: str = Query("latest_repurchase", description="정렬 기준: latest_repurchase, purchase_count, points, name"),
    product_ids: Optional[List[int]] = Query(None, description="상품 ID 목록 (복수 선택 가능)"),
    db: AsyncSession = Depends(get_db)
):
    """
    재구매 고객 리스트
    
    Query Parameters:
    - page: 페이지 번호 (기본: 1)
    - limit: 페이지당 개수 (기본: 10, 최대: 100)
    - grade: 등급 필터 (선택)
    - sort_by: 정렬 기준
      - latest_repurchase: 최근 구매일순 (기본)
      - purchase_count: 구매 횟수순
      - points: 포인트순
      - name: 이름순
    - product_ids: 상품 ID 목록 (선택)
    
    반환:
    - total_count: 전체 고객 수
    - page: 현재 페이지
    - limit: 페이지당 개수
    - items: 고객 리스트
      - customer_id: 표시용 ID (회원: member_id, 비회원: "비회원")
      - customer_key: API 호출용 실제 key (회원: member_id, 비회원: "name|address")
      - name: 이름 (비회원은 billing_name)
      - grade: 등급
      - purchase_count: 구매 횟수
      - address: 주소
      - phone: 전화번호
      - email: 이메일
      - point: 포인트
      - avg_period: 평균 재구매 주기
    
    특징:
    - 비회원 포함: member_id가 __guest__:로 시작하면 billing_name + order_address_1로 식별
    - 그룹화 적용
    """
    return await get_repurchase_customer_list(db, page, limit, grade, sort_by, product_ids)


@router.get("/customer/{customer_id}/detail")
async def get_customer_detail(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 고객의 재구매 상세 정보 (통합 API)
    
    Path Parameters:
    - customer_id: 고객 ID
      - 회원: member_id (예: "C017")
      - 비회원: "billing_name|order_address_1" (예: "김철수|서울시 강남구")
      - 비회원 customer_id는 URL 인코딩 필수
    
    반환:
    - customer: 고객 기본 정보 (이름, 등급, 포인트, 구매 횟수, 평균 재구매 기간)
    - products: 재구매 상품 목록 (상위 10개, 막대그래프용)
    - addresses: 재구매 배송지 목록 (상위 5개, 도넛차트용)
    
    예시:
    - 회원: GET /api/v1/repurchase-analysis/customer/C017/detail
    - 비회원: GET /api/v1/repurchase-analysis/customer/%EA%B9%80%EC%B2%A0%EC%88%98%7C%EC%84%9C%EC%9A%B8%EC%8B%9C/detail
    """
    from fastapi import HTTPException
    
    result = await get_customer_repurchase_detail(db, customer_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다")
    
    return result