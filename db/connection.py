from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_uri = 'postgresql+psycopg2://somu:mypwd@postgres:5432/mockdb'

engine = create_engine(db_uri, pool_size=10, max_overflow=10)

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()



