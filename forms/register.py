from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, FileField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    avatar = FileField('Image File')
    address = StringField('Address', validators=[DataRequired()])
    role = SelectField('Role', choices=["User", "Admin", "Spectator"])
    submit = SubmitField('Submit')
