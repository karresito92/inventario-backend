from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ProductBase(BaseModel):
    nombre: str
    marca: Optional[str] = None
    precio: Decimal
    stock: int = 0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id_producto: int
    id_usuario: int

    class Config:
        from_attributes = True
