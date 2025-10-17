"""
User models - User and UserProfile tables
"""

from typing import List, Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('username', name='users_username_key')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    email = mapped_column(CITEXT, nullable=False)
    username = mapped_column(String(50), nullable=False)
    password_hash = mapped_column(String(255), nullable=False)
    first_name = mapped_column(String(100))
    last_name = mapped_column(String(100))
    phone = mapped_column(String(20))
    status = mapped_column(String(50), server_default=text("'active'"))
    role = mapped_column(String(50), server_default=text("'user'"))
    email_verified = mapped_column(Boolean, server_default=text('false'))
    phone_verified = mapped_column(Boolean, server_default=text('false'))
    two_factor_enabled = mapped_column(Boolean, server_default=text('false'))
    last_login = mapped_column(DateTime(True))
    failed_login_attempts = mapped_column(Integer, server_default=text('0'))
    locked_until = mapped_column(DateTime(True))
    is_active = mapped_column(Boolean, server_default=text('true'))
    created_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    user_profiles: Mapped[List['UserProfile']] = relationship('UserProfile', back_populates='user')
    
    market_products: Mapped[List['MarketProduct']] = relationship(
        'MarketProduct', 
        back_populates='owner_user',
        foreign_keys='MarketProduct.owner_user_id'
    )
    market_orders_as_buyer: Mapped[List['MarketOrder']] = relationship(
        'MarketOrder',
        foreign_keys='MarketOrder.buyer_user_id',
        back_populates='buyer_user'
    )
    market_orders_as_seller: Mapped[List['MarketOrder']] = relationship(
        'MarketOrder',
        foreign_keys='MarketOrder.seller_user_id',
        back_populates='seller_user'
    )
    notifications: Mapped[List['Notification']] = relationship(
        'Notification',
        back_populates='user'
    )

    @property
    def full_name(self) -> str:
        """Returns user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_profiles_pkey')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id = mapped_column(Uuid, nullable=False)
    avatar_url = mapped_column(String(500))
    birth_date = mapped_column(DateTime)
    address = mapped_column(String)
    city = mapped_column(String(100))
    postal_code = mapped_column(String(20))
    country = mapped_column(String(3))
    language = mapped_column(String(5), server_default=text("'es'"))
    timezone = mapped_column(String(50), server_default=text("'Europe/Madrid'"))
    preferences = mapped_column(JSONB, server_default=text("'{}'"))
    created_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='user_profiles')

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"