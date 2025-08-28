from src.models.user import db

class CaixaCategory(db.Model):
    """Categorias para saídas do caixa"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<CaixaCategory {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CaixaTransaction(db.Model):
    """Transações do caixa (entradas e saídas)"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'entrada' ou 'saida'
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255))
    
    # Para saídas categorizadas
    category_id = db.Column(db.Integer, db.ForeignKey('caixa_category.id'), nullable=True)
    category = db.relationship('CaixaCategory', backref='transactions')
    
    # Para retiradas de funcionários
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    employee = db.relationship('Employee', backref='caixa_transactions')
    
    # Referência para vales (quando integrado futuramente)
    vale_id = db.Column(db.Integer, db.ForeignKey('vale.id'), nullable=True)
    vale = db.relationship('Vale', backref='caixa_transaction')
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<CaixaTransaction {self.type} - {self.amount}>'

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'date': self.date,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'employee_id': self.employee_id,
            'employee': self.employee.to_dict() if self.employee else None,
            'vale_id': self.vale_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

