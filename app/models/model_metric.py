from datetime import datetime

from app import db


class ModelMetric(db.Model):
    __tablename__ = "model_metrics"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float)
    precision = db.Column("precision_score", db.Float)
    recall = db.Column("recall_score", db.Float)
    f1_score = db.Column(db.Float)
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ModelMetric {self.model_name} acc={self.accuracy}>"
