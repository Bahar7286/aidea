# Gübre / Bitki Koruma Referans Kataloğu

AgriTwin MVP, **reçete motoru değildir**. Bu katalog; sera/açık alan domates pratiklerinde sık geçen **genel sınıfları** tutar. Kullanıcı arazi kurulumunda “bu arazide kullanılan” ve **son kullanılan gübre / ilaç** seçer; AI yalnızca **nem, sulama, EC/tuzluluk ve veri kalitesi** bağlamında yorumlar.

## Veri seti (kaynak)

Genişletilebilir JSON:

`backend/ai/datasets/agro_materials.json`

Alanlar: `id`, `name_tr`, `category` (`fertilizer` | `pesticide`), `purpose`, `notes` (+ isteğe bağlı `subcategory`, `nutrient_focus`, `irrigation_context`, `sort_order`).

DB seed: `ensure_agro_catalog()` bu dosyayı okuyup `AgroMaterial` satırlarını upsert eder. JSON’daki `pesticide` → DB `kind=plant_protection`.

## Kapsam dışı (ürün kısıtı)

- Gübre doz / NPK reçetesi (“yarın X kg uygula”) yok
- Hastalık teşhisi / ilaç reçetesi yok
- Marka-etiket iddiası veya yasadışı öneri yok

## Gübre sınıfları (örnekler)

| Kod | Sınıf | Odak | Not |
|-----|--------|------|-----|
| fert_map | MAP | P | Erken dönem / fertigasyon |
| fert_mkp | MKP | P-K | Fertigasyon |
| fert_kno3 | Potasyum nitrat | K | Meyve dönemi; EC etkisi |
| fert_k2so4 | Potasyum sülfat | K+S | Ca tank uyumsuzluğu |
| fert_nh4no3 | Amonyum nitrat | N | Hızlı N |
| fert_can | Kalsiyum nitrat | Ca+N | Düzensiz sulama bağlamı |
| fert_mgso4 | Mg sülfat/nitrat | Mg | Dönemsel |
| fert_as | Amonyum sülfat | N+S | Tuz birikimi |
| fert_urea | Üre / UAN | N | Açık alan / fertigasyon |
| fert_dap | DAP / taban P | N-P | Açık alan |
| fert_npk | Kompoze NPK | N-P-K | Genel sınıf |
| fert_humic | Humik / fulvik | organik | Yapı desteği |
| fert_fe | Demir şelat | Fe | Mikro |
| fert_compost | Kompost | organik | Su tutma |
| fert_manure | Ahır gübresi | organik | Değişken EC |

## Bitki koruma sınıfları

| Kod | Sınıf | Not |
|-----|--------|-----|
| pp_fungicide | Fungisit (genel) | PHI etikete bağlı |
| pp_insecticide | İnsektisit (genel) | PHI/MRL ürüne özgü |
| pp_acaricide | Akarisit (genel) | Sera domateste sık |
| pp_nematicide | Nematisit (genel) | Daha seyrek |
| pp_herbicide | Herbisit (genel) | Açık alan |
| pp_copper | Bakırlı preparat | Fungusit/bakterisit |
| pp_biological | Biyolojik / IPM | Kalıntı baskısını azaltma hedefi |

## UI

- Arazi oluştur / düzenle: çoklu seçim + **Son kullanılan gübre** / **Son kullanılan ilaç** + opsiyonel `last_applied_at`
- Arazi detay + hub ayarları: aynı panel (`FarmMaterialsPanel`)

## API

- `GET /agro-materials` — referans katalog
- `GET|PUT /farms/{id}/materials` — arazi seçimleri (`is_last_fertilizer`, `is_last_pesticide`, `last_applied_at`)
- Arazi oluşturma/güncellemede `material_ids` veya `materials[]`
- Kural: arazide kategori başına en fazla bir “son kullanılan”

## AI kullanımı

OpenRouter / kural açıklamalarına `materials_summary` eklenir; **SON GÜBRE** / **SON İLAÇ** öne çıkarılır. Prompt açıkça **gübre/ilaç doz reçetesini reddeder**.

## Kaynaklar (özet)

1. Tarım Gündem — sera domates dönemsel gübreleme: https://tarimgundemdergisi.com/sera-yetistiriciliginde-domatesin-donemsel-gubrelenmesi/
2. Esular — sera gübreleme, EC/pH: https://store.esular.com/sera-gubreleme-ve-toprak-analizi-rehberi
3. Haifa Group — domates gübreleme örnekleri: https://www.haifa-group.com/tr/ürün-rehberi-domateste-gübreleme-tavsiyeleri
4. DergiPark — TR sera domates pestisit kullanım anketi: https://dergipark.org.tr/en/pub/ankutbd/article/1469332
