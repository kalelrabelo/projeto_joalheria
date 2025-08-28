from src.models.user import db

class Material(db.Model):
    __tablename__ = 'material'
    
    id = db.Column(db.Integer, primary_key=True)
    idmat = db.Column(db.Integer, unique=True, nullable=False)  # ID original do sistema antigo
    idmatimp = db.Column(db.Float)
    foto = db.Column(db.String(255))
    tipo = db.Column(db.String(100))
    nome = db.Column(db.String(200))
    dimensao = db.Column(db.String(50))  # Unidade de medida (g, mt, Kg, Unid.)
    precopordimensao = db.Column(db.Float, default=0.0)
    cor = db.Column(db.String(100))
    noticia = db.Column(db.Text)
    ststoque = db.Column(db.String(100))
    qmin = db.Column(db.Integer, default=0)
    webexport = db.Column(db.Boolean, default=False)
    exportiert = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Material {self.idmat}: {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'idmat': self.idmat,
            'idmatimp': self.idmatimp,
            'foto': self.foto,
            'tipo': self.tipo,
            'nome': self.nome,
            'dimensao': self.dimensao,
            'precopordimensao': self.precopordimensao,
            'cor': self.cor,
            'noticia': self.noticia,
            'ststoque': self.ststoque,
            'qmin': self.qmin,
            'webexport': self.webexport,
            'exportiert': self.exportiert
        }
    
    @property
    def categoria(self):
        """Retorna a categoria baseada no tipo"""
        if 'prata' in (self.tipo or '').lower():
            return 'Metais Preciosos'
        elif 'couro' in (self.tipo or '').lower():
            return 'Couro'
        elif 'secundario' in (self.tipo or '').lower():
            return 'Materiais Secundários'
        else:
            return 'Outros'

