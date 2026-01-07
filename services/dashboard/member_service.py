# services/dashboard/member_service.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.dashboard.member_repository import MemberRepository
from schemas.dashboard.member_schema import (
    MemberGradeStatsResponse, TopMemberResponse, MemberListResponse,
    MemberGradeItem, TopMemberItem, MemberItem
)


class MemberService:
    """고객 분석 비즈니스 로직"""
    
    @staticmethod
    async def get_member_grade_statistics(db: AsyncSession) -> MemberGradeStatsResponse:
        """등급별 고객 수 통계 조회 (막대그래프용)"""
        try:
            stats_data = await MemberRepository.get_member_grade_distribution(db)
            
            grade_items = [
                MemberGradeItem(**grade_data) 
                for grade_data in stats_data["grade_distribution"]
            ]
            
            return MemberGradeStatsResponse(
                total_members=stats_data["total_members"],
                grade_distribution=grade_items
            )
        except Exception as e:
            # 오류 시 빈 통계 반환
            return MemberGradeStatsResponse(
                total_members=0,
                grade_distribution=[]
            )
    
    @staticmethod
    async def get_top_members(db: AsyncSession, limit: int = 10) -> TopMemberResponse:
        """포인트 상위 고객 조회 (오른쪽 패널용)"""
        try:
            top_data = await MemberRepository.get_top_members_by_points(db, limit)
            
            top_member_items = [
                TopMemberItem(**member_data) 
                for member_data in top_data["top_members"]
            ]
            
            return TopMemberResponse(
                top_members=top_member_items,
                total_count=top_data["total_count"]
            )
        except Exception as e:
            # 오류 시 빈 목록 반환
            return TopMemberResponse(
                top_members=[],
                total_count=0
            )
    
    @staticmethod
    async def get_member_list(
        db: AsyncSession, 
        page: int, 
        limit: int,
        grade_filter: Optional[str] = None,
        sort_by: str = "latest_purchase",
        order: str = "desc"
    ) -> MemberListResponse:
        """
        고객 리스트 조회 (필터링/정렬 지원)
        
        Args:
            limit: 페이지당 항목 수 (0 = 전체 조회, 최대 10,000개 제한)
        """
        try:
            # 전체 데이터 조회 여부 확인
            fetch_all = (limit == 0)
            
            if not fetch_all:
                # 페이지 유효성 검사
                if page < 1:
                    page = 1
                if limit < 1 or limit > 100:
                    limit = 20
            else:
                # 전체 조회 시 page는 1로 설정
                page = 1
            
            # 정렬 옵션 유효성 검사
            valid_sorts = ["latest_purchase", "purchase_count", "points", "name"]
            if sort_by not in valid_sorts:
                sort_by = "latest_purchase"
            
            # 정렬 순서 유효성 검사
            if order not in ["asc", "desc"]:
                order = "desc"
            
            member_data = await MemberRepository.get_member_list(
                db, page, limit, grade_filter, sort_by, order
            )
            
            member_items = [
                MemberItem(**member_info) 
                for member_info in member_data["members"]
            ]
            
            return MemberListResponse(
                members=member_items,
                total_count=member_data["total_count"],
                page=member_data["page"],
                limit=member_data["limit"],
                total_pages=member_data["total_pages"]
            )
        except Exception as e:
            # 오류 시 빈 목록 반환
            return MemberListResponse(
                members=[],
                total_count=0,
                page=page,
                limit=limit if limit > 0 else 0,
                total_pages=0
            )


# 기존 함수들 (하위 호환성을 위해 유지)
async def get_customer_kpi(db: AsyncSession):
    """기존 호환성을 위한 함수"""
    stats = await MemberService.get_member_grade_statistics(db)
    vip_count = 0
    
    for grade in stats.grade_distribution:
        if grade.grade_name == "VIP":
            vip_count = grade.member_count
            break
    
    return {
        "total_customers": stats.total_members, 
        "new_customers": 0, 
        "vip_customers": vip_count
    }

async def get_customer_grade_counts(db: AsyncSession):
    """기존 호환성을 위한 함수"""
    stats = await MemberService.get_member_grade_statistics(db)
    result = {"ALL": stats.total_members}
    
    for grade in stats.grade_distribution:
        result[grade.grade_name] = grade.member_count
    
    return result

async def get_customer_list(db: AsyncSession, page: int, limit: int, grade: Optional[str], sort_by: str):
    """기존 호환성을 위한 함수"""
    member_list = await MemberService.get_member_list(db, page, limit, grade, sort_by, "desc")
    
    items = []
    for member in member_list.members:
        items.append({
            "user_id": member.user_id,
            "customer_id": member.member_id,
            "name": member.name,
            "grade": member.grade,
            "purchase_count": f"{member.purchase_count}회",
            "first_purchase": member.first_purchase or "-",
            "last_purchase": member.last_purchase or "-",
            "coupon_used": "미사용",
            "points": f"{member.available_points:,}P"
        })
    
    return {
        "total_count": member_list.total_count,
        "page": member_list.page,
        "limit": member_list.limit,
        "items": items
    }