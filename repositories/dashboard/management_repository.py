# repositories/dashboard/management_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from models.models import Customer, Site, Product, Member, Order


class ManagementRepository:
    """개인정보 관리 관련 데이터베이스 쿼리"""
    
    @staticmethod
    async def get_customer_profile(db: AsyncSession, customer_id: int) -> Optional[Dict[str, Any]]:
        """고객 프로필 정보 조회"""
        query = (
            select(Customer, Site.site_name)
            .join(Site, Customer.customer_id == Site.customer_id)
            .where(Customer.customer_id == customer_id)
        )
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
            
        customer, site_name = row
        
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "site_name": site_name,
            "created_at": customer.created_at  # 실제 DB 값 사용
        }
    
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession, customer_id: int) -> Dict[str, Any]:
        """대시보드 통계 정보 조회"""
        # 고객의 사이트 ID 조회
        site_query = select(Site.site_id).where(Site.customer_id == customer_id)
        site_result = await db.execute(site_query)
        site_id = site_result.scalar_one_or_none()
        
        if not site_id:
            return {
                "total_products": 0,
                "total_customers": 0,
                "monthly_revenue": 0.0
            }
        
        # 등록상품 개수
        products_query = select(func.count(Product.product_id)).where(Product.site_id == site_id)
        products_result = await db.execute(products_query)
        total_products = products_result.scalar() or 0
        
        # 전체고객 수 (해당 사이트의 멤버 수)
        customers_query = select(func.count(Member.user_id)).where(Member.site_id == site_id)
        customers_result = await db.execute(customers_query)
        total_customers = customers_result.scalar() or 0
        
        # 이번달매출
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        revenue_query = (
            select(func.coalesce(func.sum(Order.payment_amount), 0))
            .join(Member, Order.user_id == Member.user_id)
            .where(
                and_(
                    Member.site_id == site_id,
                    extract('month', Order.order_date) == current_month,
                    extract('year', Order.order_date) == current_year
                )
            )
        )
        revenue_result = await db.execute(revenue_query)
        monthly_revenue = float(revenue_result.scalar() or 0)
        
        return {
            "total_products": total_products,
            "total_customers": total_customers,
            "monthly_revenue": monthly_revenue
        }
    
    @staticmethod
    async def update_customer_profile(
        db: AsyncSession, 
        customer_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[Customer]:
        """고객 프로필 정보 수정"""
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
        
        # 수정 가능한 필드만 업데이트
        for field, value in update_data.items():
            if hasattr(customer, field) and value is not None:
                setattr(customer, field, value)
        
        await db.commit()
        await db.refresh(customer)
        
        return customer
    
    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """고객 ID로 고객 정보 조회"""
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
