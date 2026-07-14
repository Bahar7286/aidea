"""Ensure missing columns exist for iterative MVP schema changes (SQLite + Postgres)."""

from sqlalchemy import text

from app.database import engine


def ensure_sqlite_columns() -> None:
    """Backward-compatible name — also migrates Postgres."""
    ensure_schema_columns()


def ensure_schema_columns() -> None:
    url = str(engine.url).lower()
    if url.startswith("sqlite"):
        _ensure_sqlite()
    elif "postgresql" in url or url.startswith("postgres"):
        _ensure_postgres()


def _ensure_sqlite() -> None:
    with engine.begin() as conn:
        cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()
        }
        if "phone" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(32)"))
        if "email_verified" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 1"
                )
            )
            conn.execute(text("UPDATE users SET email_verified = 1 WHERE email_verified IS NULL"))

        farm_cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(farms)")).fetchall()
        }
        if "is_active" not in farm_cols:
            conn.execute(
                text("ALTER TABLE farms ADD COLUMN is_active BOOLEAN DEFAULT 1")
            )
            conn.execute(text("UPDATE farms SET is_active = 1 WHERE is_active IS NULL"))
        if "latitude" not in farm_cols:
            conn.execute(text("ALTER TABLE farms ADD COLUMN latitude FLOAT"))
        if "longitude" not in farm_cols:
            conn.execute(text("ALTER TABLE farms ADD COLUMN longitude FLOAT"))

        try:
            device_cols = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(devices)")).fetchall()
            }
        except Exception:
            device_cols = set()
        device_alters = {
            "serial_number": "ALTER TABLE devices ADD COLUMN serial_number VARCHAR(80)",
            "zone_id": "ALTER TABLE devices ADD COLUMN zone_id INTEGER",
            "region_name": "ALTER TABLE devices ADD COLUMN region_name VARCHAR(120)",
            "depth_cm": "ALTER TABLE devices ADD COLUMN depth_cm INTEGER DEFAULT 20",
            "connection_type": "ALTER TABLE devices ADD COLUMN connection_type VARCHAR(40) DEFAULT 'wifi'",
            "battery_percent": "ALTER TABLE devices ADD COLUMN battery_percent FLOAT",
            "signal_dbm": "ALTER TABLE devices ADD COLUMN signal_dbm INTEGER",
            "firmware_version": "ALTER TABLE devices ADD COLUMN firmware_version VARCHAR(40)",
            "installed_at": "ALTER TABLE devices ADD COLUMN installed_at DATETIME",
            "last_calibration_at": "ALTER TABLE devices ADD COLUMN last_calibration_at DATETIME",
            "calibration_offset": "ALTER TABLE devices ADD COLUMN calibration_offset FLOAT DEFAULT 0",
            "sampling_minutes": "ALTER TABLE devices ADD COLUMN sampling_minutes INTEGER DEFAULT 15",
            "notes": "ALTER TABLE devices ADD COLUMN notes TEXT",
            "capabilities": "ALTER TABLE devices ADD COLUMN capabilities TEXT",
        }
        for col, sql in device_alters.items():
            if device_cols and col not in device_cols:
                conn.execute(text(sql))

        try:
            lab_cols = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(lab_reports)")).fetchall()
            }
        except Exception:
            lab_cols = set()
        if lab_cols:
            if "status" not in lab_cols:
                conn.execute(
                    text("ALTER TABLE lab_reports ADD COLUMN status VARCHAR(40) DEFAULT 'pending'")
                )
            if "extraction_confidence" not in lab_cols:
                conn.execute(
                    text("ALTER TABLE lab_reports ADD COLUMN extraction_confidence FLOAT")
                )

        try:
            lp_cols = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(lab_parameters)")).fetchall()
            }
        except Exception:
            lp_cols = set()
        if lp_cols and "confidence_pct" not in lp_cols:
            conn.execute(
                text("ALTER TABLE lab_parameters ADD COLUMN confidence_pct FLOAT")
            )

        try:
            user_cols = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()
            }
        except Exception:
            user_cols = set()
        if user_cols:
            if "is_active" not in user_cols:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
                )
                conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
            if "last_login_at" not in user_cols:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN last_login_at DATETIME")
                )
            if "subscription_plan" not in user_cols:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN subscription_plan VARCHAR(40) DEFAULT 'free'"
                    )
                )
                conn.execute(
                    text(
                        "UPDATE users SET subscription_plan = 'free' WHERE subscription_plan IS NULL"
                    )
                )

        try:
            reading_cols = {
                row[1]
                for row in conn.execute(
                    text("PRAGMA table_info(sensor_readings)")
                ).fetchall()
            }
        except Exception:
            reading_cols = set()
        reading_alters = {
            "zone_id": "ALTER TABLE sensor_readings ADD COLUMN zone_id INTEGER",
            "soil_moisture_deep": "ALTER TABLE sensor_readings ADD COLUMN soil_moisture_deep FLOAT",
            "moisture_depth_cm": "ALTER TABLE sensor_readings ADD COLUMN moisture_depth_cm FLOAT",
            "moisture_deep_depth_cm": "ALTER TABLE sensor_readings ADD COLUMN moisture_deep_depth_cm FLOAT",
            "device_id": "ALTER TABLE sensor_readings ADD COLUMN device_id INTEGER",
            "is_validated": "ALTER TABLE sensor_readings ADD COLUMN is_validated BOOLEAN DEFAULT 1",
        }
        for col, sql in reading_alters.items():
            if reading_cols and col not in reading_cols:
                conn.execute(text(sql))

        try:
            mat_use_cols = {
                row[1]
                for row in conn.execute(
                    text("PRAGMA table_info(farm_material_uses)")
                ).fetchall()
            }
        except Exception:
            mat_use_cols = set()
        if mat_use_cols:
            if "is_last_fertilizer" not in mat_use_cols:
                conn.execute(
                    text(
                        "ALTER TABLE farm_material_uses "
                        "ADD COLUMN is_last_fertilizer BOOLEAN DEFAULT 0"
                    )
                )
            if "is_last_pesticide" not in mat_use_cols:
                conn.execute(
                    text(
                        "ALTER TABLE farm_material_uses "
                        "ADD COLUMN is_last_pesticide BOOLEAN DEFAULT 0"
                    )
                )


def _ensure_postgres() -> None:
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION")
        )
        conn.execute(
            text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION")
        )
        conn.execute(
            text(
                "ALTER TABLE devices ADD COLUMN IF NOT EXISTS capabilities TEXT"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(40) DEFAULT 'free'"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE farm_material_uses "
                "ADD COLUMN IF NOT EXISTS is_last_fertilizer BOOLEAN DEFAULT FALSE"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE farm_material_uses "
                "ADD COLUMN IF NOT EXISTS is_last_pesticide BOOLEAN DEFAULT FALSE"
            )
        )
