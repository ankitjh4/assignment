"""SQLAlchemy ORM models matching Database/schema.sql."""

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(String, nullable=False, server_default=text("(datetime('now'))"))

    orders = relationship("Order", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    is_bulk_available = Column(Integer, nullable=False, default=0)
    is_low_sugar = Column(Integer, nullable=False, default=0)
    calories = Column(Integer)
    stock_quantity = Column(Integer, nullable=False, default=0)

    orders = relationship("Order", back_populates="product")
    promotions = relationship("Promotion", back_populates="product")
    product_ingredients = relationship("ProductIngredient", back_populates="product")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    is_allergen = Column(Integer, nullable=False, default=0)

    product_ingredients = relationship("ProductIngredient", back_populates="ingredient")


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"
    __table_args__ = (UniqueConstraint("product_id", "ingredient_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    quantity_mg = Column(Float)

    product = relationship("Product", back_populates="product_ingredients")
    ingredient = relationship("Ingredient", back_populates="product_ingredients")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(String, nullable=False, server_default=text("(datetime('now'))"))

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")


class SupportArticle(Base):
    __tablename__ = "support_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default=text("(datetime('now'))"))


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    discount_pct = Column(Float, nullable=False)
    description = Column(Text)
    active = Column(Integer, nullable=False, default=1)
    starts_at = Column(String)
    expires_at = Column(String)

    product = relationship("Product", back_populates="promotions")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    retrieved_context = Column(Text)
    answer = Column(Text, nullable=False)
    created_at = Column(String, nullable=False, server_default=text("(datetime('now'))"))

    user = relationship("User", back_populates="chat_sessions")
