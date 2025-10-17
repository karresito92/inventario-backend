"""
Notification schemas - Pydantic models for notification system
"""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class BaseSchema(BaseModel):
    """Base schema with common config"""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class TimestampSchema(BaseSchema):
    """Common timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuditSchema(TimestampSchema):
    """Audit fields"""
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None


class NotificationBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: str = "info"
    priority: int = Field(default=1, ge=1, le=4)
    is_read: bool = False
    data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class NotificationCreate(NotificationBase):
    user_id: UUID
    channel: str = "in_app"
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None


class NotificationUpdate(BaseSchema):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase, AuditSchema):
    id: UUID
    user_id: UUID
    type: str
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class NotificationSearchParams(BaseSchema):
    user_id: Optional[UUID] = None
    notification_type: Optional[str] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    unread_only: bool = False
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = 0
    limit: int = 100