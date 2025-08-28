from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class JoiaCreate(BaseModel):
    nome: str
    categoria: str
    material: Optional[str] = None
    peso: Optional[float] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    quantidade_estoque: Optional[int] = 0
    estoque_minimo: Optional[int] = 1
    descricao: Optional[str] = None
    foto_url: Optional[str] = None
    codigo_barras: Optional[str] = None
    status: Optional[str] = 'ativo'

    @validator('peso')
    def validate_peso(cls, v):
        if v is not None and v < 0:
            raise ValueError('Peso não pode ser negativo')
        return v

    @validator('preco_custo', 'preco_venda')
    def validate_preco(cls, v):
        if v is not None and v < 0:
            raise ValueError('Preço não pode ser negativo')
        return v

    @validator('quantidade_estoque', 'estoque_minimo')
    def validate_estoque(cls, v):
        if v is not None and v < 0:
            raise ValueError('Quantidade de estoque não pode ser negativa')
        return v

class JoiaUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    material: Optional[str] = None
    peso: Optional[float] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    quantidade_estoque: Optional[int] = None
    estoque_minimo: Optional[int] = None
    descricao: Optional[str] = None
    foto_url: Optional[str] = None
    codigo_barras: Optional[str] = None
    status: Optional[str] = None

    @validator('peso')
    def validate_peso(cls, v):
        if v is not None and v < 0:
            raise ValueError('Peso não pode ser negativo')
        return v

    @validator('preco_custo', 'preco_venda')
    def validate_preco(cls, v):
        if v is not None and v < 0:
            raise ValueError('Preço não pode ser negativo')
        return v

    @validator('quantidade_estoque', 'estoque_minimo')
    def validate_estoque(cls, v):
        if v is not None and v < 0:
            raise ValueError('Quantidade de estoque não pode ser negativa')
        return v

class JoiaResponse(BaseModel):
    id: int
    nome: str
    categoria: str
    material: Optional[str]
    peso: Optional[float]
    preco_custo: Optional[float]
    preco_venda: Optional[float]
    quantidade_estoque: int
    estoque_minimo: int
    descricao: Optional[str]
    foto_url: Optional[str]
    codigo_barras: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

