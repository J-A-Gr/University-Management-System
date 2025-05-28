from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, EmailField,
RadioField, DateField, SelectField, IntegerField)
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo, ValidationError
from app.models.user import User
from app.utils.validators import StrongPassword
import datetime


class LoginForm(FlaskForm):
    email = EmailField('Email address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    role = RadioField('Role', choices=[
                        ('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    birthday = DateField('Birth date', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), StrongPassword()])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), StrongPassword(), 
        EqualTo('password', message='Passwords must match')
    ])
    profile_picture = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

    study_program = SelectField('Studijų programa', choices=[], coerce=int)
    admission_year = IntegerField('Įstojimo metai', validators=[
    DataRequired(),
    NumberRange(min=1900, max=datetime.datetime.now().year, message="Įveskite tinkamus metus.")
    ])

    group_letter = StringField('Grupės raidė', validators=[
    DataRequired(),
    Length(min=1, max=10, message="Grupės raidė turi būti 1-10 simbolių")
    ])

    submit = SubmitField('Register')
    

    # Flask-WTF automatically calls custom validators during form.validate_on_submit()
    # Any method named validate_<fieldname> gets executed after built-in validators pass
    # If ValidationError is raised, form validation fails and error shows in template
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
