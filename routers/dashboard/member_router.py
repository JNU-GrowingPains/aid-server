# routers/dashboard/member_router.py

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

from services.dashboard.member_service import MemberService
from schemas.dashboard.member_schema import (
    MemberGradeStatsResponse, TopMemberResponse, MemberListResponse
)


class MemberRouter:
    """고객 분석 라우터"""
    
    def __init__(self):
        self.router = APIRouter(
            prefix="/api/v1/member-analysis",
            tags=["Member Analysis"],
            responses={404: {"description": "Not found"}}
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """라우터 설정"""
        
        @self.router.get(
            "/grade-stats",
            response_model=MemberGradeStatsResponse,
            summary="등급별 고객 수 통계",
            description="""
            고객 등급별 분포 통계를 조회합니다.
            
            **응답 데이터:**
            - total_members: 전체 고객 수
            - grade_distribution: 등급별 고객 수와 비율
            
            **활용:**
            - 막대그래프로 등급별 고객 분포 시각화
            - VIP, PLATINUM, GOLD, 슈둥이 등 등급별 현황 파악
            """
        )
        async def get_member_grade_statistics(
            db: AsyncSession = Depends(get_db)
        ):
            try:
                result = await MemberService.get_member_grade_statistics(db)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"등급별 통계 조회 실패: {str(e)}")
        
        @self.router.get(
            "/top-members",
            response_model=TopMemberResponse,
            summary="포인트 상위 고객",
            description="""
            포인트 기준 상위 고객 목록을 조회합니다.
            
            **응답 데이터:**
            - top_members: 상위 고객 목록 (순위, 이름, 등급, 주문수, 포인트)
            - total_count: 조회된 고객 수
            
            **활용:**
            - 오른쪽 패널에 포인트 상위 고객 표시
            - VIP 고객 관리 및 마케팅 타겟팅
            """
        )
        async def get_top_members(
            limit: int = Query(10, ge=1, le=50, description="조회할 상위 고객 수"),
            db: AsyncSession = Depends(get_db)
        ):
            try:
                result = await MemberService.get_top_members(db, limit)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"상위 고객 조회 실패: {str(e)}")
        
        @self.router.get(
            "/members",
            response_model=MemberListResponse,
            summary="고객 리스트",
            description="""
            전체 고객 목록을 페이지네이션으로 조회합니다.
            
            **필터링:**
            - grade: 등급 필터 (VIP, PLATINUM, GOLD, 슈둥이 등)
            
            **정렬 옵션:**
            - latest_purchase: 최근 구매일순 (기본값)
            - purchase_count: 구매횟수순
            - points: 포인트순
            - name: 이름순
            
            **정렬 순서:**
            - desc: 내림차순 (기본값)
            - asc: 오름차순
            
            **페이지네이션:**
            - page: 페이지 번호 (1부터 시작)
            - limit: 페이지당 항목 수 (최대 100개, **0 = 전체 데이터 조회**)
            
            **전체 데이터 조회:**
            - limit=0으로 설정 시 모든 데이터 반환 (최대 10,000개 제한)
            - 대량 데이터 조회 시 응답 시간이 길어질 수 있습니다
            
            **고객 정보:**
            - member_id: 고객 ID
            - name: 고객명
            - grade: 등급
            - purchase_count: 구매 횟수
            - available_points: 보유 포인트
            - first_purchase: 첫 구매일
            - last_purchase: 최근 구매일
            """
        )
        async def get_member_list(
            page: int = Query(1, ge=1, description="페이지 번호"),
            limit: int = Query(20, ge=0, le=100, description="페이지당 항목 수 (0 = 전체 조회)"),
            grade: Optional[str] = Query(None, description="등급 필터 (VIP, PLATINUM, GOLD 등)"),
            sort_by: str = Query("latest_purchase", description="정렬 기준 (latest_purchase, purchase_count, points, name)"),
            order: str = Query("desc", description="정렬 순서 (desc, asc)"),
            db: AsyncSession = Depends(get_db)
        ):
            try:
                result = await MemberService.get_member_list(
                    db, page, limit, grade, sort_by, order
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"고객 리스트 조회 실패: {str(e)}")


# 라우터 인스턴스 생성
member_router_instance = MemberRouter()
router = member_router_instance.router


# 기존 호환성을 위한 함수들
from services.dashboard.member_service import (
    get_customer_kpi, get_customer_grade_counts, get_customer_list
)

# 기존 엔드포인트들 (하위 호환성 유지)
@router.get("/kpis")
async def customer_kpis(
    db: AsyncSession = Depends(get_db)
):
    return await get_customer_kpi(db)

@router.get("/grades")
async def customer_grade_counts(
    db: AsyncSession = Depends(get_db)
):
    return await get_customer_grade_counts(db)

@router.get("/list")
async def customer_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=0, le=100),  # 0 허용 (전체 조회)
    grade: Optional[str] = Query(None),
    sort_by: str = Query("latest_purchase", pattern="^(latest_purchase|purchase_count|points|name)$"),
    db: AsyncSession = Depends(get_db)
):
    return await get_customer_list(db, page, limit, grade, sort_by)