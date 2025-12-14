from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum

class UserRole(Enum):
    ADMIN = "Admin"
    INVENTORY_MANAGER = "inventory_manager"
    USER = "user"

Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    user_role = Column(
        String,
        nullable=False,
        server_default=text("'User'")
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    carts = relationship("CartTable", back_populates="user", cascade="all, delete")
    purchases = relationship("PurchaseHistory", back_populates="user")


class ProductTable(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False, unique=True)
    product_price = Column(Float, nullable=False)
    product_stockqty = Column(Integer, nullable=False)

    # Relationships
    carts = relationship("CartTable", back_populates="product", cascade="all, delete")
    purchases = relationship("PurchaseHistory", back_populates="product")


class CartTable(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False, default=1)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))

    # Relationships
    user = relationship("UserTable", back_populates="carts")
    product = relationship("ProductTable", back_populates="carts")


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    purchase_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="SET NULL"))
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("UserTable", back_populates="purchases")
    product = relationship("ProductTable", back_populates="purchases")

class RefreshTokenTable(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

