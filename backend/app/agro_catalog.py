"""Reference agro-material catalog (TR tomato greenhouse / open-field oriented).

Educational classes only — not brand labels, not dose prescriptions.
Primary source: backend/ai/datasets/agro_materials.json (expandable).
Sources summarized in FERTILIZER_PESTICIDE_CATALOG.md at repo root.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_DATASET_PATH = Path(__file__).resolve().parents[1] / "ai" / "datasets" / "agro_materials.json"

# JSON category → DB kind
_KIND_MAP = {
    "fertilizer": "fertilizer",
    "pesticide": "plant_protection",
    "plant_protection": "plant_protection",
}


@dataclass(frozen=True)
class CatalogItem:
    code: str
    kind: str  # fertilizer | plant_protection
    name_tr: str
    name_en: str
    category: str
    nutrient_focus: str | None
    purpose: str
    ec_salinity_note: str | None
    phi_class_note: str | None
    irrigation_context: str | None
    sort_order: int = 100


def _item_from_json(raw: dict) -> CatalogItem:
    cat = str(raw.get("category") or "fertilizer").strip().lower()
    kind = _KIND_MAP.get(cat, "fertilizer")
    code = str(raw.get("id") or raw.get("code") or "").strip()
    if not code:
        raise ValueError("catalog item missing id/code")
    subcategory = str(raw.get("subcategory") or raw.get("class") or cat).strip()
    notes = raw.get("notes")
    notes_str = str(notes).strip() if notes else None
    # Pesticides: notes → PHI; fertilizers: notes → EC/salinity
    if kind == "plant_protection":
        phi = notes_str
        ec = None
    else:
        ec = notes_str
        phi = None
    return CatalogItem(
        code=code,
        kind=kind,
        name_tr=str(raw["name_tr"]),
        name_en=str(raw.get("name_en") or raw["name_tr"]),
        category=subcategory,
        nutrient_focus=(
            str(raw["nutrient_focus"]) if raw.get("nutrient_focus") else None
        ),
        purpose=str(raw.get("purpose") or ""),
        ec_salinity_note=ec,
        phi_class_note=phi,
        irrigation_context=(
            str(raw["irrigation_context"]) if raw.get("irrigation_context") else None
        ),
        sort_order=int(raw.get("sort_order") or 100),
    )


def load_catalog_from_dataset(path: Path | None = None) -> tuple[CatalogItem, ...]:
    """Load expandable catalog from JSON dataset."""
    p = path or _DATASET_PATH
    if not p.is_file():
        logger.warning("Agro materials dataset missing: %s", p)
        return ()
    data = json.loads(p.read_text(encoding="utf-8"))
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("agro_materials.json must contain an items list")
    return tuple(_item_from_json(raw) for raw in items)


CATALOG: tuple[CatalogItem, ...] = load_catalog_from_dataset()


def ensure_agro_catalog(db: Session) -> int:
    """Idempotent upsert of reference catalog rows. Returns touched count."""
    from app.models import AgroMaterial

    catalog = load_catalog_from_dataset() or CATALOG
    if not catalog:
        logger.error("Agro catalog empty — skip seed")
        return 0

    touched = 0
    for item in catalog:
        row = db.query(AgroMaterial).filter(AgroMaterial.code == item.code).first()
        fields = dict(
            kind=item.kind,
            name_tr=item.name_tr,
            name_en=item.name_en,
            category=item.category,
            nutrient_focus=item.nutrient_focus,
            purpose=item.purpose,
            ec_salinity_note=item.ec_salinity_note,
            phi_class_note=item.phi_class_note,
            irrigation_context=item.irrigation_context,
            sort_order=item.sort_order,
            is_active=True,
        )
        if row:
            for k, v in fields.items():
                setattr(row, k, v)
        else:
            db.add(AgroMaterial(code=item.code, **fields))
        touched += 1
    db.flush()
    return touched


def format_materials_summary(uses: list) -> str | None:
    """Build compact Turkish summary for LLM / rule commentary.

    Last-used fertilizer/pesticide are highlighted first for AI context.
    """
    if not uses:
        return None
    last_parts: list[str] = []
    other_parts: list[str] = []
    for use in uses:
        mat = getattr(use, "material", None)
        if mat is None:
            continue
        kind_tr = "gübre" if mat.kind == "fertilizer" else "bitki koruma"
        bit = f"{mat.name_tr} ({kind_tr}"
        if mat.nutrient_focus:
            bit += f", {mat.nutrient_focus}"
        bit += ")"
        if use.frequency:
            bit += f" — sıklık: {use.frequency}"
        if use.last_applied_at:
            dt = use.last_applied_at
            date_s = dt.date().isoformat() if hasattr(dt, "date") else str(dt)[:10]
            bit += f" — son uygulama: {date_s}"
        if use.notes:
            bit += f" — not: {use.notes[:80]}"

        is_last_fert = bool(getattr(use, "is_last_fertilizer", False))
        is_last_pest = bool(getattr(use, "is_last_pesticide", False))
        if is_last_fert:
            last_parts.append(f"SON GÜBRE: {bit}")
        elif is_last_pest:
            last_parts.append(f"SON İLAÇ: {bit}")
        else:
            other_parts.append(bit)

    parts = last_parts + other_parts
    return "; ".join(parts) if parts else None


def commentary_from_materials(uses: list, ec: float | None = None) -> list[str]:
    """Educational irrigation/EC/data-quality notes — never dose scripts."""
    notes: list[str] = []
    if not uses:
        return notes
    codes: set[str] = set()
    kinds: set[str] = set()
    for use in uses:
        mat = getattr(use, "material", None)
        if not mat:
            continue
        codes.add(mat.code)
        kinds.add(mat.kind)
        if getattr(use, "is_last_fertilizer", False) and mat.irrigation_context:
            notes.append(f"Son kullanılan gübre ({mat.name_tr}): {mat.irrigation_context}")
        elif getattr(use, "is_last_pesticide", False) and mat.irrigation_context:
            notes.append(f"Son kullanılan ilaç ({mat.name_tr}): {mat.irrigation_context}")
        elif mat.irrigation_context:
            notes.append(mat.irrigation_context)
    high_k = {"fert_kno3", "fert_k2so4", "fert_mkp"} & codes
    if high_k and ec is not None and ec >= 2.5:
        notes.append(
            f"Kayıtlı potasyum/P-K fertigasyon + EC {ec}: tuz birikimi sulama yonetimini "
            "etkiler (yıkama / drenaj bağlamı) — gübre dozu yazılmaz."
        )
    elif high_k:
        notes.append(
            "Potasyum ağırlıklı gübre profili seçilmiş; EC yükselişini nem ile birlikte izleyin."
        )
    if kinds & {"plant_protection"}:
        notes.append(
            "Bitki koruma sınıfı kayıtlı: yaprak ıslaklığı toprak nemi değildir."
        )
    seen: set[str] = set()
    out: list[str] = []
    for n in notes:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out[:5]
