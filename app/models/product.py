from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Product(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    marca = Column(String(100))
    descripcion = Column(Text)
    precio = Column(DECIMAL(10, 2), nullable=False)
    estado = Column(String(50))  # "nuevo", "como nuevo", "usado", "para reparar"
    vendido = Column(Boolean, default=False, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"))
    imagen_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("User")
