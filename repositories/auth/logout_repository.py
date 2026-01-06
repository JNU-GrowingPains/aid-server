# repositories/auth/logout_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.models import RefreshToken


class LogoutRepository:
    @staticmethod
    async def delete_all_refresh_tokens_by_customer(
        db: AsyncSession,
        customer_id: int,
    ) -> None:
        """
        해당 고객의 모든 refresh_token 삭제 (모든 디바이스에서 로그아웃).
        """
        stmt = delete(RefreshToken).where(RefreshToken.customer_id == customer_id)
        await db.execute(stmt)
        await db.commit()
