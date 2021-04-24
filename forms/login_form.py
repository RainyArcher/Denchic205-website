from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


# Форма входа на сайт для пользователя, включает в себя считывание его email'а, пароля, нужно ли запоминать пользвателя
# Форма создана с помощью FlaskForm, включает в себя компоненты wtforms
# Форма также нужна для удаления пользователя при подтвержении данных
class LoginForm(FlaskForm):
    # email и пароль - обязательные поля
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')
