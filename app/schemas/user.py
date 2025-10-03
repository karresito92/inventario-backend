from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserBase(BaseModel):
    nombre: str
    email: EmailStr
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v or v.strip() == '':
            raise ValueError('El nombre no puede estar vacío')
        if len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        if len(v.strip()) > 100:
            raise ValueError('El nombre es demasiado largo (máximo 100 caracteres)')
        return v.strip()

class UserCreate(UserBase):
    contrasenia: str
    
    @validator('contrasenia')
    def contrasenia_valida(cls, v):
        if not v or v.strip() == '':
            raise ValueError('La contraseña no puede estar vacía')
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    contrasenia: str

class User(UserBase):
    id_usuario: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
