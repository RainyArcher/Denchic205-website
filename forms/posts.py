from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class PostsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    image = FileField('Image File')
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
