from datetime import timedelta, datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, Email, Length, Optional
from helpers import time_choices

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
    start_time = SelectField(label="Start Time", choices=time_choices, validators=[DataRequired()])
    duration = SelectField("Duration", validators=[DataRequired()], coerce=int,
                           choices=[(30,"30 minutes"),(60, "60 minutes"), (90,"90 minutes"), (120,"120 minutes")], default=60)
    # end_time = TimeField(label="Finish",validators=[DataRequired()])
    session_type = StringField(label="Type")
    notes = StringField(label="Notes")
    member_id = SelectField(label="Member",coerce=int,choices=[],validators=[DataRequired()])
    coach_id = SelectField(label="Coach",coerce=int,choices=[],validators=[Optional()])
    package = SelectField(label="Package",coerce=int,choices=[],validators=[DataRequired()])
    submit = SubmitField("Member confirm")

class PackageForm(FlaskForm):
    date = DateField(label="Starting Date", validators=[DataRequired()])
    name = SelectField(label="Package Name",validators=[DataRequired()], coerce=int,
                        choices=[(1,"Beginners"),(2,"Boxer"), (3,"Warrior"),(4,"Walk in")])
    member_id = SelectField(label="Member",coerce=int,choices=[],validators=[DataRequired()])
    coach_id = SelectField(label="Coach",coerce=int,choices=[],validators=[Optional()])
    submit = SubmitField("Activate")