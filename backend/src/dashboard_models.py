# -*- coding: utf-8 -*-
"""
Modelos para Dashboard Editável
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class DashboardWidget(Base):
    """Widget do Dashboard Editável"""
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    tipo = Column(String(50), nullable=False)  # chart, table, metric, comparison
    configuracao = Column(JSON)  # Configurações específicas do widget
    posicao_x = Column(Integer, default=0)
    posicao_y = Column(Integer, default=0)
    largura = Column(Integer, default=4)
    altura = Column(Integer, default=3)
    grupo = Column(String(100))  # Grupo/módulo do sistema
    subgrupo = Column(String(100))  # Subgrupo específico
    filtros = Column(JSON)  # Filtros aplicados
    usuario_id = Column(Integer, ForeignKey("funcionarios.id"))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    usuario = relationship("Funcionario")

class DashboardLayout(Base):
    """Layout personalizado do Dashboard"""
    __tablename__ = "dashboard_layouts"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    usuario_id = Column(Integer, ForeignKey("funcionarios.id"))
    widgets = Column(JSON)  # Lista de IDs dos widgets
    configuracao_global = Column(JSON)  # Configurações globais do layout
    padrao = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    usuario = relationship("Funcionario")

class DashboardFilter(Base):
    """Filtros disponíveis para o Dashboard"""
    __tablename__ = "dashboard_filters"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(50), nullable=False)  # date, select, range, text
    campo_banco = Column(String(100), nullable=False)
    tabela = Column(String(100), nullable=False)
    opcoes = Column(JSON)  # Opções para filtros select
    grupo = Column(String(100))
    subgrupo = Column(String(100))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class DashboardQuery(Base):
    """Queries personalizadas para o Dashboard"""
    __tablename__ = "dashboard_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    query_sql = Column(Text, nullable=False)
    parametros = Column(JSON)  # Parâmetros da query
    tipo_retorno = Column(String(50))  # chart, table, metric
    grupo = Column(String(100))
    subgrupo = Column(String(100))
    usuario_id = Column(Integer, ForeignKey("funcionarios.id"))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    usuario = relationship("Funcionario")

