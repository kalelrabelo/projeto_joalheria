# -*- coding: utf-8 -*-
# Configuração do Banco de Dados SQLite

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import Config

# Configuração do banco SQLite
DATABASE_URL = Config.DATABASE_URL

# Criar engine com configurações otimizadas
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELOS DO BANCO ====================

class Funcionario(Base):
    """Módulo RUBI - Gestão de Funcionários"""
    __tablename__ = "funcionarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(200), nullable=False)
    nome_usuario = Column(String(50), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    rg = Column(String(20))
    telefone = Column(String(20))
    email = Column(String(100))
    endereco = Column(Text)
    cargo = Column(String(100))
    salario = Column(Float, default=0.0)
    data_admissao = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='ativo')
    foto_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    vales = relationship("Vale", back_populates="funcionario")
    folhas_pagamento = relationship("FolhaPagamento", back_populates="funcionario")

class Vale(Base):
    """Módulo RUBI - Vales de Funcionários"""
    __tablename__ = "vales"
    
    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    valor = Column(Float, nullable=False)
    motivo = Column(String(200))
    data_vale = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='ativo')
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    funcionario = relationship("Funcionario", back_populates="vales")

class FolhaPagamento(Base):
    """Módulo RUBI - Folha de Pagamento"""
    __tablename__ = "folha_pagamento"
    
    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    salario_base = Column(Float, nullable=False)
    horas_extras = Column(Float, default=0.0)
    valor_horas_extras = Column(Float, default=0.0)
    total_vales = Column(Float, default=0.0)
    inss = Column(Float, default=0.0)
    irrf = Column(Float, default=0.0)
    outros_descontos = Column(Float, default=0.0)
    salario_liquido = Column(Float, nullable=False)
    data_pagamento = Column(DateTime)
    status = Column(String(20), default='pendente')
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    funcionario = relationship("Funcionario", back_populates="folhas_pagamento")

class Joia(Base):
    """Módulo ESMERALDA - Controle de Estoque de Joias"""
    __tablename__ = "joias"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=False)
    material = Column(String(100))
    peso = Column(Float)
    preco_custo = Column(Float)
    preco_venda = Column(Float)
    quantidade_estoque = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=1)
    descricao = Column(Text)
    foto_url = Column(String(500))
    codigo_barras = Column(String(50), unique=True)
    status = Column(String(20), default='ativo')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    vendas = relationship("Venda", back_populates="joia")
    encomendas = relationship("Encomenda", back_populates="joia")

class Cliente(Base):
    """Módulo PÉROLA - Gestão de Clientes"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(200), nullable=False)
    cpf_cnpj = Column(String(20), unique=True)
    telefone = Column(String(20))
    email = Column(String(100))
    endereco = Column(Text)
    data_nascimento = Column(DateTime)
    observacoes = Column(Text)
    status = Column(String(20), default='ativo')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    vendas = relationship("Venda", back_populates="cliente")
    encomendas = relationship("Encomenda", back_populates="cliente")

class Venda(Base):
    """Módulo DIAMANTE - Controle de Vendas"""
    __tablename__ = "vendas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    joia_id = Column(Integer, ForeignKey("joias.id"))
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"))
    quantidade = Column(Integer, default=1)
    preco_unitario = Column(Float, nullable=False)
    desconto = Column(Float, default=0.0)
    valor_total = Column(Float, nullable=False)
    forma_pagamento = Column(String(50))
    data_venda = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='concluida')
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="vendas")
    joia = relationship("Joia", back_populates="vendas")
    funcionario = relationship("Funcionario")

class Encomenda(Base):
    """Módulo SAFIRA - Gestão de Encomendas"""
    __tablename__ = "encomendas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    joia_id = Column(Integer, ForeignKey("joias.id"))
    funcionario_responsavel_id = Column(Integer, ForeignKey("funcionarios.id"))
    descricao = Column(Text, nullable=False)
    quantidade = Column(Integer, default=1)
    preco_acordado = Column(Float)
    data_pedido = Column(DateTime, default=datetime.now)
    data_prevista = Column(DateTime)
    data_entrega = Column(DateTime)
    status = Column(String(50), default='pendente')  # pendente, em_producao, concluida, entregue
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="encomendas")
    joia = relationship("Joia", back_populates="encomendas")
    funcionario_responsavel = relationship("Funcionario")

class MovimentacaoCaixa(Base):
    """Módulo DIAMANTE - Controle de Caixa"""
    __tablename__ = "movimentacao_caixa"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)  # entrada, saida
    categoria = Column(String(100), nullable=False)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"))
    data_movimentacao = Column(DateTime, default=datetime.now)
    forma_pagamento = Column(String(50))
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    funcionario = relationship("Funcionario")

class ConsumoEnergia(Base):
    """Módulo OPALA - Controle de Energia"""
    __tablename__ = "consumo_energia"
    
    id = Column(Integer, primary_key=True, index=True)
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    consumo_kwh = Column(Float, nullable=False)
    valor_conta = Column(Float, nullable=False)
    data_leitura = Column(DateTime, default=datetime.now)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)



class Material(Base):
    """Módulo ESMERALDA - Materiais de Joias"""
    __tablename__ = "materiais"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    categoria = Column(String(100))
    unidade_medida = Column(String(20))
    quantidade_estoque = Column(Float, default=0.0)
    preco_por_unidade = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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

# ==================== FUNÇÕES DE BANCO ====================

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados SQLite inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def test_connection():
    """Testa a conexão com o banco"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Conexão com SQLite estabelecida!")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

