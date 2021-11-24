from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flask_sqlalchemy import SQLAlchemy, declarative_base

Base = declarative_base()
db = SQLAlchemy(model_class=Base)

metadata = Base.metadata


def get_db_session(db_url):
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
