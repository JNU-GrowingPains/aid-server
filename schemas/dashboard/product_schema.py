# schemas/dashboard/product_schema.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class PeriodType(str, Enum):
    """기간 타입"""
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"
    CUSTOM = "custom"


class ProductItem(BaseModel):
    """상품 항목"""
    product_id: int
    product_name: str
    category: str
    price: str
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """상품 목록 응답"""
    products: List[ProductItem]
    total_count: int
    
    class Config:
        from_attributes = True


class ProductStatsResponse(BaseModel):
    """상품별 통계 응답"""
    product_id: int
    product_name: str
    period_start: date
    period_end: date
    total_revenue: float      # 총 매출액
    total_sales_count: int    # 총 판매수
    total_customers: int      # 총 구매자수
    
    class Config:
        from_attributes = True


class DailySalesItem(BaseModel):
    """일별 판매 데이터 항목"""
    date: date
    sales_count: int
    revenue: float
    
    class Config:
        from_attributes = True


class DailySalesResponse(BaseModel):
    """일별 판매 차트 응답"""
    product_id: int
    product_name: str
    period_start: date
    period_end: date
    daily_data: List[DailySalesItem]
    
    class Config:
        from_attributes = True


class ReviewStatsResponse(BaseModel):
    """리뷰 통계 응답"""
    product_id: int
    product_name: str
    total_reviews: int        # 총 리뷰 수
    average_rating: float     # 평균 평점
    
    class Config:
        from_attributes = True


class ReviewKeywordItem(BaseModel):
    """리뷰 키워드 항목"""
    keyword: str
    frequency: int
    weight: float  # 워드클라우드용 가중치 (0.0 ~ 1.0)
    
    class Config:
        from_attributes = True


class ReviewKeywordResponse(BaseModel):
    """리뷰 키워드 워드클라우드 응답"""
    product_id: int
    product_name: str
    keywords: List[ReviewKeywordItem]  # 상위 30개
    total_keywords: int
    
    class Config:
        from_attributes = True


class ProductReviewItem(BaseModel):
    """상품 리뷰 항목"""
    review_id: int
    writer: str
    rating: int
    content: str
    created_date: str
    hit: int
    
    class Config:
        from_attributes = True


class ProductReviewResponse(BaseModel):
    """상품별 리뷰 목록 응답"""
    product_id: int
    product_name: str
    reviews: List[ProductReviewItem]
    total_count: int
    page: int
    limit: int
    total_pages: int
    
    class Config:
        from_attributes = True


class ProductAnalysisRequest(BaseModel):
    """상품 분석 요청"""
    period: PeriodType = PeriodType.THIRTY_DAYS
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    class Config:
        from_attributes = True






