from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):
    text = TextAreaField('Comment text', validators=[DataRequired()])
    submit = SubmitField('Submit')
