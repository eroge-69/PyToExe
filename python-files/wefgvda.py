Python 3.9.0 (tags/v3.9.0:9cf6752, Oct  5 2020, 15:34:40) [MSC v.1927 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> from __future__ import annotations
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, ForeignKey, UniqueConstraint, func, String, Integer, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class InteractionType(str, Enum):
    view = "view"
    add_to_cart = "add_to_cart"
    purchase = "purchase"
    like = "like"

class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    products: Mapped[List["Product"]] = relationship(back_populates="brand")

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    products: Mapped[List["Product"]] = relationship(back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(4000), default=None)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10,2), default=0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    images: Mapped[list[str]] = mapped_column(JSON, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    brand_id: Mapped[Optional[int]] = mapped_column(ForeignKey("brands.id"))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))

    brand: Mapped[Optional[Brand]] = relationship(back_populates="products")
    category: Mapped[Optional[Category]] = relationship(back_populates="products")
    variants: Mapped[List["Variant"]] = relationship(back_populates="product", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    sku: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    color: Mapped[str] = mapped_column(String(40), index=True)
    size: Mapped[str] = mapped_column(String(20), index=True)
    additional_price: Mapped[Decimal] = mapped_column(Numeric(10,2), default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="variants")
    __table_args__ = (
        UniqueConstraint("product_id", "color", "size", name="uix_product_color_size"),
    )

class Interaction(Base):
    __tablename__ = "interactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), index=True)  # can be session or customer id
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    type: Mapped[InteractionType] = mapped_column(default=InteractionType.view)
    weight: Mapped[float] = mapped_column(default=1.0)
    product: Mapped[Product] = relationship()
    
SyntaxError: multiple statements found while compiling a single statement
>>> 