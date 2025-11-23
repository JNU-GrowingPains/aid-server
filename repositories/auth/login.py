from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.models import Customer


class LoginRepository:
    @staticmethod
    async def get_customer_by_email(
        db: AsyncSession,
        email: str,
    ) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()