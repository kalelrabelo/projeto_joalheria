from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ValeCreate(BaseModel):
    funcionario_id: int
    valor: float
    motivo: Optional[str] = None
    data_vale: Optional[datetime] = None
    status: Optional[str] = 'ativo'
    observacoes: Optional[str] = None

    @validator('valor')
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor do vale deve ser maior que zero')
        return v

class ValeUpdate(BaseModel):
    funcionario_id: Optional[int] = None
    valor: Optional[float] = None
    motivo: Optional[str] = None
    data_vale: Optional[datetime] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

    @validator('valor')
    def validate_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor do vale deve ser maior que zero')
        return v

class ValeResponse(BaseModel):
    id: int
    funcionario_id: int
    valor: float
    motivo: Optional[str]
    data_vale: datetime
    status: str
    observacoes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

