import pytest

from app.services import ml_service


def test_model_not_ready_raises(app):
    with app.app_context():
        ml_service._model = None
        ml_service._vectorizer = None
        app.config["ML_MODEL_PATH"] = "/nonexistent/model.pkl"
        app.config["ML_VECTORIZER_PATH"] = "/nonexistent/vectorizer.pkl"
        with pytest.raises(ml_service.ModelNotFoundError):
            ml_service.predict_email("test email body")


def test_model_is_ready_false_when_missing(app):
    with app.app_context():
        app.config["ML_MODEL_PATH"] = "/nonexistent/model.pkl"
        app.config["ML_VECTORIZER_PATH"] = "/nonexistent/vectorizer.pkl"
        assert ml_service.model_is_ready() is False
