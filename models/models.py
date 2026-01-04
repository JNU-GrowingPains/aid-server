#models/models.py

from sqlalchemy import (Column, Integer, BigInteger, String, Text, Date, ForeignKey, DateTime, UniqueConstraint)
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime, timezone


# -----------------------------
# 1. Customers
# -----------------------------
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(255))
    customer_category = Column(String(50))

    # relationships
    sites = relationship("Site", back_populates="customer")
    refresh_tokens = relationship("RefreshToken", back_populates="customer")


# -----------------------------
# 3. Sites (pages)
# -----------------------------
class Site(Base):
    __tablename__ = "sites"

    site_id = Column(BigInteger, primary_key=True, autoincrement=True)
    site_url = Column(Text, nullable=False)
    site_name = Column(String(50))
    site_category = Column(String(50))
    site_tz = Column(String(50))
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)

    # relationships
    customer = relationship("Customer", back_populates="sites")
    members = relationship("Member", back_populates="site")
    products = relationship("Product", back_populates="site")


# -----------------------------
# 4. Products
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_no = Column(Integer)
    product_name = Column(String(50))
    product_price = Column(String(20))
    product_display = Column(String(10))
    product_category = Column(String(50), nullable=True)

    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)

    # relationships
    site = relationship("Site", back_populates="products")
    order_products = relationship("OrderProduct", back_populates="product")
    reviews = relationship("Review", back_populates="product")


# -----------------------------
# 5. Orders
# -----------------------------
class Order(Base):
    __tablename__ = "orders"

    order_no = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(String(50), nullable=False)
    order_date = Column(Date, nullable=True)
    payment_amount = Column(Integer, nullable=True)
    billing_name = Column(String(50), nullable=True)
    payment_method_name = Column(String(100), nullable=True)
    order_address_1 = Column(String(100), nullable=True)
    order_address_2 = Column(String(100), nullable=True)
    order_phone_number = Column(String(20), nullable=True)
    order_email = Column(String(50), nullable=True)

    member_id = Column(String(50), nullable=True)
    user_id = Column(BigInteger, ForeignKey("members.user_id"), nullable=True)
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)

    # relationships
    member = relationship("Member", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")
    site = relationship("Site", back_populates="orders")


# -----------------------------
# 6. Order Products (order details)
# -----------------------------
class OrderProduct(Base):
    __tablename__ = "order_products"

    order_product_no = Column(BigInteger, primary_key=True, autoincrement=True)
    order_product_count = Column(Integer)
    order_date = Column(Date)
    product_name = Column(String(50))
    product_price = Column(Integer)
    order_quantity = Column(Integer)  # 주문 수량
    order_product_amount = Column(Integer)   # 매출액
    order_id = Column(String(50))
    is_dirty = Column(Integer, default=0)
    order_no = Column(BigInteger, ForeignKey("orders.order_no"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)

    # relationships
    product = relationship("Product", back_populates="order_products")
    order = relationship("Order", back_populates="order_products")



# -----------------------------
# 7. Member
# -----------------------------
class Member(Base):
    __tablename__ = "members"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(String(50), nullable=False)
    available_points = Column(Integer, default=0)
    group_no = Column(Integer, nullable=True)
    last_login_date = Column(Date, nullable=True)
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)
    group_id = Column(BigInteger, ForeignKey("member_groups.group_id"), nullable=False)

    # relationships
    group = relationship("MemberGroup", back_populates="members")
    orders = relationship("Order", back_populates="member")
    reviews = relationship("Review", back_populates="member")
    site = relationship("Site", back_populates="members")
    # 하나의 사이트 내에서 member_id가 중복되면 안된다는 제약 조건
    __table_args__ = (
        UniqueConstraint('site_id', 'member_id', name='uix_site_member_id'),
    )

# -----------------------------
# 8. MemberGroup
# -----------------------------
class MemberGroup(Base):
    __tablename__ = "member_groups"

    group_id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_no = Column(Integer)  # 관리번호
    group_name = Column(String(50))
    group_description = Column(String(50))

    # relationships
    members = relationship("Member", back_populates="group")



# -----------------------------
# 9. Review
# -----------------------------
class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    writer = Column(String(50))
    content = Column(Text)
    rating = Column(Integer)
    created_date = Column(String(20))
    hit = Column(Integer, default=0)
    product_no = Column(Integer)
    member_id = Column(String(50), nullable=True)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("members.user_id"), nullable=False)

    # relationships
    product = relationship("Product", back_populates="reviews")
    member = relationship("Member", back_populates="reviews")


# -----------------------------
# Refresh Tokens
# -----------------------------
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(
        BigInteger,
        ForeignKey("customers.customer_id"),
        nullable=False
    )
    token = Column(String(512), nullable=False, unique=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # relationships
    customer = relationship("Customer", back_populates="refresh_tokens")