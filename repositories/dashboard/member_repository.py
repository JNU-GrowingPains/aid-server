# repositories/dashboard/member_repository.py

from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Member, MemberGroup, Order


class MemberRepository:
    """고객 분석 관련 데이터베이스 쿼리"""
    
    @staticmethod
    async def get_member_grade_distribution(db: AsyncSession) -> List[Dict[str, Any]]:
        """등급별 고객 수 분포 조회 (막대그래프용)"""
        # 전체 고객 수
        total_query = select(func.count(Member.user_id))
        total_members = (await db.execute(total_query)).scalar() or 0
        
        # 등급별 고객 수
        grade_query = (
            select(
                MemberGroup.group_name.label("grade_name"),
                func.count(Member.user_id).label("member_count")
            )
            .join(Member, Member.group_id == MemberGroup.group_id)
            .group_by(MemberGroup.group_name)
            .order_by(MemberGroup.group_name)
        )
        
        result = await db.execute(grade_query)
        grade_data = []
        
        for row in result.all():
            percentage = (row.member_count / total_members * 100) if total_members > 0 else 0
            grade_data.append({
                "grade_name": row.grade_name,
                "member_count": row.member_count,
                "percentage": round(percentage, 1)
            })
        
        return {
            "total_members": total_members,
            "grade_distribution": grade_data
        }
    
    @staticmethod
    async def get_top_members_by_points(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """포인트 상위 고객 조회 (오른쪽 패널용)"""
        # 최근 주문의 billing_name을 가져오는 서브쿼리
        subq_name = select(Order.billing_name).where(
            Order.user_id == Member.user_id
        ).order_by(desc(Order.order_date)).limit(1).correlate(Member).scalar_subquery()
        
        query = (
            select(
                Member.user_id,
                Member.member_id,
                subq_name.label("name"),
                MemberGroup.group_name.label("grade"),
                Member.available_points,
                func.count(Order.order_id).label("purchase_count")
            )
            .join(MemberGroup, Member.group_id == MemberGroup.group_id)
            .outerjoin(Order, Member.user_id == Order.user_id)
            .group_by(Member.user_id, Member.member_id, MemberGroup.group_name, Member.available_points)
            .order_by(desc(Member.available_points))
            .limit(limit)
        )
        
        result = await db.execute(query)
        top_members = []
        
        for rank, row in enumerate(result.all(), 1):
            top_members.append({
                "user_id": row.user_id,
                "member_id": row.member_id,
                "name": row.name or row.member_id,  # billing_name을 이름으로 사용, 없으면 member_id
                "grade": row.grade,
                "purchase_count": row.purchase_count or 0,
                "available_points": row.available_points or 0,
                "rank": rank
            })
        
        return {
            "top_members": top_members,
            "total_count": len(top_members)
        }
    
    @staticmethod
    async def get_member_list(
        db: AsyncSession, 
        page: int, 
        limit: int, 
        grade_filter: Optional[str] = None,
        sort_by: str = "latest_purchase",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        고객 리스트 조회 (필터링/정렬 지원)
        
        limit=0: 전체 데이터 조회 (최대 10,000개 제한)
        """
        # 최근 주문의 billing_name을 가져오는 서브쿼리
        subq_name = select(Order.billing_name).where(
            Order.user_id == Member.user_id
        ).order_by(desc(Order.order_date)).limit(1).correlate(Member).scalar_subquery()
        
        query = (
            select(
                Member.user_id,
                Member.member_id,
                subq_name.label("name"),
                MemberGroup.group_name.label("grade"),
                Member.available_points,
                func.count(Order.order_id).label("purchase_count"),
                func.max(Order.order_date).label("last_purchase"),
                func.min(Order.order_date).label("first_purchase")
            )
            .join(MemberGroup, Member.group_id == MemberGroup.group_id)
            .outerjoin(Order, Member.user_id == Order.user_id)
            .group_by(Member.user_id, Member.member_id, MemberGroup.group_name, Member.available_points)
        )
        
        # 등급 필터 적용
        if grade_filter and grade_filter != "전체":
            query = query.where(MemberGroup.group_name == grade_filter)
        
        # 정렬 적용
        order_func = desc if order == "desc" else asc
        
        if sort_by == "purchase_count":
            query = query.order_by(order_func("purchase_count"))
        elif sort_by == "points":
            query = query.order_by(order_func(Member.available_points))
        elif sort_by == "name":
            query = query.order_by(order_func(Member.member_id))
        else:  # latest_purchase
            query = query.order_by(order_func("last_purchase"))
        
        # 전체 개수 조회
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await db.execute(count_query)).scalar() or 0
        
        # 전체 데이터 조회 여부 확인
        fetch_all = (limit == 0)
        
        if fetch_all:
            # 전체 데이터 조회 (안전장치: 최대 10,000개)
            actual_limit = min(total_count, 10000)
            query = query.limit(actual_limit)
            page = 1
            limit = actual_limit
        else:
            # 페이징 적용
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        members = []
        
        for row in result.all():
            members.append({
                "user_id": row.user_id,
                "member_id": row.member_id,
                "name": row.name or row.member_id,  # billing_name을 이름으로 사용, 없으면 member_id
                "grade": row.grade,
                "purchase_count": row.purchase_count or 0,
                "first_purchase": row.first_purchase,
                "last_purchase": row.last_purchase,
                "available_points": row.available_points or 0
            })
        
        # total_pages 계산
        if fetch_all or limit == 0:
            total_pages = 1
        else:
            total_pages = (total_count + limit - 1) // limit
        
        return {
            "members": members,
            "total_count": total_count,
            "page": page,
            "limit": limit if not fetch_all else len(members),
            "total_pages": total_pages
        }


# 기존 함수들 (하위 호환성을 위해 유지)
async def fetch_customer_kpi(db: AsyncSession):
    """기존 호환성을 위한 함수"""
    grade_stats = await MemberRepository.get_member_grade_distribution(db)
    total = grade_stats["total_members"]
    vip_count = 0
    
    for grade in grade_stats["grade_distribution"]:
        if grade["grade_name"] == "VIP":
            vip_count = grade["member_count"]
            break
    
    return total, 0, vip_count

async def fetch_customer_grade_dist(db: AsyncSession):
    """기존 호환성을 위한 함수"""
    grade_stats = await MemberRepository.get_member_grade_distribution(db)
    
    # 기존 형식으로 변환
    result = []
    for grade in grade_stats["grade_distribution"]:
        result.append(type('Row', (), {
            'grade': grade["grade_name"],
            'count': grade["member_count"]
        })())
    
    return result

async def fetch_customer_list(db: AsyncSession, page: int, limit: int, grade: Optional[str], sort_by: str):
    """기존 호환성을 위한 함수"""
    member_data = await MemberRepository.get_member_list(
        db, page, limit, grade, sort_by, "desc"
    )
    
    # 기존 형식으로 변환
    result = []
    for member in member_data["members"]:
        result.append(type('Row', (), {
            'user_id': member["user_id"],
            'name': member["name"],
            'grade': member["grade"],
            'point': member["available_points"],
            'purchase_count': member["purchase_count"],
            'last_purchase': member["last_purchase"],
            'first_purchase': member["first_purchase"]
        })())
    
    return result, member_data["total_count"]