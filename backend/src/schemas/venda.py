from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class VendaCreate(BaseModel):
    cliente_id: Optional[int] = None
    joia_id: int
    funcionario_id: int
    quantidade: Optional[int] = 1
    preco_unitario: float
    desconto: Optional[float] = 0.0
    valor_total: float
    forma_pagamento: Optional[str] = None
    data_venda: Optional[datetime] = None
    status: Optional[str] = 'concluida'
    observacoes: Optional[str] = None

    @validator('quantidade')
    def validate_quantidade(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        return v

    @validator('preco_unitario', 'valor_total')
    def validate_preco(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v

    @validator('desconto')
    def validate_desconto(cls, v):
        if v < 0:
            raise ValueError('Desconto não pode ser negativo')
        return v

class VendaUpdate(BaseModel):
    cliente_id: Optional[int] = None
    joia_id: Optional[int] = None
    funcionario_id: Optional[int] = None
    quantidade: Optional[int] = None
    preco_unitario: Optional[float] = None
    desconto: Optional[float] = None
    valor_total: Optional[float] = None
    forma_pagamento: Optional[str] = None
    data_venda: Optional[datetime] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

    @validator('quantidade')
    def validate_quantidade(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        return v

    @validator('preco_unitario', 'valor_total')
    def validate_preco(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v

    @validator('desconto')
    def validate_desconto(cls, v):
        if v is not None and v < 0:
            raise ValueError('Desconto não pode ser negativo')
        return v

class VendaResponse(BaseModel):
    id: int
    cliente_id: Optional[int]
    joia_id: int
    funcionario_id: int
    quantidade: int
    preco_unitario: float
    desconto: float
    valor_total: float
    forma_pagamento: Optional[str]
    data_venda: datetime
    status: str
    observacoes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

