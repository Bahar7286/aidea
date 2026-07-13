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
    """Upsert the four demo accounts (+ Domates Serası for farmer)."""
    # Prefer importing the same logic as scripts.seed_demo
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    if str(scripts_dir.parent) not in sys.path:
        sys.path.insert(0, str(scripts_dir.parent))

    from scripts.seed_demo import (  # type: ignore
        DEMO_USERS,
        seed_farmer_farm,
        seed_light_farm,
        seed_ticket,
        upsert_user,
    )

    own = db is None
    session = db or SessionLocal()
    emails: list[str] = []
    try:
        for spec in DEMO_USERS:
            user = upsert_user(session, spec)
            if spec.get("seed_farm"):
                farm = seed_farmer_farm(session, user)
                seed_ticket(session, user, farm)
            if spec.get("seed_farm_light"):
                seed_light_farm(session, user)
            emails.append(user.email)
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
