#models/models.py

from sqlalchemy import (Column, Integer, BigInteger, String, Text, Date, ForeignKey, DateTime)
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
# 2. Categories
# -----------------------------
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_name = Column(String(50))
    category_no = Column(Integer)


# -----------------------------
# 3. Sites (pages)
# -----------------------------
class Site(Base):
    __tablename__ = "pages"

    site_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    site_url = Column(Text, nullable=False)
    site_name = Column(String(50))
    site_category = Column(String(50))
    site_tz = Column(String(50))

    # relationships
    customer = relationship("Customer", back_populates="sites")
    users = relationship("User", back_populates="site")
    products = relationship("Product", back_populates="site")
    visit_sources = relationship("VisitSource", back_populates="site")


# -----------------------------
# 4. Products
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_no = Column(Integer)
    product_name = Column(String(50))
    product_price = Column(String(20))
    site_id = Column(BigInteger, ForeignKey("pages.site_id"), nullable=False)

    # relationships
    site = relationship("Site", back_populates="products")
    order_products = relationship("OrderProduct", back_populates="product")
    events = relationship("Event", back_populates="product")
    reviews = relationship("Review", back_populates="product")


# -----------------------------
# 5. Orders
# -----------------------------
class Order(Base):
    __tablename__ = "orders"

    order_no = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(String(50), nullable=False)
    order_date = Column(Date)
    payment_amount = Column(Integer)
    billing_name = Column(String(50))
    payment_method_name = Column(String(100))
    order_destination = Column(String(100))
    order_phone_number = Column(String(50))

    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    member_id = Column(String(50), ForeignKey("members.member_id"))

    # relationships
    user = relationship("User", back_populates="orders")
    member = relationship("Member", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")



# -----------------------------
# 6. Order Products (order details)
# -----------------------------
class OrderProduct(Base):
    __tablename__ = "order_products"

    order_product_no = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    order_date = Column(Date)
    order_product_count = Column(Integer)
    order_product_amount = Column(Integer)   # 매출액
    order_quantity = Column(Integer)  # 주문 수량
    order_id = Column(String(50))
    order_no = Column(BigInteger, ForeignKey("orders.order_no"), nullable=False)
    product_name = Column(String(50))
    product_price = Column(Integer)
    is_dirty = Column(Integer, default=0)

    # relationships
    product = relationship("Product", back_populates="order_products")
    order = relationship("Order", back_populates="order_products")



# -----------------------------
# 7. Member
# -----------------------------
class Member(Base):
    __tablename__ = "members"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(String(50))

    available_points = Column(Integer, default=0)
    group_no = Column(Integer)
    last_login_date = Column(Date)
    site_id = Column(BigInteger, ForeignKey("pages.site_id"))
    group_id = Column(BigInteger, ForeignKey("member_groups.group_id"), nullable=False)
    address_1 = Column(String(100))  # 주소
    address_2 = Column(String(50))  # 상세 주소
    phone_number = Column(String(20))  # 휴대폰 번호

    # relationships
    group = relationship("MemberGroup", back_populates="members")
    orders = relationship("Order", back_populates="member")
    reviews = relationship("Review", back_populates="member")



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
    rating = Column(Integer)
    content = Column(Text)
    created_date = Column(String(20))
    hit = Column(Integer, default=0)
    product_no = Column(Integer)
    member_id = Column(String(50), ForeignKey("members.member_id"))
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)

    # relationships
    product = relationship("Product", back_populates="reviews")
    member = relationship("Member", back_populates="reviews")



# -----------------------------
# Users (internal users)
# -----------------------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    site_id = Column(BigInteger, ForeignKey("pages.site_id"), nullable=False)

    # relationships
    site = relationship("Site", back_populates="users")
    orders = relationship("Order", back_populates="user")
    events = relationship("Event", back_populates="user")


# -----------------------------
# Visit Sources
# -----------------------------
class VisitSource(Base):
    __tablename__ = "visit_sources"

    source_id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_type = Column(String(20))   # 광고매체, URL, 키워드
    visit_count = Column(Integer)      # 유입자 수
    site_id = Column(BigInteger, ForeignKey("pages.site_id"), nullable=False)

    # relationships
    site = relationship("Site", back_populates="visit_sources")


# -----------------------------
# Events
# -----------------------------
class Event(Base):
    __tablename__ = "events"

    event_id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_day = Column(Date)
    event_category = Column(String(20))   # 클릭, 장바구니 추가 등
    event_count = Column(Integer)         # 일별 클릭수, 장바구니 추가 수
    product_id = Column(BigInteger, ForeignKey("products.product_id"))
    user_id = Column(BigInteger, ForeignKey("users.user_id"))

    # relationships
    product = relationship("Product", back_populates="events")
    user = relationship("User", back_populates="events")


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