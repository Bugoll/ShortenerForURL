from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password1 = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Create Account')
