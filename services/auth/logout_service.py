# services/auth/logout_repository.py

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.auth.logout_repository import LogoutRepository
from schemas.auth.logout_schema import LogoutRequest, LogoutResponse


class LogoutService:
    @staticmethod
    async def logout(
        db: AsyncSession,
        customer_id: int,
        data: LogoutRequest,
    ) -> LogoutResponse:
        """
        특정 사용자가 가진 refresh_token 하나를 삭제 (해당 세션 로그아웃).
        """
        deleted = await LogoutRepository.delete_refresh_token_by_token_and_customer(
            db=db,
            token=data.refresh_token,
            customer_id=customer_id,
        )

        if not deleted:
            # 이미 삭제됐거나, 본인 소유가 아니거나, 잘못된 토큰
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found",
            )

        return LogoutResponse(detail="Successfully logged out")
