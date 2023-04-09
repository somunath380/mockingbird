from db.connection import engine
from db.models import Base
from sqlalchemy import inspect
from sanic.log import logger
from db.connection import get_session
inspector = inspect(engine)

async def check_or_create_tables():
    logger.info("checking presense of users and urls table...")
    try:
        if inspector.has_table("users") and inspector.has_table("urls"):
            logger.info("users and urls already present")
            return
        else:
            logger.info("users and urls not present...creating..")
            Base.metadata.create_all(engine)
            logger.info("all tables created successfully")
    except Exception as exe:
        logger.info(f"exception occured while creating tables -> {exe}")


async def close_all_db_sessions():
    logger.info("closing all db sessions")
    try:
        session = get_session()
        session.close_all()
        logger.info("all db sessions closed")
    except Exception as exe:
        logger.info(f"error while closing db sessions -> {exe}")
