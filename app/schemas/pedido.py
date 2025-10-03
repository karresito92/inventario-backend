from pydantic import BaseModel, validator
from decimal import Decimal
from typing import List

class DetallePedidoCreate(BaseModel):
    id_producto: int
    cantidad: int
    
    @validator('id_producto')
    def id_producto_valido(cls, v):
        if v <= 0:
            raise ValueError('El ID del producto debe ser mayor a 0')
        return v
    
    @validator('cantidad')
    def cantidad_valida(cls, v):
        if v <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        if v > 1000:
            raise ValueError('La cantidad es demasiado alta (máximo 1000 unidades por producto)')
        return v

class DetallePedidoResponse(BaseModel):
    id_detalle: int
    id_producto: int
    cantidad: int
    precio_total: Decimal
    
    class Config:
        from_attributes = True

class PedidoCreate(BaseModel):
    productos: List[DetallePedidoCreate]
    
    @validator('productos')
    def productos_validos(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Debe incluir al menos un producto en el pedido')
        if len(v) > 50:
            raise ValueError('No puedes comprar más de 50 productos diferentes en un solo pedido')
        
        ids_productos = [item.id_producto for item in v]
        if len(ids_productos) != len(set(ids_productos)):
            raise ValueError('No puedes incluir el mismo producto dos veces. Suma las cantidades.')
        
        return v

class PedidoResponse(BaseModel):
    id_pedido: int
    id_usuario: int
    completo: bool
    detalles: List[DetallePedidoResponse]
    
    class Config:
        from_attributes = True