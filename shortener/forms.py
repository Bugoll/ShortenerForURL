from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, URL
from shortener.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username.')
        
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password1 = PasswordField('Password:', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Create Account')


class ShortenLinkForm(FlaskForm):
    destination_link = StringField('Destination Link:', validators=[DataRequired(), URL()], render_kw={"placeholder": "Enter long URL"})
    shortened_link = StringField('Shortened Link:', render_kw={"readonly": True})  # Поле для сокращенной ссылки
    submit = SubmitField('Cut Link')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class PersonalShortenLinkForm(FlaskForm):
    personaldestination_link = StringField('PersonalDestination Link:', validators=[DataRequired(), URL()], render_kw={"placeholder": "Enter long URL"})
    personalshortened_link = StringField('PersonalShortened Link:', render_kw={"readonly": True})  # Поле для сокращенной ссылки
    submit = SubmitField('Cut Link')

