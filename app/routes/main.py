from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models.detection import EmailDetection
from app.services.ml_service import model_is_ready, get_model_metrics

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard")) if current_user.is_authenticated else redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    q = EmailDetection.query.filter_by(user_id=current_user.id)

    total = q.count()
    safe = q.filter_by(prediction="legitimate").count()
    phishing = q.filter_by(prediction="phishing").count()
    suspicious = q.filter_by(risk_level="Medium").count()

    recent = q.order_by(EmailDetection.created_at.desc()).limit(5).all()

    avg_confidence = db.session.query(db.func.avg(EmailDetection.confidence)).filter(
        EmailDetection.user_id == current_user.id
    ).scalar() or 0

    threat_percentage = round((phishing / total) * 100, 1) if total else 0

    metrics = get_model_metrics()

    return render_template(
        "dashboard.html",
        total=total,
        safe=safe,
        phishing=phishing,
        suspicious=suspicious,
        recent=recent,
        avg_confidence=round(avg_confidence * 100, 1),
        threat_percentage=threat_percentage,
        model_ready=model_is_ready(),
        metrics=metrics,
    )


@main_bp.route("/profile")
@login_required
def profile():
    total_detections = EmailDetection.query.filter_by(user_id=current_user.id).count()
    return render_template("profile.html", total_detections=total_detections)


@main_bp.route("/about")
def about():
    return render_template("about.html")
