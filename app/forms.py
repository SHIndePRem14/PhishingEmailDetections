from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AnalyzeEmailForm(FlaskForm):
    sender_email = StringField("Sender Email", validators=[Optional(), Length(max=255)])
    receiver_email = StringField("Receiver Email", validators=[Optional(), Length(max=255)])
    subject = StringField("Subject", validators=[Optional(), Length(max=500)])
    email_body = TextAreaField("Email Body", validators=[DataRequired(message="Email body cannot be empty")])
    submit = SubmitField("Analyze Email")
