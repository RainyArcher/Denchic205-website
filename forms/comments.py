from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


# Форма добавления комментария, включает в себя его текст и кнопку подтверждения
# Форма создана с помощью FlaskForm, включает в себя компоненты wtforms
class CommentsForm(FlaskForm):
    # Текст - обязательное поле
    text = TextAreaField('Comment text', validators=[DataRequired()])
    submit = SubmitField('Submit')
