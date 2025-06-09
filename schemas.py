# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str

class UsuarioOut(BaseModel):
    id: int
    email: EmailStr

class DocumentoOut(BaseModel):
    id: int
    nombre: str
    ruta: str
    fecha_creacion: datetime

    class Config:
        orm_mode = True

 
