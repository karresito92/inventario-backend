from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido", ondelete="CASCADE"))
    id_producto = Column(Integer, ForeignKey("producto.id_producto", ondelete="CASCADE"))
    cantidad = Column(Integer, nullable=False)
    precio_total = Column(DECIMAL(10, 2), nullable=False)

    pedido = relationship("Pedido")
    producto = relationship("Product")
