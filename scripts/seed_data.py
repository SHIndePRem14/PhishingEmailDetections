"""Seeds the database with demonstration data: sample users, detections,
and a sample model-metrics row. All records are clearly demo data.

Usage:
    python scripts/seed_data.py
"""

import os
import sys
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app import create_app, db  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.detection import EmailDetection  # noqa: E402
from app.models.model_metric import ModelMetric  # noqa: E402

SAMPLE_USERS = [
    {"name": "Demo User One", "email": "demo.user1@example.com", "role": "user"},
    {"name": "Demo User Two", "email": "demo.user2@example.com", "role": "user"},
]

SAMPLE_DETECTIONS = [
    {
        "subject": "[DEMO] Verify your account now",
        "body": "Your account has been suspended. Click here to verify your identity immediately.",
        "prediction": "phishing",
        "confidence": 0.94,
        "risk_level": "High",
        "keywords": "verify your account,click here,account suspended",
        "urls": "http://192.168.1.1/verify",
    },
    {
        "subject": "[DEMO] Meeting notes attached",
        "body": "Hi team, please find attached the notes from today's sync meeting.",
        "prediction": "legitimate",
        "confidence": 0.91,
        "risk_level": "Low",
        "keywords": "",
        "urls": "",
    },
    {
        "subject": "[DEMO] Claim your prize",
        "body": "Congratulations! Claim reward now, limited time offer, click here.",
        "prediction": "phishing",
        "confidence": 0.88,
        "risk_level": "High",
        "keywords": "congratulations,claim reward,limited time,click here",
        "urls": "http://bit.ly/claim-now",
    },
]


def main():
    app = create_app(os.environ.get("FLASK_ENV", "development"))

    with app.app_context():
        demo_password = "DemoPass123!"

        users = []
        for u in SAMPLE_USERS:
            existing = User.query.filter_by(email=u["email"]).first()
            if existing:
                users.append(existing)
                continue
            user = User(name=u["name"], email=u["email"], role=u["role"])
            user.set_password(demo_password)
            db.session.add(user)
            users.append(user)
        db.session.commit()

        for i, d in enumerate(SAMPLE_DETECTIONS):
            detection = EmailDetection(
                user_id=users[i % len(users)].id,
                sender_email="sample-sender@example.com",
                receiver_email=users[i % len(users)].email,
                subject=d["subject"],
                email_body=d["body"],
                prediction=d["prediction"],
                confidence=d["confidence"],
                risk_level=d["risk_level"],
                suspicious_keywords=d["keywords"],
                suspicious_urls=d["urls"],
                model_name="phishing_model.pkl",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10)),
            )
            db.session.add(detection)

        if not ModelMetric.query.first():
            db.session.add(ModelMetric(
                model_name="phishing_model.pkl (demo seed)",
                accuracy=0.93,
                precision=0.91,
                recall=0.90,
                f1_score=0.905,
            ))

        db.session.commit()
        print("Seed data created.")
        print(f"Demo users: {[u['email'] for u in SAMPLE_USERS]} (password: {demo_password})")
        print("NOTE: this is demonstration data only.")


if __name__ == "__main__":
    main()
