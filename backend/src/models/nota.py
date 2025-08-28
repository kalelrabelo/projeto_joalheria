from src.models.user import db

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idn = db.Column(db.Integer)
    idc = db.Column(db.Integer)
    ide = db.Column(db.Integer)
    remetente1 = db.Column(db.String(255))
    remetente2 = db.Column(db.String(255))
    remetente3 = db.Column(db.String(255))
    remetente4 = db.Column(db.String(255))
    remetente6 = db.Column(db.String(255))
    remetente7 = db.Column(db.String(255))
    remetente8 = db.Column(db.String(255))
    remetente9 = db.Column(db.String(255))
    remetente10 = db.Column(db.String(255))
    des1 = db.Column(db.String(255))
    des2 = db.Column(db.String(255))
    des3 = db.Column(db.String(255))
    des4 = db.Column(db.String(255))
    des5 = db.Column(db.String(255))
    des6 = db.Column(db.String(255))
    des7 = db.Column(db.String(255))
    des8 = db.Column(db.String(255))
    fax = db.Column(db.String(255))
    email = db.Column(db.String(255))
    data = db.Column(db.String(255))
    lugar = db.Column(db.String(255))
    mensagem = db.Column(db.String(255))
    noticia = db.Column(db.String(255))
    modo = db.Column(db.String(255))
    autor = db.Column(db.String(255))
    estadonota = db.Column(db.String(255))
    pago = db.Column(db.Integer)
    imposto1 = db.Column(db.String(255))
    imposto1v = db.Column(db.String(255))
    imposto2 = db.Column(db.String(255))
    imposto2v = db.Column(db.String(255))
    imposto3 = db.Column(db.String(255))
    imposto3v = db.Column(db.String(255))
    imposto4 = db.Column(db.String(255))
    imposto4v = db.Column(db.String(255))
    imposto5 = db.Column(db.String(255))
    imposto5v = db.Column(db.String(255))
    imposto6 = db.Column(db.String(255))
    imposto6v = db.Column(db.String(255))
    desconto = db.Column(db.Float)
    valor = db.Column(db.String(255))
    cambio = db.Column(db.Float)
    praco1 = db.Column(db.Integer)
    praco1f = db.Column(db.Float)
    praco2 = db.Column(db.Integer)
    praco2f = db.Column(db.Float)
    praco3 = db.Column(db.Integer)
    praco3f = db.Column(db.Float)
    taxa1v = db.Column(db.Integer)
    taxa2v = db.Column(db.Integer)
    taxa3v = db.Column(db.Integer)

    def __repr__(self):
        return f'<Nota {self.idn}>'

    def to_dict(self):
        return {
            'id': self.id,
            'idn': self.idn,
            'idc': self.idc,
            'ide': self.ide,
            'remetente1': self.remetente1,
            'remetente2': self.remetente2,
            'remetente3': self.remetente3,
            'remetente4': self.remetente4,
            'remetente6': self.remetente6,
            'remetente7': self.remetente7,
            'remetente8': self.remetente8,
            'remetente9': self.remetente9,
            'remetente10': self.remetente10,
            'des1': self.des1,
            'des2': self.des2,
            'des3': self.des3,
            'des4': self.des4,
            'des5': self.des5,
            'des6': self.des6,
            'des7': self.des7,
            'des8': self.des8,
            'fax': self.fax,
            'email': self.email,
            'data': self.data,
            'lugar': self.lugar,
            'mensagem': self.mensagem,
            'noticia': self.noticia,
            'modo': self.modo,
            'autor': self.autor,
            'estadonota': self.estadonota,
            'pago': self.pago,
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
            'desconto': self.desconto,
            'valor': self.valor,
            'cambio': self.cambio,
            'praco1': self.praco1,
            'praco1f': self.praco1f,
            'praco2': self.praco2,
            'praco2f': self.praco2f,
            'praco3': self.praco3,
            'praco3f': self.praco3f,
            'taxa1v': self.taxa1v,
            'taxa2v': self.taxa2v,
            'taxa3v': self.taxa3v
        }


