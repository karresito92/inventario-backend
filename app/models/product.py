from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Product(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    marca = Column(String(100))
    precio = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"))

    usuario = relationship("User")