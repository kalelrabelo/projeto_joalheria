from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class ClienteCreate(BaseModel):
    nome_completo: str
    cpf_cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    observacoes: Optional[str] = None
    status: Optional[str] = 'ativo'

    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v):
        if v is not None:
            # Remover caracteres especiais
            doc = ''.join(filter(str.isdigit, v))
            if len(doc) not in [11, 14]:
                raise ValueError('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos')
        return v

class ClienteUpdate(BaseModel):
    nome_completo: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None

    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v):
        if v is not None:
            doc = ''.join(filter(str.isdigit, v))
            if len(doc) not in [11, 14]:
                raise ValueError('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos')
        return v

class ClienteResponse(BaseModel):
    id: int
    nome_completo: str
    cpf_cnpj: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    endereco: Optional[str]
    data_nascimento: Optional[datetime]
    observacoes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

