"""Rule-based water usage / savings estimates for MVP reporting."""

from __future__ import annotations

from dataclasses import dataclass

# Calendar-style baseline: fixed 45 min × 6 L/min per session (without AI).
BASELINE_DURATION_MIN = 45.0
WATER_PER_MINUTE = 6.0


@dataclass
class WaterUsageReport:
    session_count: int
    water_used_liters: float
    baseline_liters: float
    savings_liters: float
    savings_pct: float | None
    note: str


def compute_water_usage(
    completed_water_amounts: list[float | None],
) -> WaterUsageReport:
    """Compare actual virtual irrigation water vs a simple calendar baseline.

    Baseline assumes each completed session would have run BASELINE_DURATION_MIN
    without decision support. Actual amounts come from IrrigationEvent.water_amount.
    Honest MVP estimate — not a full digital-twin claim.
    """
    amounts = [float(a) for a in completed_water_amounts if a is not None]
    sessions = len(amounts)
    used = round(sum(amounts), 1)
    if sessions == 0:
        return WaterUsageReport(
            session_count=0,
            water_used_liters=0.0,
            baseline_liters=0.0,
            savings_liters=0.0,
            savings_pct=None,
            note="Henüz tamamlanmış sanal sulama yok.",
        )

    baseline = round(sessions * BASELINE_DURATION_MIN * WATER_PER_MINUTE, 1)
    savings = round(max(0.0, baseline - used), 1)
    pct = round((savings / baseline) * 100, 1) if baseline > 0 else None
    return WaterUsageReport(
        session_count=sessions,
        water_used_liters=used,
        baseline_liters=baseline,
        savings_liters=savings,
        savings_pct=pct,
        note=(
            f"Kural tabanlı tahmin: {sessions} oturum, "
            f"takvim tabanı {BASELINE_DURATION_MIN:.0f} dk/oturum vs gerçekleşen sanal su. "
            "Tam dijital ikiz iddiası değildir."
        ),
    )
