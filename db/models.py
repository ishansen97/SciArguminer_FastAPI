from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text

Base = declarative_base()

class SampleHistory(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    paper = Column(String)
    date = Column(DateTime)
    authors = Column(String)

class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    paper = Column(String)
    authors = Column(String)
    created = Column(DateTime)
    structure = Column(Text)