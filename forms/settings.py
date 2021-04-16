from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password')
    avatar = FileField('Image File')
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')
