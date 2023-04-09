from sqlalchemy import Column, String, Integer, JSON, Boolean, ForeignKey, Index
from sqlalchemy.orm import declarative_base, backref
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String) # Hash string value
    urls = relationship("Url", backref="users", cascade="delete")
    __table_args__ = (
        Index("idx_id", "id"),
        Index("idx_username", "username")
    )
    def __repr__(self) -> str:
        return f"User({self.username})"

class Url(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    identifier = Column(String, index=True)
    filepath = Column(String, index=True)
    url = Column(String)
    method = Column(String, default='GET')
    body = Column(JSON, default={})
    response = Column(JSON, default={'ping': 'pong'})
    headers = Column(JSON, default={})
    status_code = Column(Integer)
    execute = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_identifier", "identifier"),
        Index("idx_filepath", "filepath")
    )

    def __repr__(self) -> str:
        return f"Url({self.identifier})"

