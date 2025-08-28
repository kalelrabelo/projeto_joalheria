import pytest
from pydantic import ValidationError
from src.schemas.funcionario import FuncionarioCreate, FuncionarioUpdate
from src.schemas.joia import JoiaCreate, JoiaUpdate
from src.schemas.cliente import ClienteCreate, ClienteUpdate
from src.schemas.venda import VendaCreate, VendaUpdate
from src.schemas.vale import ValeCreate, ValeUpdate

def test_funcionario_schema_valid():
    """Teste de schema válido para funcionário"""
    data = {
        "nome_completo": "João Silva",
        "nome_usuario": "joao",
        "senha": "123456",
        "cpf": "12345678901",
        "salario": 1500.0
    }
    
    funcionario = FuncionarioCreate(**data)
    assert funcionario.nome_completo == "João Silva"
    assert funcionario.salario == 1500.0

def test_funcionario_schema_invalid_cpf():
    """Teste de CPF inválido"""
    data = {
        "nome_completo": "João Silva",
        "nome_usuario": "joao",
        "senha": "123456",
        "cpf": "123",  # CPF inválido
        "salario": 1500.0
    }
    
    with pytest.raises(ValidationError):
        FuncionarioCreate(**data)

def test_funcionario_schema_negative_salary():
    """Teste de salário negativo"""
    data = {
        "nome_completo": "João Silva",
        "nome_usuario": "joao",
        "senha": "123456",
        "cpf": "12345678901",
        "salario": -100.0  # Salário negativo
    }
    
    with pytest.raises(ValidationError):
        FuncionarioCreate(**data)

def test_joia_schema_valid():
    """Teste de schema válido para joia"""
    data = {
        "nome": "Anel de Ouro",
        "categoria": "Anel",
        "preco_custo": 200.0,
        "preco_venda": 400.0,
        "quantidade_estoque": 10
    }
    
    joia = JoiaCreate(**data)
    assert joia.nome == "Anel de Ouro"
    assert joia.preco_venda == 400.0

def test_joia_schema_negative_price():
    """Teste de preço negativo"""
    data = {
        "nome": "Anel de Ouro",
        "categoria": "Anel",
        "preco_custo": -200.0,  # Preço negativo
        "preco_venda": 400.0
    }
    
    with pytest.raises(ValidationError):
        JoiaCreate(**data)

def test_cliente_schema_valid():
    """Teste de schema válido para cliente"""
    data = {
        "nome_completo": "Maria Santos",
        "cpf_cnpj": "12345678901",
        "telefone": "(85) 99999-9999"
    }
    
    cliente = ClienteCreate(**data)
    assert cliente.nome_completo == "Maria Santos"

def test_cliente_schema_invalid_cpf():
    """Teste de CPF/CNPJ inválido"""
    data = {
        "nome_completo": "Maria Santos",
        "cpf_cnpj": "123",  # Documento inválido
    }
    
    with pytest.raises(ValidationError):
        ClienteCreate(**data)

def test_venda_schema_valid():
    """Teste de schema válido para venda"""
    data = {
        "joia_id": 1,
        "funcionario_id": 1,
        "quantidade": 2,
        "preco_unitario": 200.0,
        "valor_total": 400.0
    }
    
    venda = VendaCreate(**data)
    assert venda.quantidade == 2
    assert venda.valor_total == 400.0

def test_venda_schema_zero_quantity():
    """Teste de quantidade zero"""
    data = {
        "joia_id": 1,
        "funcionario_id": 1,
        "quantidade": 0,  # Quantidade inválida
        "preco_unitario": 200.0,
        "valor_total": 400.0
    }
    
    with pytest.raises(ValidationError):
        VendaCreate(**data)

def test_vale_schema_valid():
    """Teste de schema válido para vale"""
    data = {
        "funcionario_id": 1,
        "valor": 100.0,
        "motivo": "Adiantamento"
    }
    
    vale = ValeCreate(**data)
    assert vale.valor == 100.0
    assert vale.motivo == "Adiantamento"

def test_vale_schema_zero_value():
    """Teste de valor zero"""
    data = {
        "funcionario_id": 1,
        "valor": 0.0,  # Valor inválido
        "motivo": "Adiantamento"
    }
    
    with pytest.raises(ValidationError):
        ValeCreate(**data)

