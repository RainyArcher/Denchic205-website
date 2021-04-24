# Импортируем datetime для получения даты, sqlalchemy для работы с базой, db_session для работы с сессией
import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


# Класс комментариев, таблица с их данными
class Comments(SqlAlchemyBase, UserMixin):
    __tablename__ = 'comments'
    # Комментарий влкючает в себя свой id, текст, дату создания, id пользователя, id поста
    # В конце - отношение к таблицам Users и Posts
    date = str(datetime.datetime.now()).split('.')[0].split(' ')[0]
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=date)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    post_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("posts.id"))
    user = orm.relation('User')
    post = orm.relation('Posts')
