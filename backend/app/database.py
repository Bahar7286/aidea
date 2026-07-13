from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# Prisma / Supabase pooler helpers — invalid for psycopg2/libpq DSN
_UNSUPPORTED_DB_QUERY_PARAMS = frozenset(
    {
        "pgbouncer",
        "connection_limit",
        "pool_timeout",
        "schema",
        "preparethreshold",
        "statement_cache_size",
    }
)


def sanitize_database_url(url: str) -> str:
    """Strip client-helper query params that break psycopg2 (e.g. pgbouncer=true)."""
    if not url or url.startswith("sqlite"):
        return url
    parsed = urlparse(url)
    if not parsed.query:
        return url
    kept = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _UNSUPPORTED_DB_QUERY_PARAMS
    ]
    return urlunparse(parsed._replace(query=urlencode(kept)))


database_url = sanitize_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
