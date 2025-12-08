
"""
DB Client
---------
Handles persistent DB connections and device info retrieval. All public methods are type hinted and include Google-style docstrings. Logging is included for major actions.
"""

import json
import os
from typing import Any, Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from decouple import config
from loguru import logger
from app.errors import ConfigNotFoundError, DatabaseError

# Database connection setup
try:
    DB_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    engine = create_engine(DB_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine and sessionmaker initialized.")
except Exception as e:
    logger.error(f"Failed to initialize database engine: {e}")
    raise DatabaseError(f"Failed to initialize database engine: {e}")

# config
DB_CLIENT_CONFIG_PATH = os.getenv('DB_CLIENT_CONFIG_PATH', os.path.join(os.path.dirname(__file__), '../../config/db_client_config.json'))

# Persistent session instance
_session = None

def get_session() -> Session:
    """
    Get a persistent SQLAlchemy session for database operations.

    Returns:
        Session: An active SQLAlchemy session.
    Raises:
        DatabaseError: If session creation fails.
    """
    global _session
    if _session is None:
        try:
            _session = SessionLocal()
            logger.info("Created new SQLAlchemy session.")
        except Exception as e:
            logger.error(f"Failed to create SQLAlchemy session: {e}")
            raise DatabaseError(f"Failed to create SQLAlchemy session: {e}")
    return _session

def get_device_info(search_value: Any) -> Optional[Dict[str, Any]]:
    """
    Retrieve device information from the configured database table and column.

    Uses the config/db_client_config.json file to determine which table and column to search for device info.

    Args:
        search_value (Any): The value to search for in the configured column.

    Returns:
        Optional[Dict[str, Any]]: The first matching device row as a dictionary, or None if not found.

    Raises:
        ConfigNotFoundError: If the config file or required fields are missing.
        DatabaseError: If a database error occurs.
    """
    try:
        if not os.path.exists(DB_CLIENT_CONFIG_PATH):
            logger.error(f"DB client config file not found: {DB_CLIENT_CONFIG_PATH}")
            raise ConfigNotFoundError(f"DB client config file not found: {DB_CLIENT_CONFIG_PATH}")
        with open(DB_CLIENT_CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
        table_name = cfg.get('table')
        search_column = cfg.get('search_column')
        if not table_name or not search_column:
            logger.error("Both 'table' and 'search_column' must be specified in db_client_config.json")
            raise ConfigNotFoundError("Both 'table' and 'search_column' must be specified in db_client_config.json")

        session = get_session()
        sql = f"SELECT * FROM {table_name} WHERE {search_column} = :search_value LIMIT 1"
        logger.info(f"Executing SQL: {sql} with search_value={search_value}")
        result = session.execute(sql, {"search_value": search_value})
        row = result.fetchone()
        if row:
            logger.success(f"Device found for {search_column}={search_value}")
            # Use row._mapping for SQLAlchemy 1.4+
            return dict(getattr(row, '_mapping', row))
        else:
            logger.warning(f"No device found for {search_column}={search_value}")
            return None
    except ConfigNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"Database error: {e}")