# routers/dashboard/management_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.auth.token_service import TokenService
from services.dashboard.management_service import ManagementService
from schemas.dashboard.management_schema import (
    CustomerProfileResponse,
    DashboardStatsResponse, 
    ProfileUpdateRequest,
    ProfileUpdateResponse
)

router = APIRouter(prefix="/api/v1/management", tags=["Management"])
security = HTTPBearer()


def get_current_customer_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Authorization 헤더의 Bearer 토큰에서 customer_id 추출.
    """
    token = credentials.credentials  # "Bearer xxx" 중 xxx 부분
    return TokenService.get_current_customer_id(token)


@router.get(
    "/profile",
    response_model=CustomerProfileResponse,
    summary="고객 프로필 조회"
)
async def get_customer_profile(
    db: AsyncSession = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id)
):
    """
    현재 로그인한 고객의 프로필 정보를 조회합니다.
    
    - **이름**: 고객 이름
    - **이메일**: 고객 이메일 주소
    - **가입일**: 고객 계정 생성일
    - **사이트명**: 고객이 소유한 사이트 이름
    """
    return await ManagementService.get_customer_profile(db, customer_id)


@router.get(
    "/dashboard-stats",
    response_model=DashboardStatsResponse,
    summary="대시보드 통계 조회"
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id)
):
    """
    고객 사이트의 대시보드 통계 정보를 조회합니다.
    
    - **등록상품 개수**: 해당 사이트에 등록된 상품 수
    - **전체고객 수**: 해당 사이트의 회원 수
    - **이번달매출**: 해당 사이트의 이번 달 매출 합계
    """
    return await ManagementService.get_dashboard_stats(db, customer_id)


@router.put(
    "/profile",
    response_model=ProfileUpdateResponse,
    summary="고객 프로필 수정"
)
async def update_customer_profile(
    update_request: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id)
):
    """
    현재 로그인한 고객의 프로필 정보를 수정합니다.
    
    - **name**: 수정할 고객 이름 (선택사항)
    
    수정 가능한 필드만 업데이트되며, None 값은 무시됩니다.
    """
    return await ManagementService.update_customer_profile(db, customer_id, update_request)
