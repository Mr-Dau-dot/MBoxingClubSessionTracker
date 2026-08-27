from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = EmailField(label="Email",validators=[DataRequired(),Email()])
    password = PasswordField(label="Password",validators=[DataRequired()])
    submit = SubmitField("Let's Box")

class RegisterForm(FlaskForm):
    name = StringField(label="Name",validators=[DataRequired()])
    email = EmailField(label="Email",validators=[DataRequired(),Email()])
    password = PasswordField(label="Password",validators=[DataRequired(),Length(min=8)])
    phone = StringField(label="Your phone number",validators=[DataRequired()])
    submit = SubmitField("Join the club")


class SessionForm(FlaskForm):
    date = DateField(label="Date",validators=[DataRequired()])
    start_time = TimeField(label="Start",validators=[DataRequired()])
    end_time = TimeField(label="Finish",validators=[DataRequired()])
    session_type = StringField(label="Type")
    notes = StringField(label="Notes")
    member_id = SelectField(label="Member",coerce=int,choices=[],validators=[DataRequired()])
    submit = SubmitField("Member confirm")