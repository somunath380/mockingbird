from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from sanic.log import logger
from typing import Text

def create_db_uri():
    """Creates database uri using environment variables.
    Args:
        **kwargs: dict.
    Returns:
        db_url: text.
    """
    user: Text = os.environ.get("DB_USER")
    password: Text = os.environ.get("DB_PASSWORD")
    host: Text = os.environ.get("DB_HOST")
    db: Text = os.environ.get("DB_NAME")
    port: int = os.environ.get("DB_PORT")
    logger.info({
        "user": user,
        "password": password,
        "host": host,
        "database": db,
        "port": port
    })
    db_uri: Text = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return db_uri


db_uri: Text = create_db_uri()


engine: object = create_engine(db_uri, pool_size=10, max_overflow=10)


def get_session():
    """Creates database session"""
    Session = sessionmaker(bind=engine)
    return Session()



