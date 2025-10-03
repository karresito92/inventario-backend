from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.database.connection import get_db
from app.models.pedido import Pedido, DetallePedido
from app.models.product import Product
from app.models.user import User
from app.schemas.pedido import PedidoResponse
from app.utils.auth import verify_token

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_current_user(token: str, db: Session):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/buy/{product_id}", response_model=PedidoResponse)
def buy_product(
    product_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    producto = db.query(Product).filter(
        Product.id_producto == product_id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    if producto.vendido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este producto ya ha sido vendido"
        )
    
    if producto.id_usuario == current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes comprar tu propio producto"
        )
    
    nuevo_pedido = Pedido(
        id_usuario=current_user.id_usuario,
        completo=True
    )
    db.add(nuevo_pedido)
    db.flush()
    

    detalle = DetallePedido(
        id_pedido=nuevo_pedido.id_pedido,
        id_producto=product_id,
        cantidad=1,  
        precio_total=producto.precio
    )
    db.add(detalle)
    

    producto.vendido = True
    
    db.commit()
    db.refresh(nuevo_pedido)
    
    return nuevo_pedido

@router.get("/my-purchases", response_model=List[PedidoResponse])
def get_my_purchases(token: str, db: Session = Depends(get_db)):
    current_user = get_current_user(token, db)
    
    pedidos = db.query(Pedido).filter(
        Pedido.id_usuario == current_user.id_usuario
    ).all()
    
    return pedidos

@router.get("/{order_id}", response_model=PedidoResponse)
def get_order(
    order_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == order_id
    ).first()
    
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    if pedido.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este pedido"
        )
    
    return pedido