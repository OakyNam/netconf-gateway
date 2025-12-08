"""
Database client for accessing router info.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Router, Base
from decouple import config


DB_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Persistent session instance
_session = None

def get_session():
    global _session
    if _session is None:
        _session = SessionLocal()
    return _session


def get_router_by_hostname(hostname):
    session = get_session()
    router = session.query(Router).filter(Router.router == hostname).first()
    return router

def get_table_as_dicts(table_model):
    """
    Reads all rows from the given SQLAlchemy model (table) and returns a list of dicts with column names as keys.
    Usage: get_table_as_dicts(Router)
    """
    session = get_session()
    row = session.query(table_model).first()
    if row:
        columns = row.__table__.columns.keys()
        return columns