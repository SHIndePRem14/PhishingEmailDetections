"""Loads the trained TF-IDF + Logistic Regression phishing model once and
exposes a simple predict_email() function used by the detection route.

The model is never retrained on a per-request basis -- train_model.py is
the only place training happens.
"""

import json
import os

import joblib
from flask import current_app

from app.services.text_preprocessing import clean_text

_model = None
_vectorizer = None
_model_name = "phishing_model.pkl"


class ModelNotFoundError(Exception):
    pass


def _load(app=None):
    global _model, _vectorizer
    cfg = current_app.config if app is None else app.config

    model_path = cfg["ML_MODEL_PATH"]
    vectorizer_path = cfg["ML_VECTORIZER_PATH"]

    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        raise ModelNotFoundError(
            "Trained model not found. Run: python scripts/train_model.py"
        )

    _model = joblib.load(model_path)
    _vectorizer = joblib.load(vectorizer_path)


def _risk_level(prediction, confidence):
    if prediction == "phishing":
        return "High" if confidence >= 0.75 else "Medium"
    return "Low" if confidence >= 0.6 else "Medium"


def predict_email(text):
    """Return {"prediction": ..., "confidence": ..., "risk_level": ...}."""
    global _model, _vectorizer

    if _model is None or _vectorizer is None:
        _load()

    cleaned = clean_text(text)
    features = _vectorizer.transform([cleaned])

    prediction = _model.predict(features)[0]
    proba = _model.predict_proba(features)[0]
    class_index = list(_model.classes_).index(prediction)
    confidence = float(proba[class_index])

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "risk_level": _risk_level(prediction, confidence),
        "model_name": _model_name,
    }


def get_model_metrics():
    metrics_path = current_app.config["ML_METRICS_PATH"]
    if not os.path.exists(metrics_path):
        return None
    with open(metrics_path, "r") as f:
        return json.load(f)


def model_is_ready():
    cfg = current_app.config
    return os.path.exists(cfg["ML_MODEL_PATH"]) and os.path.exists(cfg["ML_VECTORIZER_PATH"])
