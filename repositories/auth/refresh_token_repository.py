# repositories/auth/refresh_token_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.models import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    async def create(
        db: AsyncSession,
        customer_id: int,
        token: str,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            customer_id=customer_id,
            token=token,
        )
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token

    @staticmethod
    async def get_by_token(
        db: AsyncSession,
        token: str,
    ) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def delete_by_id(
        db: AsyncSession,
        refresh_token_id: int,
    ) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.refresh_token_id == refresh_token_id)
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def delete_all_by_customer(
        db: AsyncSession,
        customer_id: int,
    ) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.customer_id == customer_id)
        await db.execute(stmt)
        await db.commit()