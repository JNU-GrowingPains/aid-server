#models/models.py

from sqlalchemy import (Column, Integer, BigInteger, String, Text, Date, ForeignKey, DateTime, UniqueConstraint)
from sqlalchemy.orm import relationship
from database.session import Base
from datetime import datetime, timezone


# -----------------------------
# 1. Customers
# -----------------------------
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(100))  # DDL에서는 unique 제약이 없음
    password = Column(String(255))
    customer_category = Column(String(50))
    created_at = Column(DateTime, nullable=True)  # 가입일

    # relationships
    sites = relationship("Site", back_populates="customer")
    refresh_tokens = relationship("RefreshToken", back_populates="customer")


# -----------------------------
# 2. Sites
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
# 3. MemberGroup (DDL 순서에 맞춰 Member보다 먼저)
# -----------------------------
class MemberGroup(Base):
    __tablename__ = "member_groups"

    group_id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_no = Column(Integer)
    group_name = Column(String(50))
    group_description = Column(String(50))

    # relationships
    members = relationship("Member", back_populates="group")


# -----------------------------
# 4. Members
# -----------------------------
class Member(Base):
    __tablename__ = "members"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(String(50))  # DDL에서는 UNIQUE 제약
    available_points = Column(Integer)
    group_no = Column(Integer)
    group_id = Column(BigInteger, ForeignKey("member_groups.group_id"))
    last_login_date = Column(Date)
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)

    # relationships
    group = relationship("MemberGroup", back_populates="members")
    orders = relationship("Order", back_populates="member")
    reviews = relationship("Review", back_populates="member")
    site = relationship("Site", back_populates="members")

    # DDL의 unique 제약 조건 (member_id만)
    __table_args__ = (
        UniqueConstraint('member_id', name='uq_members_member_id'),
    )


# -----------------------------
# 5. Products
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_no = Column(Integer)  # DDL에서는 UNIQUE 제약
    product_name = Column(String(50))
    product_price = Column(String(50))  # DDL과 맞춤 (String(20) -> String(50))
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)
    product_display = Column(String(10))
    product_category = Column(String(50))

    # relationships
    site = relationship("Site", back_populates="products")
    order_products = relationship("OrderProduct", back_populates="product")
    reviews = relationship("Review", back_populates="product")

    # DDL의 unique 제약 조건
    __table_args__ = (
        UniqueConstraint('product_no', name='uq_products_product_no'),
    )


# -----------------------------
# 6. Orders (DDL 구조에 맞춤)
# -----------------------------
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(BigInteger, primary_key=True, autoincrement=True)  # DDL의 PK
    external_order_id = Column(String(50), nullable=False)  # DDL의 UNIQUE 필드
    order_date = Column(Date)
    payment_amount = Column(Integer)
    billing_name = Column(String(10))  # DDL과 맞춤
    payment_method_name = Column(String(30))  # DDL과 맞춤
    member_id = Column(String(50))
    user_id = Column(BigInteger, ForeignKey("members.user_id"))
    order_address_1 = Column(String(100))
    order_address_2 = Column(String(100))
    order_phone_number = Column(String(20))
    order_email = Column(String(50))

    # relationships
    member = relationship("Member", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")

    # DDL의 unique 제약 조건
    __table_args__ = (
        UniqueConstraint('external_order_id', name='uq_orders_external_order_id'),
    )


# -----------------------------
# 7. OrderProduct (DDL 구조에 맞춤)
# -----------------------------
class OrderProduct(Base):
    __tablename__ = "order_products"

    order_product_id = Column(BigInteger, primary_key=True, autoincrement=True)  # DDL의 PK명
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)
    external_order_id = Column(String(50), nullable=False)  # DDL에 있는 필드
    product_no = Column(Integer)
    product_id = Column(BigInteger, ForeignKey("products.product_id"))
    product_name = Column(String(50))
    product_price = Column(String(50))  # DDL과 맞춤
    order_quantity = Column(Integer)
    order_product_amount = Column(Integer)
    order_date = Column(Date)

    # relationships
    product = relationship("Product", back_populates="order_products")
    order = relationship("Order", back_populates="order_products")


# -----------------------------
# 8. Review
# -----------------------------
class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    writer = Column(String(20))  # DDL과 맞춤 (String(50) -> String(20))
    content = Column(Text)
    rating = Column(Integer)
    created_date = Column(String(20))
    hit = Column(Integer)
    product_no = Column(Integer)
    member_id = Column(String(50))
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("members.user_id"), nullable=False)

    # relationships
    product = relationship("Product", back_populates="reviews")
    member = relationship("Member", back_populates="reviews")


# -----------------------------
# 9. RefreshToken
# -----------------------------
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    token = Column(String(512), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)

    # relationships
    customer = relationship("Customer", back_populates="refresh_tokens")