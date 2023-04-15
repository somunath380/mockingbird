from db.connection import engine
from db.models import Base
from sqlalchemy import inspect
from db.connection import get_session
from sanic.log import logger

inspector = inspect(engine)

async def check_or_create_tables(**kwargs):
    """Connects to the database and Checks if the tables are created or not. \
        if tables are not created then it creates the tables.
        
    Args:
        **kwargs (dict): keyword arguments.
    
    Returns:
        None."""
    logger.info("checking presense of urls table...")
    try:
        if inspector.has_table("urls"):
            logger.info("urls table already present")
            return
        else:
            logger.info("urls table not present...creating table...")
            Base.metadata.create_all(engine)
            logger.info("all tables created successfully")
    except Exception as exe:
        logger.error(f"exception occured while creating tables -> {exe}")


async def close_all_db_sessions(**kwargs):
    """Closes db session before closing stopping the server.
    
    Args:
        **kwargs (dict): keyword arguments.
        
    Returns:
        None."""
    logger.info("closing all db sessions")
    try:
        session = get_session()
        session.close_all()
        logger.info("all db sessions closed")
    except Exception as exe:
        logger.error(f"error while closing db sessions -> {exe}")
