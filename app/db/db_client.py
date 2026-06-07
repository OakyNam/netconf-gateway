"""
DB client utilities for device metadata lookup.
"""

import json
import os
import re
from typing import Any, Dict, Optional

from decouple import config
from loguru import logger
from sqlalchemy import bindparam, column, create_engine, select, table
from sqlalchemy.orm import Session, sessionmaker

from app.errors import ConfigNotFoundError, DatabaseError

def _resolve_config_path() -> str:
    configured = os.getenv(
        "DB_CLIENT_CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), "../../config/db_client_config.json"),
    )
    if os.path.exists(configured):
        return configured
    return configured.replace("db_client_config.json", "db_client_config.example.json")


DB_CLIENT_CONFIG_PATH = _resolve_config_path()


def _validate_identifier(name: str, label: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ConfigNotFoundError(f"Invalid {label} in DB config: {name}")
    return name


_engine = None
_session_factory = None
_session = None


def _get_db_url() -> str:
    return (
        f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}"
        f"@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )


def _ensure_session_factory() -> None:
    global _engine, _session_factory
    if _session_factory is not None:
        return
    try:
        _engine = create_engine(_get_db_url(), pool_pre_ping=True)
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        logger.info("Database engine initialized")
    except Exception as exc:
        logger.error(f"Failed to initialize database engine: {exc}")
        raise DatabaseError(f"Failed to initialize database engine: {exc}")


def get_session() -> Session:
    global _session
    _ensure_session_factory()
    if _session is None:
        try:
            _session = _session_factory()
        except Exception as exc:
            logger.error(f"Failed to create SQLAlchemy session: {exc}")
            raise DatabaseError(f"Failed to create SQLAlchemy session: {exc}")
    return _session


def get_device_info(search_value: Any) -> Optional[Dict[str, Any]]:
    try:
        if not os.path.exists(DB_CLIENT_CONFIG_PATH):
            raise ConfigNotFoundError(f"DB client config file not found: {DB_CLIENT_CONFIG_PATH}")

        with open(DB_CLIENT_CONFIG_PATH, "r", encoding="utf-8") as file:
            cfg = json.load(file)

        table_name = _validate_identifier(str(cfg.get("table", "")), "table")
        search_column = _validate_identifier(str(cfg.get("search_column", "")), "search_column")
        session = get_session()
        db_table = table(table_name)
        db_column = column(search_column)
        query = (
            select(db_table)
            .where(db_column == bindparam("search_value"))
            .select_from(db_table)
            .limit(1)
        )
        result = session.execute(query, {"search_value": search_value})
        row = result.fetchone()
        return dict(getattr(row, "_mapping", row)) if row else None
    except ConfigNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Database error during device lookup: {exc}")
        raise DatabaseError(f"Database error: {exc}")
