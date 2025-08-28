from src.models.user import db
from datetime import datetime

from src.models.client import Client

class Order(db.Model):
    customer_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    customer = db.relationship("Client", backref="orders")
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, in_progress, completed, cancelled
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    materials_reserved = db.Column(db.Boolean, default=False)  # Se os materiais já foram reservados do estoque
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", backref="orders")

    def __repr__(self):
        return f"<Order {self.id} - {self.customer_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer.name if self.customer else None,
            "customer_contact": self.customer.phone if self.customer else None,
            "product_id": self.product_id,
            "product_name": self.product.descricao if self.product else None,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "status": self.status,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "notes": self.notes,
            "materials_reserved": self.materials_reserved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_total_price(self):
        """Calcula o preço total baseado na quantidade e preço unitário"""
        self.total_price = self.quantity * self.unit_price
        return self.total_price

    def reserve_materials(self):
        """Reserva materiais do estoque para esta encomenda"""
        if self.materials_reserved:
            return {"error": "Materiais já foram reservados para esta encomenda"}
        
        try:
            from src.models.inventory import Inventory
            from src.models.product import Product
            
            # Buscar a joia e seus materiais necessários
            product = Product.query.get(self.product_id)
            if not product:
                return {"error": "Produto não encontrado"}
            
            # Aqui você implementaria a lógica para buscar os materiais necessários
            # Por enquanto, vamos assumir que existe uma relação entre joias e materiais
            # que precisa ser implementada no modelo Jewelry
            
            # Marcar materiais como reservados
            self.materials_reserved = True
            db.session.commit()
            
            return {"success": "Materiais reservados com sucesso"}
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    def complete_order(self):
        """Finaliza a encomenda e atualiza o estoque definitivamente"""
        if self.status == 'completed':
            return {"error": "Encomenda já foi finalizada"}
        
        try:
            # Atualizar status
            self.status = 'completed'
            
            # Consumir materiais reservados do estoque
            if self.materials_reserved:
                # Implementar lógica para consumir materiais reservados
                # Por enquanto, apenas marcar como não reservado
                self.materials_reserved = False
            
            # Registrar custos automáticos
            self._register_automatic_costs()
            
            # Calcular e registrar lucro
            self._calculate_and_register_profit()
            
            db.session.commit()
            
            return {"success": "Encomenda finalizada com sucesso"}
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    def _register_automatic_costs(self):
        """Registra custos automáticos quando a encomenda é finalizada"""
        from src.models.cost import Cost
        from src.models.inventory import Inventory
        
        # Custo de materiais (baseado no estoque)
        # Aqui você implementaria a lógica para calcular custos de materiais
        # baseado nos materiais usados na joia
        
        # Custo de energia (exemplo: R$ 5,00 por joia)
        energy_cost = Cost(
            order_id=self.id,
            category='energy',
            description='Custo de energia para produção',
            amount=5.00,
            notes='Custo automático calculado'
        )
        db.session.add(energy_cost)
        
        # Custo de mão de obra (exemplo: 20% do preço de venda)
        labor_cost = Cost(
            order_id=self.id,
            category='labor',
            description='Custo de mão de obra',
            amount=self.total_price * 0.20,
            notes='20% do preço de venda'
        )
        db.session.add(labor_cost)

    def _calculate_and_register_profit(self):
        """Calcula e registra o lucro da encomenda"""
        from src.models.cost import Profit
        
        # Criar registro de lucro
        profit = Profit.create_from_order(self)
        
        if isinstance(profit, dict) and "error" in profit:
            # Se já existe ou houve erro, não fazer nada
            return profit
        
        db.session.add(profit)
        return profit

    def cancel_order(self):
        """Cancela a encomenda e libera materiais reservados"""
        if self.status == 'completed':
            return {"error": "Não é possível cancelar uma encomenda já finalizada"}
        
        try:
            # Liberar materiais reservados se houver
            if self.materials_reserved:
                # Implementar lógica para liberar materiais do estoque
                self.materials_reserved = False
            
            # Atualizar status
            self.status = 'cancelled'
            
            db.session.commit()
            
            return {"success": "Encomenda cancelada e materiais liberados"}
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

