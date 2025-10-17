"""
Product schemas - Pydantic models for marketplace products
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ProductStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BaseSchema(BaseModel):
    """Base schema with common config"""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ProductBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    base_price: Decimal = Field(..., ge=0)
    owner_user_id: UUID
    is_digital: bool = False
    is_physical: bool = True
    track_inventory: bool = True
    inventory_quantity: int = 0

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v):
        if not v.strip():
            raise ValueError("SKU cannot be empty")
        return v.strip().upper()


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_digital: Optional[bool] = None
    is_physical: Optional[bool] = None
    track_inventory: Optional[bool] = None
    inventory_quantity: Optional[int] = None


class ProductResponse(BaseSchema):
    id: UUID
    title: str
    description: Optional[str]
    sku: Optional[str]
    base_price: Decimal
    owner_user_id: UUID
    status: ProductStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Extra fields
    kind: Optional[str] = None
    condition: Optional[str] = None
    barcode: Optional[str] = None
    media: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="product_metadata")


class ProductListResponse(BaseSchema):
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class ProductSearchParams(BaseSchema):
    q: Optional[str] = None
    status: Optional[ProductStatus] = None
    seller_user_id: Optional[UUID] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_digital: Optional[bool] = None
    is_physical: Optional[bool] = None
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = 1
    per_page: int = 20