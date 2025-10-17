"""
Orders Router - Endpoints for marketplace orders
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
)
from app.models.order import MarketOrder as Order
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new order (purchase order).
    """
    buyer = db.query(User).filter(User.id == order_data.buyer_user_id).first()
    if not buyer:
        raise HTTPException(404, "Buyer user not found")
    seller = db.query(User).filter(User.id == order_data.seller_user_id).first()
    if not seller:
        raise HTTPException(404, "Seller user not found")
    
    if order_data.buyer_user_id != current_user.id:
        # In future: allow if admin
        raise HTTPException(403, "Not enough permissions")
    
    db_order = Order(
        buyer_user_id=order_data.buyer_user_id,
        seller_user_id=order_data.seller_user_id,
        subtotal=order_data.subtotal,
        taxes=order_data.taxes,
        shipping_cost=order_data.shipping_cost,
        discounts=order_data.discounts,
        total=order_data.total,
        currency=order_data.currency,
        status=order_data.status if hasattr(order_data, 'status') else "pending",
        buyer_notes=order_data.notes if hasattr(order_data, 'notes') else None,
        shipping_address=order_data.shipping_address,
        billing_address=order_data.billing_address,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns the details of a specific order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    if (order.buyer_user_id != current_user.id and 
        order.seller_user_id != current_user.id):
        # In future: allow if admin
        raise HTTPException(403, "Not enough permissions")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: uuid.UUID,
    order_update: OrderUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Updates order information (status, notes, tracking).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    if (order.buyer_user_id != current_user.id and 
        order.seller_user_id != current_user.id):
        raise HTTPException(403, "Not enough permissions")
    
    for k, v in order_update.model_dump(exclude_unset=True).items():
        if hasattr(order, k):
            setattr(order, k, v)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancels an order (soft delete).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    if (order.buyer_user_id != current_user.id and 
        order.seller_user_id != current_user.id):
        raise HTTPException(403, "Not enough permissions")
    
    order.status = "cancelled"
    db.commit()
    return


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    buyer_user_id: Optional[uuid.UUID] = None,
    seller_user_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    General list of orders (admin only).
    """
    q = db.query(Order)
    
    if buyer_user_id:
        q = q.filter(Order.buyer_user_id == buyer_user_id)
    if seller_user_id:
        q = q.filter(Order.seller_user_id == seller_user_id)
    if status_filter:
        q = q.filter(Order.status == status_filter)
    
    return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/me/orders", response_model=List[OrderResponse])
def get_my_orders(
    status_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns orders where the current user is the buyer.
    """
    q = db.query(Order).filter(Order.buyer_user_id == current_user.id)
    
    if status_filter:
        q = q.filter(Order.status == status_filter)
    
    return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/me/sales", response_model=List[OrderResponse])
def get_my_sales(
    status_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns orders where the current user is the seller.
    """
    q = db.query(Order).filter(Order.seller_user_id == current_user.id)
    
    if status_filter:
        q = q.filter(Order.status == status_filter)
    
    return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stats/summary")
def get_orders_stats_summary(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Shows general order system statistics (admin only).
    """
    total_orders = db.query(Order).count()
    status_stats = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    currency_stats = db.query(Order.currency, func.count(Order.id)).group_by(Order.currency).all()
    total_amount = db.query(func.sum(Order.total)).scalar() or 0
    average_amount = db.query(func.avg(Order.total)).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "total_amount": float(total_amount),
        "average_amount": float(average_amount),
        "status_distribution": {k: v for k, v in status_stats},
        "currency_distribution": {k: v for k, v in currency_stats},
    }


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: uuid.UUID,
    reason: Optional[str] = Query(None),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Allows cancelling an existing order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    if (order.buyer_user_id != current_user.id and 
        order.seller_user_id != current_user.id):
        raise HTTPException(403, "Not enough permissions")
    
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(400, "Order cannot be cancelled in current status")
    
    order.status = "cancelled"
    if reason and order.buyer_notes:
        order.buyer_notes = (order.buyer_notes or "") + f"\nCancelled: {reason}"
    db.commit()
    db.refresh(order)
    return order