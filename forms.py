from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email
from wtforms import StringField, SubmitField, IntegerField


# used to check the entries submitted on the contact us page are valid (called when form is submitted in app.py)
class ContactForm (FlaskForm):
    name = StringField("Name", validators=[DataRequired()])  # checks there is actual data being submitted
    email = StringField("Email", validators=[DataRequired(), Email()])  # checks there is actual data being submitted and that it is a valid email address
    message = StringField("Message", validators=[DataRequired()])  # checks there is actual data being submitted
    submit = SubmitField('Submit')
