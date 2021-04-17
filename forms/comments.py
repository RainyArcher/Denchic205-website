from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):
    text = StringField('Текст комментария', validators=[DataRequired()])
    submit = SubmitField('Применить')
