from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.models.detection import EmailDetection
from app.models.audit_log import AuditLog
from app.forms import AnalyzeEmailForm
from app.services.ml_service import predict_email, ModelNotFoundError
from app.services.keyword_service import detect_keywords
from app.services.url_service import detect_suspicious_urls

detection_bp = Blueprint("detection", __name__)


@detection_bp.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    form = AnalyzeEmailForm()

    if form.validate_on_submit():
        full_text = " ".join(
            filter(None, [form.subject.data, form.email_body.data])
        )

        try:
            result = predict_email(full_text)
        except ModelNotFoundError as e:
            flash(str(e), "danger")
            return render_template("analyze.html", form=form)

        matched_keywords, keyword_score = detect_keywords(full_text)
        suspicious_urls, all_urls = detect_suspicious_urls(form.email_body.data)

        detection = EmailDetection(
            user_id=current_user.id,
            sender_email=form.sender_email.data,
            receiver_email=form.receiver_email.data,
            subject=form.subject.data,
            email_body=form.email_body.data,
            prediction=result["prediction"],
            confidence=result["confidence"],
            risk_level=result["risk_level"],
            suspicious_keywords=",".join(matched_keywords),
            suspicious_urls=",".join(suspicious_urls),
            model_name=result["model_name"],
        )
        db.session.add(detection)

        db.session.add(AuditLog(
            user_id=current_user.id,
            action="analyze_email",
            description=f"Analyzed email -> {result['prediction']} ({result['confidence']*100:.1f}%)",
            ip_address=request.remote_addr,
        ))
        db.session.commit()

        return redirect(url_for("detection.result", detection_id=detection.id))

    return render_template("analyze.html", form=form)


@detection_bp.route("/detection/<int:detection_id>")
@login_required
def result(detection_id):
    detection = EmailDetection.query.get_or_404(detection_id)
    if detection.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("result.html", detection=detection)


# Alias to match the spec's /detection/<id> "details" naming.
@detection_bp.route("/detection/<int:detection_id>/details")
@login_required
def details(detection_id):
    return redirect(url_for("detection.result", detection_id=detection_id))


@detection_bp.route("/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "", type=str).strip()
    prediction_filter = request.args.get("prediction", "", type=str)

    query = EmailDetection.query.filter_by(user_id=current_user.id)

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                EmailDetection.subject.ilike(like),
                EmailDetection.sender_email.ilike(like),
            )
        )

    if prediction_filter in ("phishing", "legitimate"):
        query = query.filter_by(prediction=prediction_filter)

    query = query.order_by(EmailDetection.created_at.desc())

    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "history.html",
        pagination=pagination,
        detections=pagination.items,
        search=search,
        prediction_filter=prediction_filter,
    )
