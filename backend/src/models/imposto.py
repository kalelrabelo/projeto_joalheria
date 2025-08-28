from src.models.user import db

class Imposto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255))
    imposto = db.Column(db.Float)

    def __repr__(self):
        return f'<Imposto {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'imposto': self.imposto
        }


