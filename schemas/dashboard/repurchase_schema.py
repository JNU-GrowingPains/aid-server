# schemas/dashboard/repurchase_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class RepurchaseProductItem(BaseModel):
    """재구매 상품 항목"""
    product_id: int
    product_name: str
    price: int
    
    class Config:
        from_attributes = True


class RepurchaseProductListResponse(BaseModel):
    """재구매 상품 목록 응답"""
    items: List[RepurchaseProductItem]
    count: int
    
    class Config:
        from_attributes = True


class RepurchaseKpisResponse(BaseModel):
    """재구매 KPI 통계 응답"""
    total_repurchase_count: int  # 총 재구매 고객 수
    avg_repurchase_rate: float   # 평균 재구매율 (%)
    avg_repurchase_days: int     # 재구매까지 걸린 평균 기간 (일)
    same_product_rate: float     # 동일 상품 재구매 비율 (%)
    sales_contribution: float    # 재구매 고객 매출 기여도 (%)
    
    class Config:
        from_attributes = True


class RepurchaseCustomerItem(BaseModel):
    """재구매 고객 항목"""
    user_id: Optional[int]
    customer_id: str
    name: str
    grade: str
    purchase_count: str  # "N회" 형식
    address: str
    phone: str
    email: str
    point: str  # "N,NNNP" 형식
    avg_period: str  # "N일" 형식
    
    class Config:
        from_attributes = True


class RepurchaseCustomerListResponse(BaseModel):
    """재구매 고객 리스트 응답"""
    total_count: int
    page: int
    limit: int
    items: List[RepurchaseCustomerItem]
    
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





