from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, FileField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    # Форма настроек пользователя, включает в себя его email, старый и новый пароль (при изменении), фамилию, имя,
    # возраст, аватар, адрес, роль
    # Форма также считывает данные с базы перед их изменением
    # Форма создана с помощью FlaskForm, включает в себя компоненты wtforms
    # Все поля, кроме роли (так как в любом случае роль будет заполнена) и аватара - обязательные для заполнения
    email = EmailField('Login / email', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    role = SelectField('Role', choices=["User", "Spectator", "Admin"])
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password')
    avatar = FileField('Image File')
    submit = SubmitField('Submit')
