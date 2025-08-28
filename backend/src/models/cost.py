from src.models.user import db
from datetime import datetime

class Cost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=True)  # Pode ser nulo para custos gerais
    category = db.Column(db.String(50), nullable=False)  # materials, labor, energy, overhead, etc.
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=True)  # Para custos de materiais
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)  # Para custos de mão de obra
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", backref="costs")
    material = db.relationship("Material", backref="costs")
    employee = db.relationship("Employee", backref="costs")

    def __repr__(self):
        return f"<Cost {self.id} - {self.category}: {self.amount}>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "category": self.category,
            "description": self.description,
            "amount": self.amount,
            "date": self.date.isoformat() if self.date else None,
            "material_id": self.material_id,
            "material_name": self.material.nome if self.material else None,
            "employee_id": self.employee_id,
            "employee_name": self.employee.name if self.employee else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Profit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    revenue = db.Column(db.Float, nullable=False)  # Receita (preço de venda)
    total_costs = db.Column(db.Float, nullable=False)  # Custos totais
    gross_profit = db.Column(db.Float, nullable=False)  # Lucro bruto (receita - custos)
    profit_margin = db.Column(db.Float, nullable=False)  # Margem de lucro (%)
    date_calculated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)

    order = db.relationship("Order", backref="profit", uselist=False)

    def __repr__(self):
        return f"<Profit {self.id} - Order {self.order_id}: {self.gross_profit}>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "order_customer": self.order.customer_name if self.order else None,
            "revenue": self.revenue,
            "total_costs": self.total_costs,
            "gross_profit": self.gross_profit,
            "profit_margin": self.profit_margin,
            "date_calculated": self.date_calculated.isoformat() if self.date_calculated else None,
            "notes": self.notes,
        }

    def calculate_profit(self):
        """Calcula o lucro bruto e margem de lucro"""
        self.gross_profit = self.revenue - self.total_costs
        
        if self.revenue > 0:
            self.profit_margin = (self.gross_profit / self.revenue) * 100
        else:
            self.profit_margin = 0
        
        return {
            "gross_profit": self.gross_profit,
            "profit_margin": self.profit_margin
        }

    @staticmethod
    def calculate_order_costs(order_id):
        """Calcula os custos totais de uma encomenda"""
        total_costs = db.session.query(db.func.sum(Cost.amount)).filter_by(order_id=order_id).scalar() or 0
        return total_costs

    @staticmethod
    def create_from_order(order):
        """Cria registro de lucro a partir de uma encomenda finalizada"""
        from src.models.order import Order
        
        if not isinstance(order, Order):
            order = Order.query.get(order)
            if not order:
                return {"error": "Encomenda não encontrada"}
        
        if order.status != 'completed':
            return {"error": "Encomenda deve estar finalizada para calcular lucro"}
        
        # Verificar se já existe registro de lucro
        existing_profit = Profit.query.filter_by(order_id=order.id).first()
        if existing_profit:
            return {"error": "Registro de lucro já existe para esta encomenda"}
        
        # Calcular custos totais
        total_costs = Profit.calculate_order_costs(order.id)
        
        # Criar registro de lucro
        profit = Profit(
            order_id=order.id,
            revenue=order.total_price,
            total_costs=total_costs
        )
        
        # Calcular lucro e margem
        profit.calculate_profit()
        
        return profit

