import pytest
import tempfile
import os
from src.database import Base, engine, SessionLocal
from src.config import Config

@pytest.fixture
def app():
    """Criar aplicação Flask para testes"""
    from src.main import app
    
    # Configurar banco de dados em memória para testes
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        Base.metadata.create_all(bind=engine)
        yield app
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Sessão de banco de dados para testes"""
    with app.app_context():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

@pytest.fixture
def sample_funcionario():
    """Dados de exemplo para funcionário"""
    return {
        "nome_completo": "João Silva",
        "nome_usuario": "joao",
        "senha": "123456",
        "cpf": "12345678901",
        "cargo": "Vendedor",
        "salario": 1500.0,
        "telefone": "(85) 99999-9999",
        "email": "joao@teste.com"
    }

@pytest.fixture
def sample_joia():
    """Dados de exemplo para joia"""
    return {
        "nome": "Anel de Ouro",
        "categoria": "Anel",
        "material": "Ouro 18k",
        "peso": 5.5,
        "preco_custo": 200.0,
        "preco_venda": 400.0,
        "quantidade_estoque": 10,
        "estoque_minimo": 2,
        "descricao": "Anel de ouro 18k com design clássico"
    }

@pytest.fixture
def sample_cliente():
    """Dados de exemplo para cliente"""
    return {
        "nome_completo": "Maria Santos",
        "cpf_cnpj": "12345678901",
        "telefone": "(85) 88888-8888",
        "email": "maria@teste.com",
        "endereco": "Rua das Flores, 123"
    }

