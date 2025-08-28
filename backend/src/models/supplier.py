# backend/src/models/supplier.py

from src.models.user import db
from datetime import datetime

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    cnpj = db.Column(db.String(20))
    contact_person = db.Column(db.String(100))
    product_category = db.Column(db.String(100))  # Ex: "Ouro", "Prata", "Pedras", etc.
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'cnpj': self.cnpj,
            'contact_person': self.contact_person,
            'product_category': self.product_category,
            'notes': self.notes,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

