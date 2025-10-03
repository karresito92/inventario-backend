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
    products = db.query(Product).filter(
        Product.vendido == False
    ).order_by(Product.created_at.desc()).all()
    return products

@router.post("/publish", response_model=ProductSchema)
def publish_product(
    product: ProductCreate, 
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    db_product = Product(
        nombre=product.nombre,
        marca=product.marca,
        descripcion=product.descripcion,
        precio=product.precio,
        estado=product.estado,
        imagen_url=product.imagen_url,
        vendido=False,
        id_usuario=current_user.id_usuario
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

@router.get("/my-products", response_model=List[ProductSchema])
def get_my_products(token: str, db: Session = Depends(get_db)):
    current_user = get_current_user(token, db)
    
    products = db.query(Product).filter(
        Product.id_usuario == current_user.id_usuario
    ).order_by(Product.created_at.desc()).all()
    
    return products

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_update: ProductCreate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    db_product = db.query(Product).filter(
        Product.id_producto == product_id
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    if db_product.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este producto"
        )
    
    if db_product.vendido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes editar un producto ya vendido"
        )
    
    db_product.nombre = product_update.nombre
    db_product.marca = product_update.marca
    db_product.descripcion = product_update.descripcion
    db_product.precio = product_update.precio
    db_product.estado = product_update.estado
    db_product.imagen_url = product_update.imagen_url
    
    db.commit()
    db.refresh(db_product)
    
    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    db_product = db.query(Product).filter(
        Product.id_producto == product_id
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    if db_product.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este producto"
        )
    
    if db_product.vendido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar un producto ya vendido"
        )
    
    db.delete(db_product)
    db.commit()
    
    return {"message": "Producto eliminado correctamente", "id_producto": product_id}