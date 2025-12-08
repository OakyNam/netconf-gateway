"""
SQLAlchemy models for router table.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Router(Base):
    __tablename__ = 'router'
    id = Column(Integer, primary_key=True)
    vendor = Column(String)
    chassis = Column(String)
    owner = Column(String)
    region = Column(String)
    router = Column(String)  # This is the hostname
    port = Column(Integer)
    type = Column(String)
    software = Column(String)
