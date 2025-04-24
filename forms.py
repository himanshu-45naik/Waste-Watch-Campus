from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('User Type', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('cleaning_staff', 'Cleaning Staff')
    ], validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different one or login.')

class ReportForm(FlaskForm):
    title = StringField('Report Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    severity = SelectField('Severity', choices=[
        ('Unknown', 'Unknown (AI will assess)'),
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ], validators=[DataRequired()])
    image1 = FileField('Image 1', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    image2 = FileField('Image 2', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    image3 = FileField('Image 3', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    image4 = FileField('Image 4', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    image5 = FileField('Image 5', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Submit Report')
