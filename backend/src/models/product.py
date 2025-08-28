
from src.models.user import db

class Product(db.Model):
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    idj = db.Column(db.Integer, unique=True, nullable=False)  # ID original do sistema antigo
    idjimp = db.Column(db.Float)
    idpa = db.Column(db.Integer, db.ForeignKey("patterns.id"), index=True)  # Relacionamento com padrões
    foto = db.Column(db.String(255))
    noticia = db.Column(db.Text)
    descricao = db.Column(db.Text)
    escondido = db.Column(db.Boolean, default=False, index=True)
    precomat = db.Column(db.Float, default=0.0)
    precoped = db.Column(db.Float, default=0.0)
    precotem = db.Column(db.Float, default=0.0)
    preco0 = db.Column(db.Float, default=0.0)
    preco1 = db.Column(db.Float, default=0.0)
    preco2 = db.Column(db.Float, default=0.0)
    lucro1 = db.Column(db.Float, default=1.0)
    lucro2 = db.Column(db.Float, default=1.2)
    qmin = db.Column(db.Float, default=0.0)
    precoweb = db.Column(db.Float)
    webexport = db.Column(db.Boolean, default=False, index=True)
    exportiert = db.Column(db.String(50))
    
    # Relacionamentos
 pattern = db.relationship(\'Pattern\', backref=\'product_items\', lazy=True)    
    def __repr__(self):
        return f'<Product {self.idj}: {self.descricao[:50]}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'idj': self.idj,
            'idjimp': self.idjimp,
            'idpa': self.idpa,
            'foto': self.foto,
            'noticia': self.noticia,
            'descricao': self.descricao,
            'escondido': self.escondido,
            'precomat': self.precomat,
            'precoped': self.precoped,
            'precotem': self.precotem,
            'preco0': self.preco0,
            'preco1': self.preco1,
            'preco2': self.preco2,
            'lucro1': self.lucro1,
            'lucro2': self.lucro2,
            'qmin': self.qmin,
            'precoweb': self.precoweb,
            'webexport': self.webexport,
            'exportiert': self.exportiert,
            'pattern': self.pattern.to_dict() if self.pattern else None
        }
    
    @property
    def preco_total(self):
        """Calcula o preço total baseado nos componentes"""
        return (self.precomat or 0) + (self.precoped or 0) + (self.precotem or 0)
    
    @property
    def preco_final(self):
        """Calcula o preço final com margem de lucro"""
        return self.preco_total * (self.lucro2 or 1.2)

# Adicionando índices para otimizar consultas
# Index para busca por descricao e noticia (para full-text search, seria mais complexo)
db.Index("idx_product_descricao", Product.descricao)
db.Index("idx_product_noticia", Product.noticia)

# Índice para ordenação padrão
db.Index("idx_product_idj", Product.idj)


