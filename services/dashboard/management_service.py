# services/dashboard/management_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from repositories.dashboard.management_repository import ManagementRepository
from schemas.dashboard.management_schema import (
    CustomerProfileResponse, 
    DashboardStatsResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse
)


class ManagementService:
    """개인정보 관리 비즈니스 로직"""
    
    @staticmethod
    async def get_customer_profile(
        db: AsyncSession, 
        customer_id: int
    ) -> CustomerProfileResponse:
        """고객 프로필 조회"""
        profile_data = await ManagementRepository.get_customer_profile(db, customer_id)
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        
        return CustomerProfileResponse(**profile_data)
    
    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession, 
        customer_id: int
    ) -> DashboardStatsResponse:
        """대시보드 통계 조회"""
        stats_data = await ManagementRepository.get_dashboard_stats(db, customer_id)
        
        return DashboardStatsResponse(**stats_data)
    
    @staticmethod
    async def update_customer_profile(
        db: AsyncSession,
        customer_id: int,
        update_request: ProfileUpdateRequest
    ) -> ProfileUpdateResponse:
        """고객 프로필 수정"""
        # 기존 고객 정보 확인
        existing_customer = await ManagementRepository.get_customer_by_id(db, customer_id)
        if not existing_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # 수정할 데이터 준비 (None이 아닌 값만)
        update_data = {}
        if update_request.name is not None:
            if not update_request.name.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Name cannot be empty"
                )
            update_data["name"] = update_request.name.strip()
        
        # 수정할 데이터가 없는 경우
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid data to update"
            )
        
        # 프로필 업데이트
        updated_customer = await ManagementRepository.update_customer_profile(
            db, customer_id, update_data
        )
        
        if not updated_customer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        # 업데이트된 프로필 정보 조회
        updated_profile = await ManagementService.get_customer_profile(db, customer_id)
        
        return ProfileUpdateResponse(
            success=True,
            message="Profile updated successfully",
            updated_data=updated_profile
        )
