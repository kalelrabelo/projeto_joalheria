from src.models.user import db
from datetime import datetime

class ReportHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    command = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<ReportHistory {self.filename}>"


