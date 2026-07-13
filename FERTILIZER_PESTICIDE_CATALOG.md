# Gübre / Bitki Koruma Referans Kataloğu

AgriTwin MVP, **reçete motoru değildir**. Bu katalog; sera/açık alan domates pratiklerinde sık geçen **genel sınıfları** tutar. Kullanıcı arazi kurulumunda “bu arazide kullanılan” seçer; AI yalnızca **nem, sulama, EC/tuzluluk ve veri kalitesi** bağlamında yorumlar.

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
| fert_compost | Kompost | organik | Su tutma |
| fert_manure | Ahır gübresi | organik | Değişken EC |

## Bitki koruma sınıfları

| Kod | Sınıf | Not |
|-----|--------|-----|
| pp_fungicide | Fungisit (genel) | PHI etikete bağlı |
| pp_insecticide | İnsektisit (genel) | PHI/MRL ürüne özgü |
| pp_acaricide | Akarisit (genel) | Sera domateste sık |
| pp_nematicide | Nematisit (genel) | Daha seyrek |
| pp_biological | Biyolojik / IPM | Kalıntı baskısını azaltma hedefi |

## Kaynaklar (özet)

1. Tarım Gündem — sera domates dönemsel gübreleme (MAP, KNO₃, amonyum sülfat, Ca/Mg nitrat): https://tarimgundemdergisi.com/sera-yetistiriciliginde-domatesin-donemsel-gubrelenmesi/
2. Esular — sera gübreleme, EC/pH, A/B tank Ca–fosfat/sülfat ayrımı: https://store.esular.com/sera-gubreleme-ve-toprak-analizi-rehberi
3. Haifa Group — domates gübreleme örnekleri (MAP, KNO₃, amonyum nitrat, Ca nitrat): https://www.haifa-group.com/tr/ürün-rehberi-domateste-gübreleme-tavsiyeleri
4. DergiPark — TR sera domates pestisit kullanım anketi (insektisit, fungisit, akarisit, nematisit kategorileri): https://dergipark.org.tr/en/pub/ankutbd/article/1469332

## API

- `GET /agro-materials` — referans katalog
- `GET|PUT /farms/{id}/materials` — arazi seçimleri
- Arazi oluşturma/güncellemede `material_ids` veya `materials[]`

## AI kullanımı

OpenRouter / kural açıklamalarına `materials_summary` ve eğitim notları eklenir. Prompt açıkça **gübre/ilaç doz reçetesini reddeder**.
