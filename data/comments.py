import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'
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
