# Импортируем datetime для получения даты, sqlalchemy для работы с базой, db_session для работы с сессией
import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


# Класс постов, таблица с их данными
class Posts(SqlAlchemyBase, UserMixin):
    __tablename__ = 'posts'
    # Пост влкючает в себя свой id, тип, заголовок, описание, изображение, приватность, дату создания, id пользователя
    # В конце - отношение к таблицам Users и Comments (комментарии этого поста)
    date = str(datetime.datetime.now()).split('.')[0].split(' ')[0]
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=date)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    comments = orm.relation("Comments", back_populates='post')
