"""Rule-based lab soil interpretation (not fertilizer prescriptions)."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path

PARAM_LABELS = {
    "ph": "pH",
    "ec": "EC",
    "om": "Organik madde",
    "organic_matter": "Organik madde",
    "lime": "Kireç",
    "p": "Fosfor",
    "phosphorus": "Fosfor",
    "k": "Potasyum",
    "potassium": "Potasyum",
    "n": "Azot",
    "nitrogen": "Azot",
    "ca": "Kalsiyum",
    "calcium": "Kalsiyum",
    "zn": "Çinko",
    "zinc": "Çinko",
    "fe": "Demir",
    "iron": "Demir",
    "b": "Bor",
    "boron": "Bor",
    "mg": "Magnezyum",
    "magnesium": "Magnezyum",
    "na": "Sodyum",
    "sodium": "Sodyum",
    "texture": "Bünye",
    "saturation": "Saturasyon",
}

DEFAULT_UNITS = {
    "ph": "pH",
    "ec": "dS/m",
    "om": "%",
    "organic_matter": "%",
    "lime": "%",
    "p": "ppm",
    "phosphorus": "ppm",
    "k": "ppm",
    "potassium": "ppm",
    "n": "ppm",
    "nitrogen": "ppm",
    "ca": "ppm",
    "calcium": "ppm",
    "zn": "ppm",
    "zinc": "ppm",
    "fe": "ppm",
    "iron": "ppm",
    "b": "ppm",
    "boron": "ppm",
    "mg": "ppm",
    "magnesium": "ppm",
    "na": "ppm",
    "sodium": "ppm",
}

# TR soil lab core + optional parameter set (acceptance / UI allow-list)
SOIL_CORE_CODES = frozenset({"ph", "om", "p", "k"})
SOIL_OPTIONAL_CODES = frozenset(
    {"ec", "lime", "n", "ca", "mg", "zn", "fe", "b", "na", "texture", "saturation"}
)
SOIL_EXPECTED_CODES = SOIL_CORE_CODES | SOIL_OPTIONAL_CODES

SOIL_POSITIVE_KEYWORDS: tuple[str, ...] = (
    "toprak analiz",
    "toprak analizi",
    "toprak laboratuvar",
    "toprak laboratuar",
    "analiz raporu",
    "laboratuvar raporu",
    "laboratuar raporu",
    "soil analysis",
    "soil report",
    "organik madde",
    "organic matter",
    "elektriksel iletkenlik",
    "p2o5",
    "p₂o₅",
    "k2o",
    "k₂o",
    "caco3",
    "caco₃",
    "yarayışlı",
    "yarayisli",
    "numune derin",
    "bünye",
    "bunye",
    "tekstür",
    "tekstur",
    "tarım laboratuvar",
    "tarim laboratuvar",
    "il toprak",
    "il tarım",
    "toprak ph",
    "saturasyon",
)

SOIL_NEGATIVE_KEYWORDS: tuple[str, ...] = (
    "fatura",
    "invoice",
    "receipt",
    "ödeme bildirimi",
    "kredi kartı",
    "weather forecast",
    "hava durumu",
    "meteoroloji",
    "hastane",
    "kan tahlili",
    "kan sonucu",
    "eczane",
    "irsaliye",
    "sipariş no",
    "order confirmation",
)

MIN_SOIL_GATE_SCORE = 40.0


def normalize_code(code: str) -> str:
    c = code.lower().strip()
    aliases = {
        "organic_matter": "om",
        "phosphorus": "p",
        "potassium": "k",
        "nitrogen": "n",
        "calcium": "ca",
        "zinc": "zn",
        "iron": "fe",
        "boron": "b",
        "magnesium": "mg",
        "sodium": "na",
        "caco3": "lime",
        "p2o5": "p",
        "k2o": "k",
    }
    return aliases.get(c, c)


@dataclass
class SoilGateResult:
    accepted: bool
    score: float
    message: str
    matched_keywords: list[str] = field(default_factory=list)
    matched_params: list[str] = field(default_factory=list)


def score_soil_document(text: str, parsed_codes: set[str] | None = None) -> SoilGateResult:
    """Score whether extracted text looks like a TR farm soil laboratory report."""
    raw = (text or "").strip()
    low = raw.lower()
    codes = {normalize_code(c) for c in (parsed_codes or set()) if c}

    if not raw:
        return SoilGateResult(
            accepted=False,
            score=0.0,
            message=(
                "Belgeden okunabilir metin çıkarılamadı. "
                "Tarımsal toprak analiz raporu (PDF metin/CSV/TXT) yükleyin; "
                "görüntü taraması için OCR henüz yok — manuel lab girişi kullanın."
            ),
        )

    neg_hits = [k for k in SOIL_NEGATIVE_KEYWORDS if k in low]
    pos_hits = [k for k in SOIL_POSITIVE_KEYWORDS if k in low]

    # Loose single-token soil signals
    loose_tokens = (
        "toprak",
        "laboratuvar",
        "laboratuar",
        "organik",
        "fosfor",
        "potasyum",
        "kireç",
        "kirec",
        " ph",
        "ph ",
        "ph:",
        " ec",
        "ec:",
        "ppm",
        "ds/m",
        "mg/kg",
    )
    loose_hits = [t.strip() for t in loose_tokens if t in low]

    # Param signals from raw text (even before full parse)
    param_text_hits: list[str] = []
    for pattern, code in (
        (r"(?:^|[^a-z])ph(?:$|[^a-z0-9])", "ph"),
        (r"organik\s*madde|\bom\b", "om"),
        (r"p2o5|fosfor|phosphorus", "p"),
        (r"k2o|potasyum|potassium", "k"),
        (r"elektriksel\s*iletkenlik|\bec\b", "ec"),
        (r"kire[cç]|caco3", "lime"),
        (r"\bazot\b|\bnitrogen\b", "n"),
        (r"kalsiyum|\bca\b", "ca"),
        (r"magnezyum|\bmg\b", "mg"),
        (r"bünye|bunye|tekst[uü]r", "texture"),
    ):
        if re.search(pattern, low):
            param_text_hits.append(code)

    all_param_codes = codes | set(param_text_hits)
    core_found = sorted(all_param_codes & SOIL_CORE_CODES)
    opt_found = sorted(all_param_codes & SOIL_OPTIONAL_CODES)

    score = 0.0
    score += min(45.0, len(pos_hits) * 12.0)
    score += min(15.0, len(loose_hits) * 3.0)
    score += min(48.0, len(core_found) * 12.0)
    score += min(15.0, len(opt_found) * 3.0)
    score -= min(50.0, len(neg_hits) * 20.0)

    # Strong reject: negative docs without soil core
    if neg_hits and len(core_found) < 2 and len(pos_hits) == 0:
        score = min(score, 15.0)

    # Structured soil param sheet (CSV) with ≥2 core codes is enough
    if len(core_found) >= 2 and not (neg_hits and len(pos_hits) == 0 and len(core_found) < 3):
        score = max(score, 55.0)

    accepted = score >= MIN_SOIL_GATE_SCORE and (
        len(core_found) >= 2
        or (len(pos_hits) >= 1 and len(core_found) >= 1)
        or (len(pos_hits) >= 2 and len(all_param_codes & SOIL_EXPECTED_CODES) >= 2)
    )

    if accepted:
        msg = (
            f"Toprak laboratuvar raporu olarak kabul edildi (skor {score:.0f}/100). "
            "Değerleri onaylamadan kayda geçmez."
        )
    else:
        msg = (
            "Bu dosya tarımsal toprak laboratuvar analiz raporu gibi görünmüyor. "
            "Fatura, hava durumu veya rastgele PDF kabul edilmez; "
            "sahte toprak analizi üretilmez. "
            "Örnek parametreler: pH, organik madde, P2O5, K2O, EC, kireç."
        )
        if neg_hits:
            msg += f" Tespit: alakasız içerik ({', '.join(neg_hits[:3])})."

    return SoilGateResult(
        accepted=accepted,
        score=round(max(0.0, min(100.0, score)), 1),
        message=msg,
        matched_keywords=pos_hits[:8],
        matched_params=sorted(all_param_codes & SOIL_EXPECTED_CODES),
    )


def param_label(code: str) -> str:
    return PARAM_LABELS.get(normalize_code(code), code)


def classify_value(code: str, value: float) -> dict:
    """Return label, tone, and optional insight for a parameter."""
    c = normalize_code(code)
    if c == "ph":
        if value < 5.5:
            return {
                "label": "Asidik",
                "tone": "warn",
                "risk": "medium",
                "message": "Asidik pH besin alınabilirliğini düşürebilir.",
            }
        if value < 6.5:
            return {
                "label": "İdeal",
                "tone": "ok",
                "risk": "low",
                "message": "pH çoğu ürün için uygun aralıkta.",
            }
        if value <= 7.5:
            return {
                "label": "Nötr / hafif alkali",
                "tone": "ok",
                "risk": "low",
                "message": "pH kabul edilebilir; mikro besinleri izleyin.",
            }
        if value <= 8.2:
            return {
                "label": "Hafif alkali",
                "tone": "warn",
                "risk": "medium",
                "message": "Hafif alkali pH — demir/çinko alınabilirliği azalabilir.",
            }
        return {
            "label": "Alkali",
            "tone": "critical",
            "risk": "high",
            "message": "Yüksek pH — kritik bulgu; uzman görüşü önerilir.",
        }
    if c == "ec":
        if value < 0.8:
            return {"label": "Düşük", "tone": "ok", "risk": "low", "message": "EC düşük-orta; tuzluluk riski sınırlı."}
        if value <= 2.0:
            return {"label": "Orta", "tone": "ok", "risk": "low", "message": "EC orta seviyede."}
        if value <= 3.5:
            return {"label": "Yüksek", "tone": "warn", "risk": "medium", "message": "EC yüksek — sulama suyu ve drenajı kontrol edin."}
        return {"label": "Kritik", "tone": "critical", "risk": "high", "message": "Yüksek tuzluluk (EC) — kritik bulgu."}
    if c == "om":
        if value < 1.5:
            return {
                "label": "Düşük",
                "tone": "critical",
                "risk": "high",
                "message": "Organik madde düşük — toprak yapısı ve su tutumu zayıf olabilir.",
            }
        if value < 2.5:
            return {"label": "Orta-düşük", "tone": "warn", "risk": "medium", "message": "Organik madde sınırda; iyileştirme önerilir."}
        if value < 4.0:
            return {"label": "İyi", "tone": "ok", "risk": "low", "message": "Organik madde yeterli."}
        return {"label": "Yüksek", "tone": "ok", "risk": "low", "message": "Organik madde yüksek."}
    if c in {"p", "k", "n"}:
        low = 15 if c != "k" else 150
        high = 40 if c != "k" else 350
        if value < low:
            return {"label": "Düşük", "tone": "warn", "risk": "medium", "message": f"{param_label(c)} düşük görünüyor (bilgi amaçlı; reçete değil)."}
        if value > high:
            return {"label": "Yüksek", "tone": "warn", "risk": "low", "message": f"{param_label(c)} yüksek; gübreleme planında dikkate alın."}
        return {"label": "Yeterli", "tone": "ok", "risk": "low", "message": f"{param_label(c)} yeterli aralıkta."}
    if c == "lime":
        if value > 25:
            return {"label": "Yüksek", "tone": "warn", "risk": "medium", "message": "Kireç oranı yüksek."}
        return {"label": "Uygun", "tone": "ok", "risk": "low", "message": "Kireç oranı kabul edilebilir."}
    return {"label": "—", "tone": "neutral", "risk": "low", "message": f"{param_label(c)} kaydı mevcut."}


def interpret_report(parameters: list[dict]) -> list[dict]:
    insights: list[dict] = []
    for p in parameters:
        code = p.get("parameter_code") or p.get("code")
        value = p.get("value")
        if code is None or value is None:
            continue
        info = classify_value(str(code), float(value))
        insights.append(
            {
                "parameter_code": normalize_code(str(code)),
                "label": param_label(str(code)),
                "value": float(value),
                "unit": p.get("unit") or DEFAULT_UNITS.get(normalize_code(str(code)), ""),
                "status_label": info["label"],
                "tone": info["tone"],
                "risk": info["risk"],
                "message": info["message"],
            }
        )
    # sort critical first
    order = {"high": 0, "medium": 1, "low": 2}
    insights.sort(key=lambda x: order.get(x["risk"], 9))
    return insights


def count_critical(insights: list[dict]) -> int:
    return sum(1 for i in insights if i.get("risk") == "high")


def demo_extraction() -> tuple[list[dict], float]:
    """Simulated parameter set — only valid after a real file upload, never alone."""
    rows = [
        {"parameter_code": "ph", "value": 7.8, "unit": "pH", "confidence_pct": 96, "extracted_auto": True},
        {"parameter_code": "ec", "value": 1.42, "unit": "dS/m", "confidence_pct": 91, "extracted_auto": True},
        {"parameter_code": "om", "value": 1.65, "unit": "%", "confidence_pct": 88, "extracted_auto": True},
        {"parameter_code": "lime", "value": 21.3, "unit": "%", "confidence_pct": 84, "extracted_auto": True},
        {"parameter_code": "p", "value": 18.5, "unit": "ppm", "confidence_pct": 79, "extracted_auto": True},
        {"parameter_code": "k", "value": 280, "unit": "ppm", "confidence_pct": 93, "extracted_auto": True},
        {"parameter_code": "n", "value": 42, "unit": "ppm", "confidence_pct": 72, "extracted_auto": True},
        {"parameter_code": "zn", "value": 1.1, "unit": "ppm", "confidence_pct": 65, "extracted_auto": True},
        {"parameter_code": "fe", "value": 8.4, "unit": "ppm", "confidence_pct": 58, "extracted_auto": True},
    ]
    avg = sum(r["confidence_pct"] for r in rows) / len(rows)
    return rows, round(avg, 1)


# Heuristic token → parameter_code (Turkish + English lab labels)
_TEXT_ALIASES: list[tuple[tuple[str, ...], str]] = [
    (("organik madde", "organic matter", "organikmadde", " o.m.", "om%"), "om"),
    (("elektriksel iletkenlik", "electrical conductivity", " e.c.", "ec ", "ec:", "ec="), "ec"),
    (("kirec", "kireç", "caco3", "caco₃", "lime"), "lime"),
    (("fosfor", "phosphorus", "p2o5", "p₂o₅", " yar. p", "p "), "p"),
    (("potasyum", "potassium", "k2o", "k₂o", " yar. k", "k "), "k"),
    (("azot", "nitrogen", " toplam n", "n "), "n"),
    (("kalsiyum", "calcium", " ca ", "ca:", "ca="), "ca"),
    (("cinko", "çinko", "zinc", "zn"), "zn"),
    (("demir", "iron", "fe"), "fe"),
    (("boron", " bor ", "b "), "b"),
    (("magnezyum", "magnesium", "mg"), "mg"),
    (("sodyum", "sodium", "na"), "na"),
    (("saturasyon", "saturation", "isba", "işba"), "saturation"),
    (("bünye", "bunye", "tekstür", "tekstur", "texture"), "texture"),
    ((" ph", "ph ", "ph:", "ph=", "toprak ph", "ph değeri"), "ph"),
]


def _parse_number(token: str) -> float | None:
    t = token.strip().replace(",", ".").replace("%", "")
    try:
        return float(t)
    except ValueError:
        return None


def _match_code(line: str) -> str | None:
    low = f" {line.lower()} "
    # Prefer pH early — short token "ph" alone is ambiguous in other words
    if re.search(r"(?:^|[^a-z])ph(?:$|[^a-z0-9])", low) or "toprak ph" in low or "ph değeri" in low:
        return "ph"
    for aliases, code in _TEXT_ALIASES:
        if code == "ph":
            continue
        for a in aliases:
            if a in low:
                return code
    return None


def parse_parameters_from_text(text: str) -> list[dict]:
    """Pull parameter_code/value/unit pairs from free text or CSV-like lines."""
    found: dict[str, dict] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or len(line) < 3:
            continue
        # CSV / TSV: code_or_label, value, unit
        parts = re.split(r"[,;\t|]+", line)
        if len(parts) >= 2:
            code = normalize_code(parts[0].strip())
            if code in DEFAULT_UNITS or code in PARAM_LABELS or code in SOIL_EXPECTED_CODES:
                val = _parse_number(parts[1])
                if val is not None:
                    unit = parts[2].strip() if len(parts) >= 3 and parts[2].strip() else DEFAULT_UNITS.get(code, "")
                    if code == "texture" and not unit:
                        unit = parts[1].strip() or "bünye"
                        val = 0.0
                    found[code] = {
                        "parameter_code": code,
                        "value": val,
                        "unit": unit or DEFAULT_UNITS.get(code, ""),
                        "confidence_pct": 82.0,
                        "extracted_auto": True,
                    }
                    continue
            # label,value[,unit]
            code2 = _match_code(parts[0])
            val2 = _parse_number(parts[1])
            if code2 and val2 is not None:
                unit = parts[2].strip() if len(parts) >= 3 and parts[2].strip() else DEFAULT_UNITS.get(code2, "")
                found[code2] = {
                    "parameter_code": code2,
                    "value": val2,
                    "unit": unit or DEFAULT_UNITS.get(code2, ""),
                    "confidence_pct": 78.0,
                    "extracted_auto": True,
                }
                continue

        code3 = _match_code(line)
        if not code3:
            continue
        if code3 == "texture":
            found[code3] = {
                "parameter_code": code3,
                "value": 0.0,
                "unit": line.split(":")[-1].strip()[:40] or "bünye",
                "confidence_pct": 65.0,
                "extracted_auto": True,
            }
            continue
        nums = re.findall(r"[-+]?\d+(?:[.,]\d+)?", line)
        if not nums:
            continue
        # Prefer the number after the label when multiple exist
        val3 = _parse_number(nums[-1] if code3 != "ph" else nums[0])
        if val3 is None:
            continue
        unit_guess = DEFAULT_UNITS.get(code3, "")
        for u in ("% ", "dS/m", "ds/m", "ppm", "mg/kg", "meq"):
            if u.lower().strip() in line.lower():
                unit_guess = u.strip() if u.strip() != "% " else "%"
                break
        found[code3] = {
            "parameter_code": code3,
            "value": val3,
            "unit": unit_guess,
            "confidence_pct": 70.0,
            "extracted_auto": True,
        }
    return list(found.values())


def _decode_text_bytes(content: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1254"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ""
    try:
        reader = PdfReader(io.BytesIO(content))
        chunks: list[str] = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        return "\n".join(chunks)
    except Exception:
        return ""


def extract_text_from_bytes(content: bytes, filename: str) -> str:
    """Best-effort text extraction (no image OCR in MVP)."""
    name = filename.lower()
    ext = Path(name).suffix
    if ext == ".pdf":
        return _extract_pdf_text(content)
    if ext in {".csv", ".txt", ".tsv"}:
        return _decode_text_bytes(content)
    if ext in {".xlsx", ".xls"}:
        text = _decode_text_bytes(content)
        if text.count("\x00") > 20:
            return ""
        return text
    if ext in {".jpg", ".jpeg", ".png"}:
        return ""
    return _decode_text_bytes(content)


def extract_from_file(
    content: bytes,
    filename: str,
    *,
    allow_simulated_fallback: bool = False,
    use_ai: bool = True,
) -> tuple[list[dict], float, str, str, SoilGateResult]:
    """
    Extract lab parameters from an uploaded report file.

    Returns (parameters, confidence, mode, message, soil_gate).
    mode: "parsed" | "ai" | "rejected" | "needs_manual"
    Never invents fake soil values for unrelated documents.
    allow_simulated_fallback is kept for API compat but ignored (always False path).
    """
    del allow_simulated_fallback  # deprecated — no fake soil analysis
    text = extract_text_from_bytes(content, filename)
    heuristic = parse_parameters_from_text(text) if text.strip() else []
    codes = {normalize_code(p["parameter_code"]) for p in heuristic}
    gate = score_soil_document(text, codes)

    if not gate.accepted:
        return [], 0.0, "rejected", gate.message, gate

    # Prefer AI structured parse when key present
    if use_ai:
        try:
            from app.lab_ai import parse_soil_report_with_ai

            ai_result = parse_soil_report_with_ai(text)
        except Exception:
            ai_result = None
        if ai_result is not None:
            rows, avg, ai_msg = ai_result
            if not rows and "olmadığı" in ai_msg.lower():
                # AI says not a soil report — override gate
                reject = SoilGateResult(
                    accepted=False,
                    score=min(gate.score, 20.0),
                    message=ai_msg,
                    matched_keywords=gate.matched_keywords,
                    matched_params=gate.matched_params,
                )
                return [], 0.0, "rejected", ai_msg, reject
            if len(rows) >= 2:
                return rows, avg, "ai", ai_msg, gate
            if rows and len(heuristic) < 2:
                return rows, avg, "ai", ai_msg, gate

    if len(heuristic) >= 2:
        avg = round(sum(p.get("confidence_pct") or 0 for p in heuristic) / len(heuristic), 1)
        return (
            heuristic,
            avg,
            "parsed",
            "Dosyadan metin çıkarıldı (heuristik). Gerçek OCR değildir — değerleri doğrulayın.",
            gate,
        )

    # Soil-like but unparseable (scan/image/empty values) — soft fail, no fake demo
    soft = (
        "Belge toprak analiz raporu gibi görünüyor ancak parametreler okunamadı. "
        "Metin içeren PDF/CSV/TXT deneyin veya manuel lab girişi kullanın. "
        "Sahte değer üretilmedi."
    )
    return [], 0.0, "needs_manual", soft, gate


def compute_status(user_confirmed: bool, parameters: list) -> str:
    codes = {normalize_code(getattr(p, "parameter_code", None) or p.get("parameter_code", "")) for p in parameters}
    if "ph" not in codes or len(codes) < 2:
        return "missing"
    if not user_confirmed:
        return "pending"
    return "verified"
