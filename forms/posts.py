from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class PostsForm(FlaskForm):
    # Форма добавления поста, включает в себя его тип, заголовок, описание, картинку и является ли он приватным
    # Форма создана с помощью FlaskForm, включает в себя компоненты wtforms
    # заголовок - обязательные поля
    type = SelectField('Post type', choices=["None", "Life", "Programming", "Gaming", "Arting"])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField("Content")
    image = FileField('Image File')
    is_private = BooleanField("Private")
    submit = SubmitField('Submit')
