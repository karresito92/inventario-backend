"""
Order models - MarketOrder and MarketOrderItem tables
"""

from typing import List, Optional
from sqlalchemy import (
    Column, String, Integer, DateTime, Numeric, CheckConstraint,
    ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint,
    Uuid, Text, text, CHAR
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class MarketOrder(Base):
    __tablename__ = 'market_orders'
    __table_args__ = (
        CheckConstraint('discounts >= (0)::numeric', name='market_orders_discounts_check'),
        CheckConstraint('shipping_cost >= (0)::numeric', name='market_orders_shipping_cost_check'),
        CheckConstraint('subtotal >= (0)::numeric', name='market_orders_subtotal_check'),
        CheckConstraint('taxes >= (0)::numeric', name='market_orders_taxes_check'),
        CheckConstraint('total >= (0)::numeric', name='market_orders_total_check'),
        ForeignKeyConstraint(['buyer_user_id'], ['users.id'], ondelete='CASCADE', name='market_orders_buyer_user_id_fkey'),
        ForeignKeyConstraint(['seller_user_id'], ['users.id'], ondelete='CASCADE', name='market_orders_seller_user_id_fkey'),
        PrimaryKeyConstraint('id', name='market_orders_pkey'),
        UniqueConstraint('order_number', name='market_orders_order_number_key')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    buyer_user_id = mapped_column(Uuid, nullable=False)
    seller_user_id = mapped_column(Uuid, nullable=False)
    subtotal = mapped_column(Numeric(14, 2), nullable=False)
    taxes = mapped_column(Numeric(14, 2), server_default=text('0'))
    shipping_cost = mapped_column(Numeric(14, 2), server_default=text('0'))
    discounts = mapped_column(Numeric(14, 2), server_default=text('0'))
    total = mapped_column(Numeric(14, 2), nullable=False)
    currency = mapped_column(CHAR(3), nullable=False, server_default=text("'EUR'"))
    status = mapped_column(String(50), server_default=text("'pending'"))
    order_number = mapped_column(String(50), unique=True)
    tracking_number = mapped_column(String(100))
    shipped_at = mapped_column(DateTime(True))
    delivered_at = mapped_column(DateTime(True))
    buyer_notes = mapped_column(Text)
    seller_notes = mapped_column(Text)
    shipping_address = mapped_column(JSONB)
    billing_address = mapped_column(JSONB)
    order_metadata = mapped_column('metadata', JSONB, server_default=text("'{}'"))
    created_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    buyer_user: Mapped['User'] = relationship(
        'User',
        foreign_keys=[buyer_user_id],
        back_populates='market_orders_as_buyer'
    )
    seller_user: Mapped['User'] = relationship(
        'User',
        foreign_keys=[seller_user_id],
        back_populates='market_orders_as_seller'
    )
    order_items: Mapped[List['MarketOrderItem']] = relationship(
        'MarketOrderItem',
        back_populates='order'
    )

    def __repr__(self):
        return f"<MarketOrder(id={self.id}, status='{self.status}', total={self.total} {self.currency})>"

class MarketOrderItem(Base):
    __tablename__ = 'market_order_items'
    __table_args__ = (
        CheckConstraint('quantity > 0', name='market_order_items_quantity_check'),
        CheckConstraint('unit_price >= (0)::numeric', name='market_order_items_unit_price_check'),
        ForeignKeyConstraint(['listing_id'], ['market_listings.id'], ondelete='SET NULL', name='market_order_items_listing_id_fkey'),
        ForeignKeyConstraint(['order_id'], ['market_orders.id'], ondelete='CASCADE', name='market_order_items_order_id_fkey'),
        ForeignKeyConstraint(['product_id'], ['market_products.id'], ondelete='SET NULL', name='market_order_items_product_id_fkey'),
        PrimaryKeyConstraint('id', name='market_order_items_pkey')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    order_id = mapped_column(Uuid, nullable=False)
    listing_id = mapped_column(Uuid)
    product_id = mapped_column(Uuid)
    title = mapped_column(String(200), nullable=False)
    quantity = mapped_column(Integer, nullable=False)
    unit_price = mapped_column(Numeric(12, 2), nullable=False)
    currency = mapped_column(CHAR(3), nullable=False, server_default=text("'EUR'"))
    item_metadata = mapped_column('metadata', JSONB, server_default=text("'{}'"))

    # Relationships
    order: Mapped['MarketOrder'] = relationship('MarketOrder', back_populates='order_items')

    def __repr__(self):
        return f"<MarketOrderItem(id={self.id}, title='{self.title}', qty={self.quantity})>"