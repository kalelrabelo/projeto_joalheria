from src.models.user import db
from datetime import datetime

class FinancialTransaction(db.Model):
    __tablename__ = 'financial_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    valor1 = db.Column(db.Float, nullable=False)
    valor2 = db.Column(db.Float, nullable=True)
    valor = db.Column(db.String(10), default='R$')
    imposto = db.Column(db.Float, nullable=True)
    imposto2 = db.Column(db.Float, nullable=True)
    imposto3 = db.Column(db.Float, nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    grupo1 = db.Column(db.String(100), nullable=False)
    grupo2 = db.Column(db.String(100), nullable=False)
    idc = db.Column(db.Float, nullable=True)
    nome = db.Column(db.String(200), nullable=True)
    noticia = db.Column(db.Text, nullable=True)
    caixa = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'mes': self.mes,
            'ano': self.ano,
            'valor1': self.valor1,
            'valor2': self.valor2,
            'valor': self.valor,
            'imposto': self.imposto,
            'imposto2': self.imposto2,
            'imposto3': self.imposto3,
            'descricao': self.descricao,
            'grupo1': self.grupo1,
            'grupo2': self.grupo2,
            'idc': self.idc,
            'nome': self.nome,
            'noticia': self.noticia,
            'caixa': self.caixa
        }

class ProductionReport(db.Model):
    __tablename__ = 'production_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lugar = db.Column(db.String(100), nullable=False)
    assunto = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), default='OK')
    noticia = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'lugar': self.lugar,
            'assunto': self.assunto,
            'mensagem': self.mensagem,
            'autor': self.autor,
            'estado': self.estado,
            'noticia': self.noticia
        }

class AdvancedOrder(db.Model):
    __tablename__ = 'advanced_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    idc = db.Column(db.Integer, nullable=False)  # ID do cliente
    data_encomenda = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modo_encomenda = db.Column(db.String(100), nullable=True)
    pessoala = db.Column(db.String(200), nullable=True)
    pessoaaqui = db.Column(db.String(200), nullable=True)
    praco = db.Column(db.DateTime, nullable=True)
    estado_encomenda = db.Column(db.String(50), default='novo')
    noticia = db.Column(db.Text, nullable=True)
    ultimanota = db.Column(db.Integer, default=0)
    
    # Impostos
    imposto1 = db.Column(db.String(50), nullable=True)
    imposto1v = db.Column(db.Float, nullable=True)
    imposto2 = db.Column(db.String(50), nullable=True)
    imposto2v = db.Column(db.Float, nullable=True)
    imposto3 = db.Column(db.String(50), nullable=True)
    imposto3v = db.Column(db.Float, nullable=True)
    imposto4 = db.Column(db.String(50), nullable=True)
    imposto4v = db.Column(db.Float, nullable=True)
    imposto5 = db.Column(db.String(50), nullable=True)
    imposto5v = db.Column(db.Float, nullable=True)
    imposto6 = db.Column(db.String(50), nullable=True)
    imposto6v = db.Column(db.Float, nullable=True)
    
    desconto_encomenda = db.Column(db.Float, default=0.0)
    valor_total_encomenda = db.Column(db.String(10), default='R$')
    cambio = db.Column(db.Float, default=1.0)
    
    # Prazos
    praco1 = db.Column(db.Integer, default=30)
    praco1f = db.Column(db.Float, default=1.1)
    praco2 = db.Column(db.Integer, default=60)
    praco2f = db.Column(db.Float, default=1.15)
    praco3 = db.Column(db.Integer, default=90)
    praco3f = db.Column(db.Float, default=1.2)
    
    # Taxas
    taxa1v = db.Column(db.Float, default=0)
    taxa2v = db.Column(db.Float, default=0)
    taxa3v = db.Column(db.Float, default=0)
    
    entregaonde = db.Column(db.String(100), nullable=True)
    fabricarate = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'idc': self.idc,
            'data_encomenda': self.data_encomenda.isoformat() if self.data_encomenda else None,
            'modo_encomenda': self.modo_encomenda,
            'pessoala': self.pessoala,
            'pessoaaqui': self.pessoaaqui,
            'praco': self.praco.isoformat() if self.praco else None,
            'estado_encomenda': self.estado_encomenda,
            'noticia': self.noticia,
            'ultimanota': self.ultimanota,
            'imposto1': self.imposto1,
            'imposto1v': self.imposto1v,
            'imposto2': self.imposto2,
            'imposto2v': self.imposto2v,
            'imposto3': self.imposto3,
            'imposto3v': self.imposto3v,
            'imposto4': self.imposto4,
            'imposto4v': self.imposto4v,
            'imposto5': self.imposto5,
            'imposto5v': self.imposto5v,
            'imposto6': self.imposto6,
            'imposto6v': self.imposto6v,
            'desconto_encomenda': self.desconto_encomenda,
            'valor_total_encomenda': self.valor_total_encomenda,
            'cambio': self.cambio,
            'praco1': self.praco1,
            'praco1f': self.praco1f,
            'praco2': self.praco2,
            'praco2f': self.praco2f,
            'praco3': self.praco3,
            'praco3f': self.praco3f,
            'taxa1v': self.taxa1v,
            'taxa2v': self.taxa2v,
            'taxa3v': self.taxa3v,
            'entregaonde': self.entregaonde,
            'fabricarate': self.fabricarate.isoformat() if self.fabricarate else None
        }

class DiscountTable(db.Model):
    __tablename__ = 'discount_table'
    
    id = db.Column(db.Integer, primary_key=True)
    soma = db.Column(db.Float, nullable=False)
    desconto = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'soma': self.soma,
            'desconto': self.desconto
        }

class CostCalculation(db.Model):
    __tablename__ = 'cost_calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    empregados = db.Column(db.Integer, nullable=False)
    horas_por_semana = db.Column(db.Integer, nullable=False)
    rs_por_hora = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ano': self.ano,
            'mes': self.mes,
            'empregados': self.empregados,
            'horas_por_semana': self.horas_por_semana,
            'rs_por_hora': self.rs_por_hora
        }

