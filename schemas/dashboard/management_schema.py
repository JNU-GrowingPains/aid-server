# schemas/dashboard/management_schema.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CustomerProfileResponse(BaseModel):
    """고객 프로필 조회 응답 스키마"""
    customer_id: int
    name: str
    email: EmailStr
    site_name: str
    created_at: Optional[datetime] = None  # 가입일 (NULL 가능)
    
    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    """대시보드 통계 응답 스키마"""
    total_products: int
    total_customers: int
    monthly_revenue: float
    
    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """프로필 수정 요청 스키마"""
    name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProfileUpdateResponse(BaseModel):
    """프로필 수정 응답 스키마"""
    success: bool
    message: str
    updated_data: Optional[CustomerProfileResponse] = None
    
    class Config:
        from_attributes = True
