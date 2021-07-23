import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app import config

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    # pool_pre_ping=True,
    # pool_size=20,
    # max_overflow=60,
    # pool_timeout=2,
)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=True, bind=engine)
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def SessionManager():
    session = Session()
    try:
        yield session
    except:
        logging.error("auto-rollbacking...")
        session.rollback()
        raise
    finally:
        session.close()
