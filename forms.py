from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from models import User


# used to check the entries submitted on the contact us page are valid (called when form is submitted in app.py)
class ContactForm (FlaskForm):
    name = StringField("Name", validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Name"})  # checks there is actual data being submitted
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"class": "form-control", "placeholder": "Email"})  # checks there is actual data being submitted and that it is a valid email address
    message = TextAreaField("Message", validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Message to send"})  # checks there is actual data being submitted
    submit = SubmitField('Submit', render_kw={"class": "btn btn-primary"})


class RegistrationForm(FlaskForm):
    email_address = StringField("Email Address (Username)", validators=[DataRequired(), Email()])
    name = StringField("Full Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_email_address(self, email_address_to_register):
        user = User.query.filter_by(email_address=email_address_to_register.data).first()
        if user is not None:
            raise ValidationError("Please Use a Different Email Address)")


class LoginForm(FlaskForm):
    email_address = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
