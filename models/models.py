# models.py : db 테이블 구조 (무엇을 저장하는지)
from __future__ import annotations
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Integer, String, Date, ForeignKey

class Base(DeclarativeBase):
    pass

# ---------- pages / customers ----------
class Customer(Base):
    __tablename__ = "customers"
    customer_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name:          Mapped[Optional[str]] = mapped_column(String(50))
    email:         Mapped[Optional[str]] = mapped_column(String(100))
    password:      Mapped[Optional[str]] = mapped_column(String(255))
    customer_category: Mapped[Optional[str]] = mapped_column(String(50))

    pages: Mapped[List["Page"]] = relationship(back_populates="customer")

class Page(Base):
    __tablename__ = "pages"
    site_id:      Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site_url:     Mapped[str] = mapped_column(String(255), nullable=False)
    site_name:    Mapped[Optional[str]] = mapped_column(String(50))
    site_category:Mapped[Optional[str]] = mapped_column(String(50))
    site_tz:      Mapped[Optional[str]] = mapped_column(String(50))
    customer_id:  Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="pages")
    users:    Mapped[List["User"]] = relationship(back_populates="page")
    visits:   Mapped[List["VisitSource"]] = relationship(back_populates="page")
    products: Mapped[List["Product"]] = relationship(back_populates="page")

# ---------- users / orders ----------
class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("pages.site_id"), nullable=False)

    page:   Mapped["Page"] = relationship(back_populates="users")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    events: Mapped[List["Event"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    order_id:     Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_date:   Mapped[Optional[date]] = mapped_column(Date)
    order_count:  Mapped[Optional[int]] = mapped_column(BigInteger)
    order_amount: Mapped[Optional[int]] = mapped_column(BigInteger)
    user_id:      Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderProduct"]] = relationship(back_populates="order")

# ---------- categories / products ----------
class Category(Base):
    __tablename__ = "categories"
    category_no:    Mapped[int] = mapped_column("category_id", BigInteger, primary_key=True, autoincrement=True)
    category_name:  Mapped[Optional[str]] = mapped_column(String(50))
    category_carts_count_per: Mapped[Optional[int]] = mapped_column(BigInteger)
    category_sales_price_per: Mapped[Optional[int]] = mapped_column(BigInteger)
    page_url:       Mapped[Optional[str]] = mapped_column(String(255))

    products: Mapped[List["Product"]] = relationship(back_populates="category")

class Product(Base):
    __tablename__ = "products"
    product_no:   Mapped[int] = mapped_column("product_id", BigInteger, primary_key=True, autoincrement=True)
    product_code: Mapped[Optional[str]] = mapped_column(String(50))
    product_name: Mapped[Optional[str]] = mapped_column(String(50))
    order_count:  Mapped[Optional[int]] = mapped_column(BigInteger)
    device:       Mapped[Optional[str]] = mapped_column(String(20))   # PC/모바일/기타
    site_id:      Mapped[int] = mapped_column(BigInteger, ForeignKey("pages.site_id"), nullable=False)
    category_no:  Mapped[int] = mapped_column("category_id", BigInteger, ForeignKey("categories.category_id"), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products")
    page:     Mapped["Page"] = relationship(back_populates="products")
    items:    Mapped[List["OrderProduct"]] = relationship(back_populates="product")
    events:   Mapped[List["Event"]] = relationship(back_populates="product")

# ---------- order_products ----------
class OrderProduct(Base):
    __tablename__ = "order_products"
    order_product_id:  Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_no:        Mapped[int] = mapped_column("product_id", BigInteger, ForeignKey("products.product_id"), nullable=False)
    order_product_date:   Mapped[Optional[date]] = mapped_column(Date)
    order_product_count:  Mapped[Optional[int]] = mapped_column(BigInteger)
    order_product_amount: Mapped[Optional[int]] = mapped_column(BigInteger)
    order_id:            Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("orders.order_id"))

    product: Mapped["Product"] = relationship(back_populates="items")
    order:   Mapped["Order"]   = relationship(back_populates="items")

# ---------- visit_sources / events ----------
class VisitSource(Base):
    __tablename__ = "visit_sources"
    source_id:   Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(20))
    visit_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    site_id:     Mapped[int] = mapped_column(BigInteger, ForeignKey("pages.site_id"), nullable=False)

    page: Mapped["Page"] = relationship(back_populates="visits")

class Event(Base):
    __tablename__ = "events"
    event_id:      Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_day:     Mapped[Optional[date]] = mapped_column(Date)
    event_category:Mapped[Optional[str]] = mapped_column(String(20))  # 클릭/장바구니추가 등
    event_count:   Mapped[Optional[int]] = mapped_column(BigInteger)
    product_no:    Mapped[int] = mapped_column("product_id", BigInteger, ForeignKey("products.product_id"))
    user_id:       Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    product: Mapped["Product"] = relationship(back_populates="events")
    user:    Mapped["User"]    = relationship(back_populates="events")
