"""
User schemas - Pydantic models for user-related operations
"""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending_verification"
    SUSPENDED = "suspended"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


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


class UserBase(BaseSchema):
    email: EmailStr = Field(..., description="Email del usuario")
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError("Username must contain only alphanumeric characters")
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not v.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone must contain only digits, spaces, + and -")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = Field(UserRole.USER)
    terms_accepted: bool = True
    privacy_policy_accepted: bool = True

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v, info):
        if info.data and "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    metadata: Optional[Dict[str, Any]] = None


class UserPasswordUpdate(BaseSchema):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v, info):
        if info.data and "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(AuditSchema):
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class UserLogin(BaseSchema):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserToken(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserSearchParams(BaseSchema):
    search: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    email_verified: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = 0
    limit: int = 100