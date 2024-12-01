from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField,TextAreaField,DateField,TimeField,SelectField,FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    phone_no = IntegerField("Phone Number", validators=[
        DataRequired(),
        NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 digits")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField("Register")
    