# ==================== DADOS INICIAIS ====================

def seed_initial_data():
    """Popula o banco com dados iniciais dos funcionários reais"""
    db = SessionLocal()
    try:
        # Verificar se já existem funcionários
        if db.query(Funcionario).count() > 0:
            print("✅ Dados iniciais já existem no banco")
            return
        
        # Funcionários reais da joalheria
        funcionarios_iniciais = [
            {
                "nome_completo": "Francisco Antonio Rabelo",
                "nome_usuario": "rabelo",
                "senha": "rabeloce",
                "cpf": "123.456.789-01",
                "cargo": "Gerente Geral",
                "salario": 2500.00,
                "telefone": "(85) 99999-0001",
                "email": "rabelo@joalheria.com"
            },
            {
                "nome_completo": "Alex Santos Silva",
                "nome_usuario": "alex",
                "senha": "a",
                "cpf": "123.456.789-02",
                "cargo": "Vendedor",
                "salario": 1800.00,
                "telefone": "(85) 99999-0002",
                "email": "alex@joalheria.com"
            },
            {
                "nome_completo": "David Einstein Araújo Rabelo",
                "nome_usuario": "david",
                "senha": "1818",
                "cpf": "123.456.789-03",
                "cargo": "Técnico em Joalheria",
                "salario": 1500.00,
                "telefone": "(85) 99999-0003",
                "email": "david@joalheria.com"
            },
            {
                "nome_completo": "Antonio Darvin Araújo Rabelo",
                "nome_usuario": "darvin",
                "senha": "16",
                "cpf": "123.456.789-04",
                "cargo": "Supervisor de Produção",
                "salario": 2000.00,
                "telefone": "(85) 99999-0004",
                "email": "darvin@joalheria.com"
            },
            {
                "nome_completo": "José Carlos Oliveira",
                "nome_usuario": "0751",
                "senha": "0751",
                "cpf": "123.456.789-05",
                "cargo": "Operador de Máquinas",
                "salario": 1700.00,
                "telefone": "(85) 99999-0005",
                "email": "jose@joalheria.com"
            },
            {
                "nome_completo": "Josemir Rabelo",
                "nome_usuario": "josa",
                "senha": "josa123",
                "cpf": "123.456.789-06",
                "cargo": "Coordenador de Vendas",
                "salario": 2460.80,
                "telefone": "(85) 99999-0006",
                "email": "josemir@joalheria.com"
            }
        ]
        
        for func_data in funcionarios_iniciais:
            funcionario = Funcionario(**func_data)
            db.add(funcionario)
        
        db.commit()
        print("✅ Dados iniciais inseridos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados iniciais: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Inicializando banco SQLite...")
    if test_connection():
        if init_database():
            seed_initial_data()
            print("✅ Sistema de banco pronto para uso!")
    else:
        print("❌ Falha na inicialização do banco!")

