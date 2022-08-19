from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from models import User


# used to check the entries submitted on the contact us page are valid (called when form is submitted in app.py)
class ContactForm (FlaskForm):
    name = StringField("Name", validators=[DataRequired()])  # checks there is actual data being submitted
    email = StringField("Email", validators=[DataRequired(), Email()])  # checks there is actual data being submitted and that it is a valid email address
    message = StringField("Message", validators=[DataRequired()])  # checks there is actual data being submitted
    submit = SubmitField('Submit')


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
