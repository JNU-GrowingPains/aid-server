# repositories/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import Customer, Site


class CustomerRepository:

    @staticmethod
    async def get_customer_by_email(db: AsyncSession, email: str):
        result = await db.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_customer(db: AsyncSession, name: str, email: str, hashed_pw: str, category: str):
        customer = Customer(
            name=name,
            email=email,
            password=hashed_pw,
            customer_category=category
        )
        db.add(customer)
        await db.flush()  # customer_id 확보
        return customer

    @staticmethod
    async def create_site(db: AsyncSession, customer_id: int, site_name: str, site_url: str, site_tz: str, site_category: str):
        site = Site(
            customer_id=customer_id,
            site_name=site_name,
            site_url=site_url,
            site_tz=site_tz,
            site_category=site_category
        )
        db.add(site)
        return site
