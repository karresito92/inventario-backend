from sqlalchemy import Column, Integer, Boolean, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"))
    completo = Column(Boolean, default=False)

    usuario = relationship("User")
    detalles = relationship("DetallePedido", back_populates="pedido")

class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido", ondelete="CASCADE"))
    id_producto = Column(Integer, ForeignKey("producto.id_producto", ondelete="CASCADE"))
    cantidad = Column(Integer, nullable=False)
    precio_total = Column(DECIMAL(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Product")