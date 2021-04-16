from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class PostsForm(FlaskForm):
    type = SelectField('Тип поста', choices=["None", "Life", "Programming", "Gaming", "Arting"])
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    image = FileField('Image File')
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
