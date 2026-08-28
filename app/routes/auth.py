from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)


def _log_action(user_id, action, description):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        description=description,
        ip_address=request.remote_addr,
    )
    db.session.add(entry)
    db.session.commit()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
            return render_template("register.html", form=form)

        user = User(name=form.name.data.strip(), email=form.email.data.lower().strip(), role="user")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        _log_action(user.id, "register", f"New user registered: {user.email}")
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user is None or not user.check_password(form.password.data):
            _log_action(user.id if user else None, "login_failed", f"Failed login for {form.email.data}")
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        login_user(user)
        _log_action(user.id, "login", f"User logged in: {user.email}")
        flash(f"Welcome back, {user.name}!", "success")

        next_page = request.args.get("next")
        if user.is_admin:
            return redirect(next_page or url_for("admin.dashboard"))
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    _log_action(
        current_user.id,
        "logout",
        f"User logged out: {current_user.email}"
    )

    logout_user()

    return redirect(url_for("auth.login"))