from src.models.user import db
from datetime import datetime

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=False)
    quantity_available = db.Column(db.Float, nullable=False, default=0.0)
    quantity_reserved = db.Column(db.Float, nullable=False, default=0.0)  # Quantidade reservada para encomendas
    unit = db.Column(db.String(20), nullable=False, default='unidade')  # gramas, unidades, metros, etc.
    minimum_stock = db.Column(db.Float, default=0.0)  # Estoque mínimo para alertas
    cost_per_unit = db.Column(db.Float, default=0.0)  # Custo por unidade
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)

    material = db.relationship("Material", backref="inventory")

    def __repr__(self):
        return f"<Inventory {self.material_id} - {self.quantity_available} {self.unit}>"

    def to_dict(self):
        return {
            "id": self.id,
            "material_id": self.material_id,
            "material_name": self.material.nome if self.material else None,
            "quantity_available": self.quantity_available,
            "quantity_reserved": self.quantity_reserved,
            "total_quantity": self.quantity_available + self.quantity_reserved,
            "unit": self.unit,
            "minimum_stock": self.minimum_stock,
            "cost_per_unit": self.cost_per_unit,
            "is_low_stock": self.is_low_stock(),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "notes": self.notes,
        }

    def is_low_stock(self):
        """Verifica se o estoque está baixo"""
        return self.quantity_available <= self.minimum_stock

    def reserve_quantity(self, quantity):
        """Reserva uma quantidade do estoque para uma encomenda"""
        if self.quantity_available < quantity:
            return {"error": f"Estoque insuficiente. Disponível: {self.quantity_available} {self.unit}"}
        
        self.quantity_available -= quantity
        self.quantity_reserved += quantity
        
        return {"success": f"{quantity} {self.unit} reservados com sucesso"}

    def release_reservation(self, quantity):
        """Libera uma reserva e retorna a quantidade ao estoque disponível"""
        if self.quantity_reserved < quantity:
            return {"error": f"Quantidade reservada insuficiente. Reservado: {self.quantity_reserved} {self.unit}"}
        
        self.quantity_reserved -= quantity
        self.quantity_available += quantity
        
        return {"success": f"{quantity} {self.unit} liberados da reserva"}

    def consume_reserved(self, quantity):
        """Consome uma quantidade reservada (para finalização de encomenda)"""
        if self.quantity_reserved < quantity:
            return {"error": f"Quantidade reservada insuficiente. Reservado: {self.quantity_reserved} {self.unit}"}
        
        self.quantity_reserved -= quantity
        
        return {"success": f"{quantity} {self.unit} consumidos do estoque"}

    def add_stock(self, quantity, cost_per_unit=None):
        """Adiciona estoque (entrada de materiais)"""
        self.quantity_available += quantity
        
        if cost_per_unit is not None:
            # Calcular custo médio ponderado
            total_current_value = (self.quantity_available - quantity) * self.cost_per_unit
            total_new_value = quantity * cost_per_unit
            total_quantity = self.quantity_available
            
            if total_quantity > 0:
                self.cost_per_unit = (total_current_value + total_new_value) / total_quantity
        
        return {"success": f"{quantity} {self.unit} adicionados ao estoque"}

    def remove_stock(self, quantity):
        """Remove estoque diretamente (perdas, danos, etc.)"""
        total_available = self.quantity_available + self.quantity_reserved
        
        if total_available < quantity:
            return {"error": f"Quantidade insuficiente no estoque. Total: {total_available} {self.unit}"}
        
        # Remover primeiro do estoque disponível, depois do reservado
        if self.quantity_available >= quantity:
            self.quantity_available -= quantity
        else:
            remaining = quantity - self.quantity_available
            self.quantity_available = 0
            self.quantity_reserved -= remaining
        
        return {"success": f"{quantity} {self.unit} removidos do estoque"}

    def calculate_total_value(self):
        """Calcula o valor total do estoque (disponível + reservado)"""
        total_quantity = self.quantity_available + self.quantity_reserved
        return total_quantity * self.cost_per_unit

