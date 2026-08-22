from datetime import datetime

from app import db


class EmailDetection(db.Model):
    __tablename__ = "email_detections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    sender_email = db.Column(db.String(255))
    receiver_email = db.Column(db.String(255))
    subject = db.Column(db.String(500))
    email_body = db.Column(db.Text, nullable=False)

    prediction = db.Column(db.String(20), nullable=False)  # phishing / legitimate
    confidence = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # Low / Medium / High

    suspicious_keywords = db.Column(db.Text)  # comma-separated
    suspicious_urls = db.Column(db.Text)  # comma-separated

    model_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def keyword_list(self):
        return [k for k in (self.suspicious_keywords or "").split(",") if k]

    def url_list(self):
        return [u for u in (self.suspicious_urls or "").split(",") if u]

    def __repr__(self):
        return f"<EmailDetection {self.id} {self.prediction}>"
