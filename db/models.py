from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()

class SampleHistory(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    paper = Column(String)
    date = Column(DateTime)
    authors = Column(String)
