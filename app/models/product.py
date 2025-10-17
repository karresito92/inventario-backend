"""
Product models - MarketProduct and MarketCategory tables
"""

from typing import List, Optional
from sqlalchemy import (
    ARRAY, Boolean, Column, String, Integer, DateTime, Numeric,
    ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint, 
    Uuid, Text, text, Table
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


# Association table for many-to-many relationship
market_product_categories = Table(
    'market_product_categories',
    Base.metadata,
    Column('product_id', Uuid, primary_key=True),
    Column('category_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['product_id'], ['market_products.id'], ondelete='CASCADE'),
    ForeignKeyConstraint(['category_id'], ['market_categories.id'], ondelete='CASCADE')
)


class MarketCategory(Base):
    __tablename__ = 'market_categories'
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['market_categories.id'], ondelete='SET NULL', name='market_categories_parent_id_fkey'),
        PrimaryKeyConstraint('id', name='market_categories_pkey'),
        UniqueConstraint('name', name='market_categories_name_key'),
        UniqueConstraint('slug', name='market_categories_slug_key')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    name = mapped_column(String(120), nullable=False)
    slug = mapped_column(String(140), nullable=False)
    parent_id = mapped_column(Uuid)
    is_active = mapped_column(Boolean, server_default=text('true'))
    created_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    # Self-referential relationships
    parent: Mapped[Optional['MarketCategory']] = relationship(
        'MarketCategory',
        remote_side=[id],
        back_populates='children'
    )
    children: Mapped[List['MarketCategory']] = relationship(
        'MarketCategory',
        back_populates='parent'
    )

    # Many-to-many with products
    products: Mapped[List['MarketProduct']] = relationship(
        'MarketProduct',
        secondary=market_product_categories,
        back_populates='categories'
    )

    def __repr__(self):
        return f"<MarketCategory(id={self.id}, name='{self.name}')>"


class MarketProduct(Base):
    __tablename__ = 'market_products'
    __table_args__ = (
        ForeignKeyConstraint(['owner_user_id'], ['users.id'], ondelete='CASCADE', name='market_products_owner_user_id_fkey'),
        PrimaryKeyConstraint('id', name='market_products_pkey')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    owner_user_id = mapped_column(Uuid, nullable=False)
    dare_id = mapped_column(Integer)
    title = mapped_column(String(200), nullable=False)
    description = mapped_column(Text)
    kind = mapped_column(String(50), server_default=text("'physical'"))
    condition = mapped_column(String(50))
    sku = mapped_column(String(100))
    barcode = mapped_column(String(100))
    media = mapped_column(JSONB, server_default=text("'[]'"))
    attributes = mapped_column(JSONB, server_default=text("'{}'"))
    tags = mapped_column(ARRAY(Text))
    is_active = mapped_column(Boolean, server_default=text('true'))
    product_metadata = mapped_column('metadata', JSONB, server_default=text("'{}'"))
    created_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    owner_user: Mapped['User'] = relationship('User', back_populates='market_products')
    
    # Many-to-many with categories
    categories: Mapped[List['MarketCategory']] = relationship(
        'MarketCategory',
        secondary=market_product_categories,
        back_populates='products'
    )

    def __repr__(self):
        return f"<MarketProduct(id={self.id}, title='{self.title}', owner={self.owner_user_id})>"