from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class PostsForm(FlaskForm):
    type = SelectField('Post type', choices=["None", "Life", "Programming", "Gaming", "Arting"])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField("Content")
    image = FileField('Image File')
    is_private = BooleanField("Private")
    submit = SubmitField('Submit')
