from src.models.user import db
from datetime import datetime

class Pattern(db.Model):
    __tablename__ = 'patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    idpa = db.Column(db.Integer, unique=True, nullable=False)  # ID original do sistema antigo
    idpaimp = db.Column(db.Float)
    foto = db.Column(db.String(255))
    tipo = db.Column(db.String(100))  # brincos, anel, colar, etc.
    code = db.Column(db.String(100))
    colecao = db.Column(db.String(200))
    nome = db.Column(db.String(200))
    tempo = db.Column(db.Float, default=0.0)  # Tempo de produção em minutos
    noticia = db.Column(db.Text)  # Descrição detalhada
    comp = db.Column(db.Float, default=0.0)  # Comprimento
    lag = db.Column(db.Float, default=0.0)   # Largura
    alt = db.Column(db.Float, default=0.0)   # Altura
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pattern {self.idpa}: {self.nome}>'
    
    def to_dict(self, include_images=False):
        data = {
            'id': self.id,
            'idpa': self.idpa,
            'idpaimp': self.idpaimp,
            'foto': self.foto,
            'tipo': self.tipo,
            'code': self.code,
            'colecao': self.colecao,
            'nome': self.nome,
            'tempo': self.tempo,
            'tempo_formatado': self.tempo_formatado,
            'noticia': self.noticia,
            'comp': self.comp,
            'lag': self.lag,
            'alt': self.alt,
            'dimensoes_formatadas': self.dimensoes_formatadas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_images:
            data['images'] = [img.to_dict() for img in self.images]
            data['primary_image'] = next((img.to_dict() for img in self.images if img.is_primary), None)
        
        return data
    
    @property
    def tempo_formatado(self):
        """Retorna o tempo formatado em horas e minutos"""
        if not self.tempo:
            return "N/A"
        
        horas = int(self.tempo // 60)
        minutos = int(self.tempo % 60)
        
        if horas > 0:
            return f"{horas}h {minutos}min"
        else:
            return f"{minutos}min"
    
    @property
    def dimensoes_formatadas(self):
        """Retorna as dimensões formatadas"""
        dimensoes = []
        if self.comp and self.comp > 0:
            dimensoes.append(f"C: {self.comp}")
        if self.lag and self.lag > 0:
            dimensoes.append(f"L: {self.lag}")
        if self.alt and self.alt > 0:
            dimensoes.append(f"A: {self.alt}")
        
        return " x ".join(dimensoes) if dimensoes else "N/A"
    
    @property
    def primary_image(self):
        """Retorna a imagem primária do padrão"""
        return next((img for img in self.images if img.is_primary), None)
    
    def get_image_count(self):
        """Retorna o número de imagens associadas ao padrão"""
        return len(self.images)
    
    @staticmethod
    def get_tipos():
        """Retorna os tipos de padrões disponíveis"""
        return ['anel', 'brincos', 'colar', 'pingente', 'pulseira', 'bracelete', 'outros']
    
    @staticmethod
    def get_colecoes():
        """Retorna as coleções disponíveis"""
        colecoes = db.session.query(Pattern.colecao).distinct().filter(Pattern.colecao.isnot(None)).all()
        return [c[0] for c in colecoes if c[0]]

