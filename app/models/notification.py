"""
Notification models - Notifications table
"""

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, CheckConstraint,
    ForeignKeyConstraint, PrimaryKeyConstraint, Uuid, Text, text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        CheckConstraint('priority >= 1 AND priority <= 4', name='notifications_priority_check'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='notifications_user_id_fkey'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id = mapped_column(Uuid, nullable=False)
    type = mapped_column(String(50), server_default=text("'info'"))
    title = mapped_column(String(200), nullable=False)
    message = mapped_column(Text, nullable=False)
    data = mapped_column(JSONB, server_default=text("'{}'"))
    is_read = mapped_column(Boolean, server_default=text('false'))
    read_at = mapped_column(DateTime(True))
    priority = mapped_column(Integer, server_default=text('1'))
    created_at = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='notifications')

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title='{self.title}', read={self.is_read})>"

    def mark_as_read(self):
        """Helper method to mark notification as read"""
        from datetime import datetime, timezone
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)