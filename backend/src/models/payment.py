from src.models.user import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255))

    employee = db.relationship("Employee", backref="payments")

    def __repr__(self):
        return f"<Payment {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "amount": self.amount,
            "date": self.date,
            "description": self.description,
        }


