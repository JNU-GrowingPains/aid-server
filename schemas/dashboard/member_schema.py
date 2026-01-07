# schemas/dashboard/member_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class MemberGradeItem(BaseModel):
    """등급별 고객 수 항목"""
    grade_name: str
    member_count: int
    percentage: float
    
    class Config:
        from_attributes = True


class MemberGradeStatsResponse(BaseModel):
    """등급별 고객 수 통계 응답 (막대그래프용)"""
    total_members: int
    grade_distribution: List[MemberGradeItem]
    
    class Config:
        from_attributes = True


class MemberItem(BaseModel):
    """개별 고객 정보"""
    user_id: int
    member_id: str
    name: str
    grade: str
    purchase_count: int
    first_purchase: Optional[date]
    last_purchase: Optional[date]
    available_points: int
    
    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """고객 리스트 응답"""
    members: List[MemberItem]
    total_count: int
    page: int
    limit: int
    total_pages: int
    
    class Config:
        from_attributes = True


class TopMemberItem(BaseModel):
    """포인트 상위 고객 항목"""
    user_id: int
    member_id: str
    name: str
    grade: str
    purchase_count: int
    available_points: int
    rank: int
    
    class Config:
        from_attributes = True


class TopMemberResponse(BaseModel):
    """포인트 상위 고객 응답 (오른쪽 패널용)"""
    top_members: List[TopMemberItem]
    total_count: int
    
    class Config:
        from_attributes = True


class MemberFilterRequest(BaseModel):
    """고객 필터링 요청"""
    grade: Optional[str] = None
    
    class Config:
        from_attributes = True


class MemberSortRequest(BaseModel):
    """고객 정렬 요청"""
    sort_by: str = "latest_purchase"  # latest_purchase, purchase_count, points, name
    order: str = "desc"  # desc, asc
    
    class Config:
        from_attributes = True






