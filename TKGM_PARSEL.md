# TKGM Parsel Sorgusu — AgriTwin Tasarım Notu

## Amaç

Arazi oluşturma / düzenlemede **il → ilçe → mahalle → ada / parsel** ile TKGM MEGSIS üzerinden parsel geometrisi ve merkezi almak; lat/lng ve alanı (da) doldurmak; dijital ikiz haritasında sınır poligonunu çizmek.

Bu bir **konum yardımcı** özelliğidir — nem MVP’sinin yerine geçmez.

## Mimari

| Katman | Rol |
|--------|-----|
| Frontend (Leaflet / OSM) | Cascade UI + GeoJSON çizimi |
| FastAPI `GET /geo/*` | Sunucu tarafı proxy + normalize |
| TKGM MEGSIS (public) | Kaynak idari liste + parsel |

**Neden proxy?** Tarayıcıdan doğrudan `cbsapi.tkgm.gov.tr` CORS / User-Agent kısıtlarına takılır; anahtar gerekmez ama istekler sunucudan yapılmalıdır. Electron + Google Maps forklamak gerekmez.

## Sarılan uçlar (upstream)

| AgriTwin | Upstream |
|----------|----------|
| `GET /geo/provinces` | `https://parselsorgu.tkgm.gov.tr/app/modules/administrativeQuery/data/ilListe.json` (yedek: cbsapi `…/ilListe`) |
| `GET /geo/districts?il_id=` | `https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api/idariYapi/ilceListe/{ilId}` |
| `GET /geo/neighborhoods?ilce_id=` | `…/idariYapi/mahalleListe/{ilceId}` |
| `GET /geo/parcel?mahalle_id=&ada=&parsel=` | `…/api/parsel/{mahalleId}/{ada}/{parsel}` |

API anahtarı **gerekmez** (genel MEGSIS sorgu uçları).

## Normalize cevap (parsel)

```json
{
  "mahalle": "…",
  "ada": "101",
  "parsel": "12",
  "area_da": 2.45,
  "centroid": { "lat": 36.91, "lng": 31.10 },
  "geometry": { "type": "Polygon", "coordinates": […] }
}
```

`area_da`: TKGM alanı m² ise `/ 1000` ile dekara çevrilir. Alan yoksa `null` — kullanıcı manuel girebilir.

## Oran sınırlama ve önbellek

- Upstream timeout ~12–15 sn; sabit `User-Agent` + `Referer: parselsorgu.tkgm.gov.tr`
- İl / ilçe / mahalle listeleri kısa TTL bellek önbelleği (≈1 saat)
- Parsel sorgusu önbelleğe alınmaz (veya çok kısa TTL) — yanlış sonuç riski

## Hata mesajları (TR)

| Durum | Mesaj |
|-------|--------|
| Parsel yok (404) | Parsel bulunamadı. Ada / parsel numarasını kontrol edin. |
| TKGM down / timeout | TKGM servisine şu an ulaşılamıyor. Konumu manuel girin. |
| Eksik parametre | İlçe / mahalle / ada / parsel gerekli. |

## Yasal / ürün uyarısı

- **Resmi TKGM ortaklığı yoktur.** Veri halka açık MEGSIS uçlarından alınır; süreklilik veya doğruluk garantisi verilmez.
- Tapu / hukuki işlem için resmi kanalları kullanın.
- UI’da “resmi TKGM entegrasyonu” iddiası yapılmaz; isteğe bağlı konum yardımcısı olarak sunulur.

## Fallback

Parsel bulunamazsa veya servis düşerse: mevcut **manuel lat / lng / alan** alanları kullanılır; arazi yine kaydedilir.

## Farm alanları

Opsiyonel: `parcel_ada`, `parcel_parsel`, `parcel_mahalle_id`, `geometry_geojson` (+ mevcut `latitude` / `longitude` / `area`).
