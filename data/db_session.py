# Импортируем sqlalchemy для работы с базой данных
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
# Файл сессии, необходим для работы сайта и взаимодействия с данными и пользвателями
SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("You need to enter a name of your database.")
    # Подключение к базе, если указано её имя
    conn_str = 'sqlite:///' + db_file.strip()
    print(f"Connecting database {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, connect_args={'check_same_thread': False}
)
    __factory = orm.sessionmaker(bind=engine)
    # Подключаем все модели
    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
