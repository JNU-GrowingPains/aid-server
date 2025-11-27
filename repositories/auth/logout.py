# repositories/auth/logout.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.models import RefreshToken


class LogoutRepository:
    @staticmethod
    async def delete_refresh_token_by_token_and_customer(
        db: AsyncSession,
        token: str,
        customer_id: int,
    ) -> bool:
        """
        해당 customer가 소유한 refresh_token만 삭제.
        삭제 성공 시 True, 없으면 False 반환.
        """
        stmt = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.customer_id == customer_id,
        )
        result = await db.execute(stmt)
        refresh_token = result.scalars().first()

        if not refresh_token:
            return False

        del_stmt = delete(RefreshToken).where(
            RefreshToken.refresh_token_id == refresh_token.refresh_token_id
        )
        await db.execute(del_stmt)
        await db.commit()
        return True
