from pydantic import BaseModel, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    nombre: str
    marca: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Decimal
    estado: str
    imagen_url: Optional[str] = None
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v or v.strip() == '':
            raise ValueError('El nombre del producto no puede estar vacío')
        return v.strip()
    
    @validator('precio')
    def precio_valido(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return round(v, 2)
    
    @validator('estado')
    def estado_valido(cls, v):
        estados_permitidos = ['nuevo', 'como nuevo', 'usado', 'para reparar']
        if v.lower() not in estados_permitidos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_permitidos)}')
        return v.lower()

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id_producto: int
    id_usuario: int
    vendido: bool
    created_at: datetime

    class Config:
        from_attributes = True
