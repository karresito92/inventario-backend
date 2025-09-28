from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    nombre: str
    email: EmailStr

class UserCreate(UserBase):
    contrasenia: str

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
