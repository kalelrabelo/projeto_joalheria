from src.models.user import db
from datetime import datetime

class Vale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", backref="vales")

    def __repr__(self):
        return f"<Vale {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee.name if self.employee else None,
            "amount": self.amount,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def update_payroll(self):
        """Atualiza a folha de pagamento do funcionário após criar/atualizar vale"""
        from src.models.payroll import Payroll
        
        # Buscar folha de pagamento do mês/ano do vale
        month = self.date.month
        year = self.date.year
        
        payroll = Payroll.query.filter_by(
            employee_id=self.employee_id,
            month=month,
            year=year
        ).first()
        
        if not payroll:
            # Criar folha de pagamento se não existir
            from src.models.employee import Employee
            employee = Employee.query.get(self.employee_id)
            if employee:
                payroll = Payroll(
                    employee_id=self.employee_id,
                    month=month,
                    year=year,
                    base_salary=employee.salary or 0.0,
                    total_vales=0.0,
                    net_salary=employee.salary or 0.0
                )
                db.session.add(payroll)
        
        if payroll:
            # Atualizar total de vales na folha de pagamento
            payroll.update_vales_total()
            db.session.commit()
        
        return payroll


