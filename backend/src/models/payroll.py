from src.models.user import db
from datetime import datetime

class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    base_salary = db.Column(db.Float, nullable=False)
    total_vales = db.Column(db.Float, default=0.0)  # Total de vales descontados
    net_salary = db.Column(db.Float, nullable=False)  # Salário líquido (base - vales)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", backref="payrolls")

    def __repr__(self):
        return f"<Payroll {self.employee_id} - {self.month}/{self.year}>"

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee.name if self.employee else None,
            "month": self.month,
            "year": self.year,
            "base_salary": self.base_salary,
            "total_vales": self.total_vales,
            "net_salary": self.net_salary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_net_salary(self):
        """Calcula o salário líquido baseado no salário base menos os vales"""
        self.net_salary = self.base_salary - self.total_vales
        return self.net_salary

    def update_vales_total(self):
        """Atualiza o total de vales baseado nos vales registrados no mês/ano"""
        from src.models.vale import Vale
        from sqlalchemy import extract
        
        # Buscar todos os vales do funcionário no mês/ano específico
        vales = Vale.query.filter(
            Vale.employee_id == self.employee_id,
            extract('month', Vale.date) == self.month,
            extract('year', Vale.date) == self.year
        ).all()
        
        self.total_vales = sum(vale.amount for vale in vales)
        self.calculate_net_salary()
        return self.total_vales

