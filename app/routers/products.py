"""
Products Router - Endpoints for marketplace products
"""

import uuid
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_active_user
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from app.models.product import MarketProduct as Product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Creates a new product associated with the authenticated user.
    """
    if product_data.owner_user_id != current_user.id:
        raise HTTPException(403, "Cannot create products for other users")
    
    if product_data.sku:
        if db.query(Product).filter(Product.sku == product_data.sku).first():
            raise HTTPException(400, "Product with this SKU already exists")
    
    db_product = Product(
        title=product_data.title,
        description=product_data.description,
        sku=product_data.sku,
        owner_user_id=product_data.owner_user_id,
        kind=product_data.kind if hasattr(product_data, 'kind') else 'physical',
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Returns a product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Check permissions (owner or active product)
    if product.owner_user_id != current_user.id:
        if not product.is_active:
            raise HTTPException(403, "Not authorized to view this product")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Modifies an existing product.
    - Only the owner can update it.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized to update this product")
    
    data = product_data.model_dump(exclude_unset=True)
    for k, v in data.items():
        if hasattr(product, k):
            setattr(product, k, v)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Permanently deletes a product.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized to delete this product")
    db.delete(product)
    db.commit()
    return


@router.get("/me/products", response_model=List[ProductResponse])
def get_my_products(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Returns all products created by the authenticated user.
    """
    return db.query(Product).filter(
        Product.owner_user_id == current_user.id
    ).offset(skip).limit(limit).all()


@router.get("/", response_model=List[ProductResponse])
def list_products(
    search: Optional[str] = Query(None, alias="q"),
    seller_user_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 20,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns a general list of products with filters.
    """
    q = db.query(Product)
    
    if search:
        like = f"%{search}%"
        q = q.filter(
            (Product.title.ilike(like)) |
            (Product.description.ilike(like))
        )
    
    if seller_user_id:
        q = q.filter(Product.owner_user_id == seller_user_id)
    
    return q.offset(skip).limit(limit).all()


@router.get("/public/raw", response_model=List[ProductResponse])
def get_public_products_raw(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Returns publicly visible products (is_active=True).
    - Does not require authentication.
    """
    products = db.query(Product).filter(
        Product.is_active.is_(True)
    ).offset(skip).limit(limit).all()
    return products