# schemas/dashboard/repurchase_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class RepurchaseProductItem(BaseModel):
    """재구매 상품 항목"""
    product_id: int
    product_name: str
    category: str
    price: str
    repurchase_rate: float
    
    class Config:
        from_attributes = True


class RepurchaseProductResponse(BaseModel):
    """재구매 상품 목록 응답"""
    products: List[RepurchaseProductItem]
    total_count: int
    
    class Config:
        from_attributes = True


class RepurchaseStatsResponse(BaseModel):
    """재구매 통계 응답"""
    total_repurchase_count: int  # 총 재구매 수
    avg_repurchase_rate: float   # 평균 재구매율 (%)
    avg_repurchase_days: int     # 재구매까지 걸린 기간 (일)
    same_product_rate: float     # 동일 상품 재구매 비율 (%)
    sales_contribution: float    # 재구매 고객 매출 기여도 (%)
    
    class Config:
        from_attributes = True


class RepurchaseCustomerItem(BaseModel):
    """재구매 고객 항목"""
    customer_id: str
    name: str
    grade: str
    purchase_count: int
    address: str
    phone: str
    email: str
    points: int
    avg_repurchase_period: int  # 평균 재구매 주기 (일)
    last_purchase_date: Optional[date]
    
    class Config:
        from_attributes = True


class RepurchaseCustomerResponse(BaseModel):
    """재구매 고객 리스트 응답"""
    customers: List[RepurchaseCustomerItem]
    total_count: int
    page: int
    limit: int
    total_pages: int
    
    class Config:
        from_attributes = True


class RepurchaseFilterRequest(BaseModel):
    """재구매 분석 필터 요청"""
    product_ids: Optional[List[int]] = None
    grade: Optional[str] = None
    sort_by: str = "latest_repurchase"
    page: int = 1
    limit: int = 10
    
    class Config:
        from_attributes = True






