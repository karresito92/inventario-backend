"""
Order schemas - Pydantic models for marketplace orders
"""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class BaseSchema(BaseModel):
    """Base schema with common config"""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class TimestampSchema(BaseSchema):
    """Common timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderBase(BaseSchema):
    buyer_user_id: UUID
    seller_user_id: UUID
    subtotal: Decimal = Field(..., ge=0)
    taxes: Decimal = Field(default=0, ge=0, alias="tax_amount")
    shipping_cost: Decimal = Field(default=0, ge=0, alias="shipping_amount")
    discounts: Decimal = Field(default=0, ge=0, alias="discount_amount")
    total: Decimal = Field(..., ge=0, alias="total_amount")
    currency: str = Field(default="EUR", max_length=3)
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    order_number: str
    status: Optional[OrderStatus] = OrderStatus.PENDING
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


class OrderUpdate(BaseSchema):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    tracking_number: Optional[str] = None


class OrderResponse(TimestampSchema):
    id: UUID
    order_number: str
    buyer_user_id: UUID
    seller_user_id: UUID
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    status: OrderStatus
    shipping_address: Optional[Dict[str, Any]]
    billing_address: Optional[Dict[str, Any]]
    notes: Optional[str]
    tracking_number: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    updated_by: Optional[UUID] = None


class OrderSearchParams(BaseSchema):
    order_number: Optional[str] = None
    buyer_user_id: Optional[UUID] = None
    seller_user_id: Optional[UUID] = None
    status: Optional[OrderStatus] = None
    min_total: Optional[Decimal] = None
    max_total: Optional[Decimal] = None
    currency: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = 0
    limit: int = 100