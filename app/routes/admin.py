from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.models.user import User
from app.models.detection import EmailDetection
from app.models.model_metric import ModelMetric
from app.models.audit_log import AuditLog

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_detections = EmailDetection.query.count()
    phishing_count = EmailDetection.query.filter_by(prediction="phishing").count()
    legitimate_count = EmailDetection.query.filter_by(prediction="legitimate").count()
    suspicious_count = EmailDetection.query.filter_by(risk_level="Medium").count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_detections = EmailDetection.query.order_by(EmailDetection.created_at.desc()).limit(5).all()
    latest_metric = ModelMetric.query.order_by(ModelMetric.trained_at.desc()).first()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_detections=total_detections,
        phishing_count=phishing_count,
        legitimate_count=legitimate_count,
        suspicious_count=suspicious_count,
        recent_users=recent_users,
        recent_detections=recent_detections,
        latest_metric=latest_metric,
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template("admin/users.html", pagination=pagination, users=pagination.items)


@admin_bp.route("/detections")
@login_required
@admin_required
def detections():
    page = request.args.get("page", 1, type=int)
    pagination = EmailDetection.query.order_by(EmailDetection.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template("admin/detections.html", pagination=pagination, detections=pagination.items)


@admin_bp.route("/detections/<int:detection_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_detection(detection_id):
    detection = EmailDetection.query.get_or_404(detection_id)
    db.session.delete(detection)
    db.session.add(AuditLog(
        user_id=current_user.id,
        action="delete_detection",
        description=f"Admin deleted detection #{detection_id}",
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    flash("Detection record deleted.", "success")
    return redirect(url_for("admin.detections"))


@admin_bp.route("/audit-logs")
@login_required
@admin_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/audit_logs.html", pagination=pagination, logs=pagination.items)


@admin_bp.route("/model-metrics")
@login_required
@admin_required
def model_metrics():
    metrics = ModelMetric.query.order_by(ModelMetric.trained_at.desc()).all()
    return render_template("admin/model_metrics.html", metrics=metrics)
