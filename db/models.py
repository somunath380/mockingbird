from sqlalchemy import Column, String, Integer, JSON, Boolean, ForeignKey, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Url(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    identifier = Column(String, index=True)
    filepath = Column(String, index=True)
    url = Column(String, index=True)
    method = Column(String, default='GET')
    body = Column(JSON, default={})
    response = Column(JSON, default={})
    headers = Column(JSON, default={})
    status_code = Column(Integer)
    execute = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_identifier", "identifier"),
        Index("idx_filepath", "filepath")
    )

    def __repr__(self) -> str:
        return f"Url({self.identifier})"

