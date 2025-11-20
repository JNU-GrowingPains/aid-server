from sqlalchemy import (Column, Integer, BigInteger, String, Text, Date, ForeignKey)
from sqlalchemy.orm import relationship
from database.database import Base


# -----------------------------
# Customers
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


# -----------------------------
# Categories
# -----------------------------
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_name = Column(String(50))
    category_carts_count_per = Column(Integer)      # 카테고리별 담긴 수
    category_sales_price_per = Column(Integer)      # 카테고리별 상품 판매 금액
    page_url = Column(Text)

    # relationships
    products = relationship("Product", back_populates="category")


# -----------------------------
# Sites (pages)
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
# Users (internal users)
# -----------------------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)

    # relationships
    site = relationship("Site", back_populates="users")
    orders = relationship("Order", back_populates="user")
    events = relationship("Event", back_populates="user")


# -----------------------------
# Products
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_code = Column(String(50))
    product_name = Column(String(50))
    order_count = Column(Integer)              # 상품 조회수
    device = Column(String(20))
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.category_id"), nullable=False)

    # relationships
    site = relationship("Site", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_products = relationship("OrderProduct", back_populates="product")
    events = relationship("Event", back_populates="product")


# -----------------------------
# Orders
# -----------------------------
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_date = Column(Date)
    order_count = Column(Integer)      # 주문 건수
    order_amount = Column(Integer)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))

    # relationships
    user = relationship("User", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")


# -----------------------------
# Order Products (order details)
# -----------------------------
class OrderProduct(Base):
    __tablename__ = "order_products"

    order_product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    order_product_date = Column(Date)
    order_product_count = Column(BigInteger)    # 판매 물품 수
    order_product_amount = Column(BigInteger)   # 매출액
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)

    # relationships
    product = relationship("Product", back_populates="order_products")
    order = relationship("Order", back_populates="order_products")


# -----------------------------
# Visit Sources
# -----------------------------
class VisitSource(Base):
    __tablename__ = "visit_sources"

    source_id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_type = Column(String(20))   # 광고매체, URL, 키워드
    visit_count = Column(Integer)      # 유입자 수
    site_id = Column(BigInteger, ForeignKey("sites.site_id"), nullable=False)

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
