"""Reference agro-material catalog (TR tomato greenhouse / open-field oriented).

Educational classes only — not brand labels, not dose prescriptions.
Sources summarized in FERTILIZER_PESTICIDE_CATALOG.md at repo root.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session


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


CATALOG: tuple[CatalogItem, ...] = (
    CatalogItem(
        code="fert_map",
        kind="fertilizer",
        name_tr="MAP (Monoamonyum fosfat)",
        name_en="MAP (monoammonium phosphate)",
        category="fosfat",
        nutrient_focus="P (N-P)",
        purpose="Kök ve erken dönem fosfor kaynağı; damla fertigasyonda yaygındır.",
        ec_salinity_note="Tuz etkisi orta; kalsiyum nitrat ile aynı stok tankında karıştırılmaz.",
        phi_class_note=None,
        irrigation_context="Fosfor ağırlıklı besleme döneminde EC'yi aşırı yükseltmeden sulama frekansını izleyin.",
        sort_order=10,
    ),
    CatalogItem(
        code="fert_mkp",
        kind="fertilizer",
        name_tr="MKP (Monopotasyum fosfat)",
        name_en="MKP (monopotassium phosphate)",
        category="fosfat",
        nutrient_focus="P-K",
        purpose="P+K kaynağı; çiçeklenme / meyve dönemlerinde fertigasyonda kullanılır.",
        ec_salinity_note="EC'ye katkı eder; tank karışımında Ca ile çökelme riski.",
        phi_class_note=None,
        irrigation_context="P-K fertigasyon EC artışını hızlandırabilir — yüksek EC'de yıkama sulaması düşünülür.",
        sort_order=20,
    ),
    CatalogItem(
        code="fert_kno3",
        kind="fertilizer",
        name_tr="Potasyum nitrat (KNO3)",
        name_en="Potassium nitrate",
        category="potasyum",
        nutrient_focus="K (+N)",
        purpose="Meyve gelişimi / kalite döneminde potasyum ağırlıklı fertigasyon.",
        ec_salinity_note="Yüksek K programları EC birikimine yol açabilir.",
        phi_class_note=None,
        irrigation_context="Yüksek K fertigasyonunda EC/tuzluluk ile nemi birlikte yorumlayın; doz reçetesi üretilmez.",
        sort_order=30,
    ),
    CatalogItem(
        code="fert_k2so4",
        kind="fertilizer",
        name_tr="Potasyum sülfat",
        name_en="Potassium sulfate",
        category="potasyum",
        nutrient_focus="K (+S)",
        purpose="Klorürsüz potasyum kaynağı; açık alan ve sera taban/fertigasyon.",
        ec_salinity_note="Sülfatlı gübreler EC'yi yükseltir; Ca nitrat ile aynı tankta karıştırılmaz.",
        phi_class_note=None,
        irrigation_context="Sülfatlı K programında drenaj / yıkama ihtiyacı nem yönetimini etkiler.",
        sort_order=40,
    ),
    CatalogItem(
        code="fert_nh4no3",
        kind="fertilizer",
        name_tr="Amonyum nitrat",
        name_en="Ammonium nitrate",
        category="azot",
        nutrient_focus="N",
        purpose="Hızlı azot kaynağı; sera ve açık alanda yaygın.",
        ec_salinity_note="Yoğun N programı kök bölgesi EC ve pH dengesini bozabilir.",
        phi_class_note=None,
        irrigation_context="Aşırı N ile birlikte yüksek nem/aşırı sulama riski artabilir — dengeli sulama izlenir.",
        sort_order=50,
    ),
    CatalogItem(
        code="fert_can",
        kind="fertilizer",
        name_tr="Kalsiyum nitrat",
        name_en="Calcium nitrate",
        category="kalsiyum",
        nutrient_focus="Ca (+N)",
        purpose="Ca takviyesi; düzensiz sulama ile birlikte değerlendirilir.",
        ec_salinity_note="A/B tankta Ca ayrı tutulur; fosfat/sülfat ile çökelme.",
        phi_class_note=None,
        irrigation_context="Ca alımı düzensiz sulamadan etkilenir — nem sürekliliği yorumlanır, doz yazılmaz.",
        sort_order=60,
    ),
    CatalogItem(
        code="fert_mgso4",
        kind="fertilizer",
        name_tr="Magnezyum sülfat / nitrat",
        name_en="Magnesium sulfate / nitrate",
        category="magnezyum",
        nutrient_focus="Mg",
        purpose="Mg takviyesi; dönemsel fertigasyon programlarında yer alır.",
        ec_salinity_note="Sülfat formu EC'ye katkı eder.",
        phi_class_note=None,
        irrigation_context="Mg programı EC okumasını etkileyebilir; nem okuması ile karıştırılmamalıdır.",
        sort_order=70,
    ),
    CatalogItem(
        code="fert_as",
        kind="fertilizer",
        name_tr="Amonyum sülfat",
        name_en="Ammonium sulfate",
        category="azot",
        nutrient_focus="N (+S)",
        purpose="N+S kaynağı; damla ve bant uygulamalarında kullanılır.",
        ec_salinity_note="Sülfat tuz birikimine katkı; Ca ile tank uyumsuzluğu.",
        phi_class_note=None,
        irrigation_context="Tuz birikimi riskinde yıkama sulaması nem profilini değiştirir.",
        sort_order=80,
    ),
    CatalogItem(
        code="fert_urea",
        kind="fertilizer",
        name_tr="Üre / UAN",
        name_en="Urea / UAN",
        category="azot",
        nutrient_focus="N",
        purpose="Ucuz azot kaynağı; açık alanda ve bazı fertigasyon programlarında.",
        ec_salinity_note="Aşırı kullanım kök yanması / EC etkisi yaratabilir.",
        phi_class_note=None,
        irrigation_context="Azot zamanlaması sulama döngüsüyle bağlanır; reçete üretilmez.",
        sort_order=90,
    ),
    CatalogItem(
        code="fert_dap",
        kind="fertilizer",
        name_tr="DAP / taban fosfor",
        name_en="DAP / base phosphate",
        category="fosfat",
        nutrient_focus="N-P",
        purpose="Açık alan taban gübreleme sınıfı.",
        ec_salinity_note="Yüksek dozlarda lokal tuz stresi.",
        phi_class_note=None,
        irrigation_context="Taban sonrası ilk sulamalar tuz yıkanmasını etkileyebilir.",
        sort_order=100,
    ),
    CatalogItem(
        code="fert_compost",
        kind="fertilizer",
        name_tr="Kompost / organik madde",
        name_en="Compost / organic matter",
        category="organik",
        nutrient_focus="organik C / yavaş N",
        purpose="Toprak yapısı ve su tutma; organik girdi sınıfı.",
        ec_salinity_note="Olgunlaşmamış kompost lokal EC / gaz etkisi yapabilir.",
        phi_class_note=None,
        irrigation_context="Organik madde su tutmayı değiştirir — nem eşikleri ürün/toprakla birlikte okunur.",
        sort_order=110,
    ),
    CatalogItem(
        code="fert_manure",
        kind="fertilizer",
        name_tr="Ahır gübresi / farmyard manure",
        name_en="Farmyard manure",
        category="organik",
        nutrient_focus="organik N-P-K",
        purpose="Açık alan organik baz; değişken tuz ve olgunlaşma.",
        ec_salinity_note="Taze gübre yüksek EC / amonyak riski taşır.",
        phi_class_note=None,
        irrigation_context="Yüksek tuzlu organik girdide ilk sulamalar yıkama etkisi gösterebilir.",
        sort_order=120,
    ),
    CatalogItem(
        code="pp_fungicide",
        kind="plant_protection",
        name_tr="Fungisit (genel sınıf)",
        name_en="Fungicide (generic class)",
        category="fungisit",
        nutrient_focus=None,
        purpose="Fungal hastalık baskısı; TR sera domateste sık kullanılan gruplardan.",
        ec_salinity_note=None,
        phi_class_note="Hasat öncesi bekleme süresi (PHI) ürüne ve etken maddeye göre değişir — etiket zorunlu.",
        irrigation_context="Yaprak uygulaması toprak nem sensörünü temsil etmez; okumayı ilaçla karıştırmayın.",
        sort_order=200,
    ),
    CatalogItem(
        code="pp_insecticide",
        kind="plant_protection",
        name_tr="İnsektisit (genel sınıf)",
        name_en="Insecticide (generic class)",
        category="insektisit",
        nutrient_focus=None,
        purpose="Zararlı böcek baskısı; sera domates anketlerinde yaygın kategori.",
        ec_salinity_note=None,
        phi_class_note="PHI ve MRL ürüne özgüdür; bu katalog reçete değildir.",
        irrigation_context="İlaçlama günü yaprak ıslaklığı nem/sensor yorumunu yanıltabilir.",
        sort_order=210,
    ),
    CatalogItem(
        code="pp_acaricide",
        kind="plant_protection",
        name_tr="Akarisit (genel sınıf)",
        name_en="Acaricide (generic class)",
        category="akarisit",
        nutrient_focus=None,
        purpose="Kırmızı örümcek vb. akar mücadelesi; sera domateste sık kategori.",
        ec_salinity_note=None,
        phi_class_note="Bekleme süresi etiket ve ihracat MRL'lerine bağlıdır.",
        irrigation_context="Foliar uygulama sonrası nem okumasını toprak nemi sanmayın.",
        sort_order=220,
    ),
    CatalogItem(
        code="pp_nematicide",
        kind="plant_protection",
        name_tr="Nematisit (genel sınıf)",
        name_en="Nematicide (generic class)",
        category="nematisit",
        nutrient_focus=None,
        purpose="Kök-ur nematodu vb.; sera domateste daha seyrek ama kayıtlı kategori.",
        ec_salinity_note=None,
        phi_class_note="Çoğu ürün sıkı PHI / uygulama kısıtı taşır — mühendis/etiket şart.",
        irrigation_context="Toprak uygulaması sonrası ıslatma sulaması nem profilini geçici değiştirir.",
        sort_order=230,
    ),
    CatalogItem(
        code="pp_biological",
        kind="plant_protection",
        name_tr="Biyolojik / IPM destek",
        name_en="Biological / IPM support",
        category="biyolojik",
        nutrient_focus=None,
        purpose="Faydalı böcek / biyolojik preparat sınıfı; kalıntı baskısını azaltma hedefi.",
        ec_salinity_note=None,
        phi_class_note="Genelde kimyasal PHI'den farklıdır; ürün bazlı kontrol gerekir.",
        irrigation_context="Sulama zamanlaması faydalı organizma salımını etkileyebilir — doz reçetesi yok.",
        sort_order=240,
    ),
)


def ensure_agro_catalog(db: Session) -> int:
    """Idempotent upsert of reference catalog rows. Returns touched count."""
    from app.models import AgroMaterial

    touched = 0
    for item in CATALOG:
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
    """Build compact Turkish summary for LLM / rule commentary."""
    if not uses:
        return None
    parts: list[str] = []
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
        if use.notes:
            bit += f" — not: {use.notes[:80]}"
        parts.append(bit)
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
        if mat.irrigation_context:
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
    return out[:4]
