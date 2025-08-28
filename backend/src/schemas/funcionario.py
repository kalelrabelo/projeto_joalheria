from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class FuncionarioCreate(BaseModel):
    nome_completo: str
    nome_usuario: str
    senha: str
    cpf: str
    rg: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    cargo: Optional[str] = None
    salario: Optional[float] = 0.0
    data_admissao: Optional[datetime] = None
    status: Optional[str] = 'ativo'
    foto_url: Optional[str] = None

    @validator('cpf')
    def validate_cpf(cls, v):
        # Remover caracteres especiais
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v

    @validator('salario')
    def validate_salario(cls, v):
        if v < 0:
            raise ValueError('Salário não pode ser negativo')
        return v

class FuncionarioUpdate(BaseModel):
    nome_completo: Optional[str] = None
    nome_usuario: Optional[str] = None
    senha: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    cargo: Optional[str] = None
    salario: Optional[float] = None
    data_admissao: Optional[datetime] = None
    status: Optional[str] = None
    foto_url: Optional[str] = None

    @validator('cpf')
    def validate_cpf(cls, v):
        if v is not None:
            cpf = ''.join(filter(str.isdigit, v))
            if len(cpf) != 11:
                raise ValueError('CPF deve ter 11 dígitos')
        return v

    @validator('salario')
    def validate_salario(cls, v):
        if v is not None and v < 0:
            raise ValueError('Salário não pode ser negativo')
        return v

class FuncionarioResponse(BaseModel):
    id: int
    nome_completo: str
    nome_usuario: str
    cpf: str
    rg: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    endereco: Optional[str]
    cargo: Optional[str]
    salario: Optional[float]
    data_admissao: Optional[datetime]
    status: str
    foto_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

