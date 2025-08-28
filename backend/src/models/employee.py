from src.models.user import db

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    role = db.Column(db.String(100))
    salary = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Employee {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cpf': self.cpf,
            'role': self.role,
            'salary': self.salary,
            'active': self.active
        }


