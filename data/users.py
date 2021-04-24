# Импортируем datetime для получения даты, sqlalchemy для работы с базой, db_session для работы с сессией
# werkzeug.security для генерации пароля (безопасность)
import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


# Класс пользователей, таблица с их данными
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    # Пользователь влкючает в себя свой id, фамилию, имя возраст, адрес, аватар, email, роль, пароль, дату изменения
    # В конце - отношение к таблицам Posts (посты этого пользователя) и Comments (комментарии этого пользователя)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String, default="User")
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    posts = orm.relation("Posts", back_populates='user')
    comments = orm.relation('Comments', back_populates="user", lazy='subquery')

    # Функция установки зашифрованного пароля
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # Функция проверки пароля на совпадение с расшифрованным текущим
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
