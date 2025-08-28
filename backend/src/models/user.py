from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

    @staticmethod
    def create_admin(username, password):
        hashed_password = generate_password_hash(password)
        admin_user = User(username=username, email=f'{username}@example.com', password_hash=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        return admin_user

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


