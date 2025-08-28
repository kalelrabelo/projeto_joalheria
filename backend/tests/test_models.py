import pytest
from datetime import datetime
from src.database import Funcionario, Joia, Cliente, Venda, Vale

def test_funcionario_creation(db_session, sample_funcionario):
    """Teste de criação de funcionário"""
    funcionario = Funcionario(**sample_funcionario)
    db_session.add(funcionario)
    db_session.commit()
    
    assert funcionario.id is not None
    assert funcionario.nome_completo == sample_funcionario["nome_completo"]
    assert funcionario.cpf == sample_funcionario["cpf"]
    assert funcionario.status == "ativo"

def test_joia_creation(db_session, sample_joia):
    """Teste de criação de joia"""
    joia = Joia(**sample_joia)
    db_session.add(joia)
    db_session.commit()
    
    assert joia.id is not None
    assert joia.nome == sample_joia["nome"]
    assert joia.preco_venda == sample_joia["preco_venda"]
    assert joia.quantidade_estoque == sample_joia["quantidade_estoque"]

def test_cliente_creation(db_session, sample_cliente):
    """Teste de criação de cliente"""
    cliente = Cliente(**sample_cliente)
    db_session.add(cliente)
    db_session.commit()
    
    assert cliente.id is not None
    assert cliente.nome_completo == sample_cliente["nome_completo"]
    assert cliente.cpf_cnpj == sample_cliente["cpf_cnpj"]
    assert cliente.status == "ativo"

def test_venda_creation(db_session, sample_funcionario, sample_joia, sample_cliente):
    """Teste de criação de venda"""
    # Criar dependências
    funcionario = Funcionario(**sample_funcionario)
    joia = Joia(**sample_joia)
    cliente = Cliente(**sample_cliente)
    
    db_session.add_all([funcionario, joia, cliente])
    db_session.commit()
    
    # Criar venda
    venda = Venda(
        cliente_id=cliente.id,
        joia_id=joia.id,
        funcionario_id=funcionario.id,
        quantidade=1,
        preco_unitario=400.0,
        valor_total=400.0,
        forma_pagamento="Dinheiro"
    )
    
    db_session.add(venda)
    db_session.commit()
    
    assert venda.id is not None
    assert venda.valor_total == 400.0
    assert venda.status == "concluida"

def test_vale_creation(db_session, sample_funcionario):
    """Teste de criação de vale"""
    funcionario = Funcionario(**sample_funcionario)
    db_session.add(funcionario)
    db_session.commit()
    
    vale = Vale(
        funcionario_id=funcionario.id,
        valor=100.0,
        motivo="Adiantamento salarial"
    )
    
    db_session.add(vale)
    db_session.commit()
    
    assert vale.id is not None
    assert vale.valor == 100.0
    assert vale.status == "ativo"

def test_funcionario_vales_relationship(db_session, sample_funcionario):
    """Teste de relacionamento funcionário-vales"""
    funcionario = Funcionario(**sample_funcionario)
    db_session.add(funcionario)
    db_session.commit()
    
    # Criar vales
    vale1 = Vale(funcionario_id=funcionario.id, valor=50.0, motivo="Vale 1")
    vale2 = Vale(funcionario_id=funcionario.id, valor=75.0, motivo="Vale 2")
    
    db_session.add_all([vale1, vale2])
    db_session.commit()
    
    # Verificar relacionamento
    assert len(funcionario.vales) == 2
    assert sum(v.valor for v in funcionario.vales) == 125.0

