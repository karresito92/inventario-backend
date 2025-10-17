"""
Notifications Router - Endpoints for notification system
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, get_current_active_user, get_current_admin_user
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
)
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: NotificationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a notification for a user.
    """
    user = db.query(User).filter(User.id == notification_data.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    if notification_data.user_id != current_user.id:
        # In future: allow if admin
        raise HTTPException(403, "Not enough permissions")
    
    notif = Notification(
        user_id=notification_data.user_id,
        title=notification_data.title,
        message=notification_data.message,
        type=notification_data.notification_type or "info",
        priority=notification_data.priority or 1,
        data=notification_data.data or {},
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns a specific notification.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    
    if notif.user_id != current_user.id:
        # In future: allow if admin
        raise HTTPException(403, "Not enough permissions")
    return notif


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: uuid.UUID,
    notification_update: NotificationUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Allows modifying an existing notification.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    
    if notif.user_id != current_user.id:
        raise HTTPException(403, "Not enough permissions")
    
    for k, v in notification_update.model_dump(exclude_unset=True).items():
        if hasattr(notif, k):
            setattr(notif, k, v)
    db.commit()
    db.refresh(notif)
    return notif


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Permanently deletes a notification.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    
    if notif.user_id != current_user.id:
        raise HTTPException(403, "Not enough permissions")
    
    db.delete(notif)
    db.commit()
    return


@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    user_id: Optional[uuid.UUID] = None,
    notification_type: Optional[str] = None,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns all notifications in the system (admin only).
    """
    q = db.query(Notification)
    
    if user_id:
        q = q.filter(Notification.user_id == user_id)
    if notification_type:
        q = q.filter(Notification.type == notification_type)
    if unread_only:
        q = q.filter(Notification.read_at.is_(None))
    
    return q.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/me/list", response_model=List[NotificationResponse])
def get_my_notifications(
    unread_only: bool = Query(False),
    notification_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns the current user's notifications.
    """
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        q = q.filter(Notification.read_at.is_(None))
    if notification_type:
        q = q.filter(Notification.type == notification_type)
    
    return q.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marks a notification as read.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    
    if notif.user_id != current_user.id:
        raise HTTPException(403, "Not enough permissions")
    
    notif.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notif)
    return notif


@router.post("/me/mark-all-read", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_my_notifications_as_read(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marks all current user's notifications as read.
    """
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read_at.is_(None)
    ).all()
    
    now = datetime.now(timezone.utc)
    for n in notifs:
        n.read_at = now
    db.commit()
    return


@router.get("/me/unread-count")
def get_my_unread_count(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns the number of unread notifications for the current user.
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read_at.is_(None)
    ).count()
    return {"unread_count": count}


@router.get("/stats/summary")
def get_notification_stats_summary(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns global notification statistics (admin only).
    """
    total = db.query(Notification).count()
    type_stats = {k: v for k, v in db.query(
        Notification.type, func.count(Notification.id)
    ).group_by(Notification.type).all()}
    priority_stats = {k: v for k, v in db.query(
        Notification.priority, func.count(Notification.id)
    ).group_by(Notification.priority).all()}
    
    return {
        "total_notifications": total,
        "type_distribution": type_stats,
        "priority_distribution": priority_stats,
    }