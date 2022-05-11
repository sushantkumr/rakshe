from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from lib.core import config

configuration = config.get_config()

engine = create_engine(configuration['connection_string'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    '''Create DB with all tables.'''
    Base.metadata.create_all(bind=engine)
