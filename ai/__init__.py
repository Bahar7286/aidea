"""AI package for AgriTwin — datasets and rule engine."""

from pathlib import Path

DATASETS_DIR = Path(__file__).parent / "datasets"


def list_scenarios() -> list[str]:
    return sorted(p.stem for p in DATASETS_DIR.glob("*.json"))
