from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, Product as ProductSchema
from app.utils.auth import verify_token

router = APIRouter(prefix="/products", tags=["Products"])

def get_current_user(token: str, db: Session):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.get("/catalog", response_model=List[ProductSchema])
def get_catalog(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.stock > 0).all()
    return products

@router.post("/sell", response_model=ProductSchema)
def create_product(
    product: ProductCreate, 
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    db_product = Product(
        nombre=product.nombre,
        marca=product.marca,
        precio=product.precio,
        stock=product.stock,
        id_usuario=current_user.id_usuario
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

@router.get("/inventory", response_model=List[ProductSchema])
def get_user_inventory(token: str, db: Session = Depends(get_db)):
    current_user = get_current_user(token, db)
    
    products = db.query(Product).filter(
        Product.id_usuario == current_user.id_usuario
    ).all()
    
    return products