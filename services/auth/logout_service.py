# services/auth/logout_repository.py

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.auth.logout_repository import LogoutRepository
from schemas.auth.logout_schema import LogoutResponse


class LogoutService:
    @staticmethod
    async def logout(
        db: AsyncSession,
        customer_id: int,
    ) -> LogoutResponse:
        """
        해당 사용자의 모든 refresh_token 삭제 (모든 세션 종료).
        """
        await LogoutRepository.delete_all_refresh_tokens_by_customer(
            db=db,
            customer_id=customer_id,
        )

        return LogoutResponse(detail="Successfully logged out from all devices")
