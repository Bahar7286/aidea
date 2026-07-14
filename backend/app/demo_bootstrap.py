"""Upsert demo users for production (Supabase) when SEED_DEMO_USERS is set."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal

logger = logging.getLogger(__name__)


def should_seed_demo_users() -> bool:
    flag = (settings.seed_demo_users or "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return True
    if flag in {"0", "false", "no", "off"}:
        return False
    # Auto on non-SQLite (hosted Postgres) so Render demos work without a shell.
    return not str(settings.database_url).lower().startswith("sqlite")


def seed_demo_users(db: Session | None = None) -> list[str]:
    """Upsert four demo accounts with distinct persona farm data."""
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    if str(scripts_dir.parent) not in sys.path:
        sys.path.insert(0, str(scripts_dir.parent))

    from scripts.seed_demo import run_seed  # type: ignore

    own = db is None
    session = db or SessionLocal()
    emails: list[str] = []
    try:
        result = run_seed(session)
        emails = list(result.keys())
        session.commit()
        logger.info("Demo users upserted: %s", ", ".join(emails))
    except Exception:
        session.rollback()
        logger.exception("Demo user seed failed")
        raise
    finally:
        if own:
            session.close()
    return emails


def maybe_seed_on_startup() -> None:
    if not should_seed_demo_users():
        return
    try:
        seed_demo_users()
    except Exception:
        logger.exception("Startup demo seed skipped after error")


def ensure_catalog_on_startup() -> None:
    """Always seed educational agro reference catalog (idempotent)."""
    from app.agro_catalog import ensure_agro_catalog

    session = SessionLocal()
    try:
        n = ensure_agro_catalog(session)
        session.commit()
        logger.info("Agro catalog ensured (%s entries)", n)
    except Exception:
        session.rollback()
        logger.exception("Agro catalog seed failed")
    finally:
        session.close()
