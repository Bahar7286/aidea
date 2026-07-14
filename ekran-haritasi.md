# AgriTwin AI — Ekran Haritası ve UX/UI Spesifikasyonu

## 1. Amaç ve sayım kuralları

Bu doküman AgriTwin AI ürününün **ekran envanterini**, bilgi mimarisini ve UX/UI spesifikasyonlarını tanımlar.

### Sayım

| Kapsam | Sayı |
|--------|------|
| Çiftçi / ziraat mühendisi uygulaması | 30 (F01–F30) |
| Yönetici paneli | 8 (A01–A08) |
| **Toplam ana ekran** | **38** |

### Kurallar

- **Mobil ayrı ekran sayılmaz.** Mobil = aynı ekranın responsive varyasyonu (`designsystem.md` §28).
- Token, renk, tipografi → [`designsystem.md`](designsystem.md).
- Veri kaynağı / lab → [`veri-mimarisi.md`](veri-mimarisi.md).
- Saha cihazı → [`iot-mimarisi.md`](iot-mimarisi.md).
- Ürün kapsamı: nem + sulama karar desteği; **tam dijital ikiz iddiası yok.**
- Simülasyon asla “gerçek sensör” diye sunulmaz.
- Sanal sulama: kullanıcı onayı zorunlu; güven &lt; 60 → otomasyon önerilmez.

### MVP önceliği

İlk çalışan prototip için **20 ekran** detaylı tasarlanır (aşağıda ★). Kalan 18 envanterde tanımlıdır; kod P1/P2.

---

## 2. Bilgi mimarisi

### 2.1. Çiftçi uygulaması

```text
Auth (oturumsuz)
├── F01 Giriş Yap
├── F02 Hesap Oluştur
├── F03 Kullanıcı Türü Seçimi
├── F04 Telefon/E-posta Doğrulama
├── F05 Şifremi Unuttum
└── F06 İlk Araziyi Ekleme

App shell (oturumlu)
├── Genel bakış ........ F07
├── Araziler ........... F08 F09 F10 F11 F12
├── Veriler / ikiz ..... F13 F14 F15 F16 F17
├── Cihazlar ........... F18 F19 F20 F21
├── Laboratuvar ........ F22 F23 F24 F25
├── AI ................. F26 F27 F28
├── Sulama ............. F29
└── Merkez ............. F30 (rapor / uyarı / ayar)
```

**IA (ürün):** masaüstü sol menü — Genel bakış, Araziler, Veriler, Cihazlar, Lab, AI, Sulama, Merkez.  
**Mobil IA (5):** Özet · Araziler · Veriler · AI · Daha fazla.

**As-built (`AppShell`):** masaüstü — Genel Bakış, Araziler, Dijital İkiz, Cihazlar, Sensörler, Laboratuvar, AI Önerileri, Sulama, Raporlar (`/hub`), Arazi detay.  
Mobil alt bar — Ana Sayfa · Araziler · Sensör · AI · Diğer (`/hub` + lab/sulama). Seçili arazi yoksa farm-bağımlı linkler `/farms`’a düşer.

### 2.2. Yönetici paneli (`role=admin`)

Ayrı shell (`AdminShell`); çiftçi menüsü ile karışmaz. Rotalar `/admin/...`.

```text
A01 Genel bakış
A02 Kullanıcı yönetimi
A03 Çiftlik ve arazi yönetimi
A04 Sensör ve cihaz filosu
A05 Abonelik ve paketler
A06 Destek talepleri
A07 Sistem raporları ve analitik
A08 Sistem ayarları ve entegrasyonlar
```

**As-built:** A01–A08 rotaları + `AdminShell` menüsü mevcut. Admin değilse bootstrap (“Bu hesabı yönetici yap”) veya çiftçi paneline dönüş.

---

## 3. Ortak layout kalıpları

Referans: `designsystem.md` — App shell, PageHeader, SourceBadge, ConfirmGate.

### Auth shell

- Merkezlenmiş kart (max-width ~420px)
- Üstte marka adı (hero-level değil; sade logo + ürün adı)
- Tek kolon form; birincil CTA altta
- Alt linkler (kayıt / giriş / şifre)

### App shell

| Bölge | Masaüstü | Mobil |
|-------|----------|-------|
| Nav | Sol 240px | Alt bar 56px + “Daha fazla” sheet |
| Header | PageHeader + PrimaryAction | Başlık + ikon CTA |
| İçerik | 1–3 kolon grid | Tek kolon, 16px gutter |
| Context | Sağ panel (opsiyonel) | Alta yığılır |

### Durum matrisi (tüm ekranlar)

| Durum | Davranış |
|-------|----------|
| Empty | Açıklama + birincil CTA (boş beyaz ekran yok) |
| Loading | Skeleton veya spinner; layout kayması yok |
| Error | İnsan dili mesaj + yeniden dene |
| Stale | “Veri güncel değil” + zaman damgası |
| Forbidden | Yetkisiz; admin ekranlarında çiftçi yönlendirme yok |

---

## 4. Ekran envanteri (38)

### A. Çiftçi (30)

| ID | Ekran | MVP | Grup | As-built rota |
|----|-------|-----|------|---------------|
| F01 | Giriş Yap | ★ | Auth | `/login` |
| F02 | Hesap Oluştur | ★ | Auth | `/register` |
| F03 | Kullanıcı Türü Seçimi | | Auth | `/register/role` |
| F04 | Telefon/E-posta Doğrulama | | Auth | `/register/verify` (demo kod `123456`) |
| F05 | Şifremi Unuttum | | Auth | `/forgot-password` |
| F06 | İlk Araziyi Ekleme | ★ | Onboarding | `/farms/new` (arazi yokken yönlendirme) |
| F07 | Genel Bakış Dashboard | ★ | Genel | `/dashboard` |
| F08 | Arazilerim | ★ | Genel | `/farms` |
| F09 | Yeni Arazi Ekle | ★ | Genel | `/farms/new` |
| F10 | Arazi Düzenle | | Genel | `/farms/[id]/edit` |
| F11 | Arazi Detayı | ★ | Genel | `/farms/[id]` (hâlâ özet + kısayollar + kısmi monolit) |
| F12 | Arazi Bölgeleri Yönetimi | ★ | Genel | `/farms/[id]/zones` |
| F13 | Dijital İkiz Haritası | ★ | Veri | `/farms/[id]/twin` |
| F14 | Canlı Sensör Verileri | ★ | Veri | `/farms/[id]/sensors/live` |
| F15 | Geçmiş Veri Grafikleri | | Veri | `/farms/[id]/sensors/history` |
| F16 | Manuel Veri Girişi | ★ | Veri | `/farms/[id]/data/manual` |
| F17 | Veri Kaynakları Merkezi | ★ | Veri | `/farms/[id]/data/sources` |
| F18 | Sensör ve Cihazlar | ★ | IoT | `/farms/[id]/devices` |
| F19 | Yeni Cihaz Bağla | ★ | IoT | `/farms/[id]/devices/new` |
| F20 | Cihaz Detayı | | IoT | `/farms/[id]/devices/[deviceId]` |
| F21 | Cihaz Kurulum ve Kalibrasyon | | IoT | `/farms/[id]/devices/[deviceId]/calibrate` |
| F22 | Laboratuvar Analizleri | ★ | Lab | `/farms/[id]/lab` |
| F23 | Laboratuvar Raporu Yükle | ★ | Lab | `/farms/[id]/lab/new` |
| F24 | Analiz Değerlerini Doğrula | | Lab | `/farms/[id]/lab/[reportId]/verify` |
| F25 | Laboratuvar Analizi Detayı | | Lab | `/farms/[id]/lab/[reportId]` |
| F26 | AI Önerileri | ★ | AI | `/farms/[id]/ai` |
| F27 | AI Öneri Detayı ve Açıklaması | ★ | AI | `/farms/[id]/ai/[predictionId]` |
| F28 | Sulama Senaryo Simülatörü | ★ | AI | `/farms/[id]/scenarios` |
| F29 | Sulama Kontrol ve Planlama | ★ | Sulama | `/farms/[id]/irrigation` |
| F30 | Raporlar, Uyarılar ve Kullanıcı Ayarları Merkezi | | Merkez | `/farms/[id]/hub` |

★ = MVP-20 ürün önceliği (IA). Birçok ★ dışı ekranın da UI’si as-built’te vardır.

### B. Yönetici (8)

| ID | Ekran | Öncelik | As-built rota |
|----|-------|---------|---------------|
| A01 | Yönetim Paneli Genel Bakış | P2 | `/admin` |
| A02 | Kullanıcı Yönetimi | P2 | `/admin/users` |
| A03 | Çiftlik ve Arazi Yönetimi | P2 | `/admin/farms` |
| A04 | Sensör ve Cihaz Filosu Yönetimi | P2 | `/admin/devices` |
| A05 | Abonelik ve Paket Yönetimi | P2 | `/admin/billing` |
| A06 | Destek Talepleri | P2 | `/admin/support` |
| A07 | Sistem Raporları ve Analitik | P2 | `/admin/analytics` |
| A08 | Sistem Ayarları ve Entegrasyonlar | P2 | `/admin/settings` |

---

## 5. MVP-20 detay spesifikasyonları

Her ekran şablonu: amaç · birincil görev · giriş/çıkış · layout · bölümler · bileşenler · veri/etiket · durumlar · kullanılabilirlik · MVP notu.

---

### F01 — Giriş Yap ★

- **Amaç:** Kullanıcının hesabına güvenli giriş yapması.
- **Birincil görev:** E-posta + şifre ile oturum açmak.
- **Giriş / çıkış:** Landing `/` → F01; başarı → F07 (veya arazi yoksa F06); linkler → F02, F05.
- **Layout:** Auth shell; tek kolon.
- **Bölümler:** Marka satırı · form · birincil “Giriş yap” · alt linkler.
- **Bileşenler:** Input, Button primary, inline ErrorAlert, TextLink.
- **Veri / etiket:** Yok.
- **Durumlar:** loading (buton disabled) · invalid credentials · network error.
- **Kullanılabilirlik:** Label’lı alanlar; Enter gönderir; hata alanı form üstünde; dokunma ≥44px.
- **MVP notu:** Mevcut `/login`.

---

### F02 — Hesap Oluştur ★

- **Amaç:** Yeni çiftçi hesabı oluşturmak.
- **Birincil görev:** Ad, e-posta, şifre kaydı.
- **Giriş / çıkış:** F01 linki → F02; başarı → F06 (ilk arazi) veya F03 (P1); zaten hesap → F01.
- **Layout:** Auth shell.
- **Bölümler:** Başlık “Hesap oluştur” · form · CTA · “Giriş yap” linki.
- **Bileşenler:** Input (name, email, password), Button, ErrorAlert.
- **Veri / etiket:** Rol MVP’de varsayılan `farmer` (F03 sonra).
- **Durumlar:** email taken · weak password · loading.
- **Kullanılabilirlik:** Şifre min. uzunluk mesajı; spam submit engeli.
- **MVP notu:** Mevcut `/register`.

---

### F06 — İlk Araziyi Ekleme ★

- **Amaç:** Boş hesabı kullanılabilir hale getirmek; boş dashboard yok.
- **Birincil görev:** İlk arazi + ürün bilgisini kaydetmek.
- **Giriş / çıkış:** Kayıt/giriş sonrası arazi yoksa zorunlu; başarı → F11 veya F07.
- **Layout:** App shell sade (nav minimal) veya wizard tam genişlik.
- **Bölümler:** Adım göstergesi (1/1 MVP) · arazi formu · “Devam et”.
- **Bileşenler:** Form fields (ad, konum, alan, toprak tipi, sulama tipi, ürün, gelişim dönemi), PrimaryButton.
- **Veri / etiket:** Yok.
- **Durumlar:** validation · empty name blocked · success toast.
- **Kullanılabilirlik:** “Neden gerekli?” mikro metin; atlama yok (MVP).
- **MVP notu:** As-built `/farms/new` (`AppShell`); ayrı `/onboarding/farm` yok — arazi yokken dashboard/flows buraya yönlendirir.

---

### F07 — Genel Bakış Dashboard ★

- **Amaç:** Üç soruya tek bakışta cevap vermek.
- **Birincil görev:** Durumu anlamak ve bir sonraki aksiyona geçmek.
- **Giriş / çıkış:** Login sonrası varsayılan; CTA → F26, F29, F11, F14.
- **Layout:** App shell; masaüstü 3 kart yan yana; mobil stack.
- **Bölümler:**
  1. Toprağın durumu nasıl? (nem, risk badge, kaynak)
  2. Ne yapmalıyım? (sulama önerisi özeti)
  3. Neden? (kısa gerekçe + “Detay” → F27)
  4. Hızlı aksiyonlar (senaryo, sulama, veri gir)
- **Bileşenler:** StatusCard, RiskBadge, SourceBadge, ConfidenceMeter, Button group.
- **Veri / etiket:** Son okuma `source_type`; güven skoru.
- **Durumlar:** no farm → F06 · no reading → CTA F16 · stale · low confidence banner.
- **Kullanılabilirlik:** 3 soru testi geçmeli; risk yalnız renkle değil (metin).
- **MVP notu:** As-built `/dashboard` + `AppShell`; üç soru kartları + kaynak etiketi.

---

### F08 — Arazilerim ★

- **Amaç:** Kullanıcının arazilerini listelemek.
- **Birincil görev:** Arazi seçmek veya yeni eklemek.
- **Giriş / çıkış:** Nav → F08; kart → F11; CTA → F09.
- **Layout:** Kart grid (2–3 kolon desktop / 1 mobil).
- **Bölümler:** PageHeader + “Yeni arazi” · liste · empty state.
- **Bileşenler:** FarmCard (ad, konum, ürün, risk özeti), EmptyState.
- **Veri / etiket:** Opsiyonel son risk.
- **Durumlar:** empty · loading · error.
- **Kullanılabilirlik:** Kart tamamı tıklanabilir; silme bu ekranda yok (F10).
- **MVP notu:** As-built `/farms` liste/kart + empty → Yeni arazi.

---

### F09 — Yeni Arazi Ekle ★

- **Amaç:** Yeni arazi kaydı.
- **Birincil görev:** Formu doldurup kaydetmek.
- **Giriş / çıkış:** F08 / F06 → F09; başarı → F11.
- **Layout:** Form sayfası; max-width ~640px.
- **Bölümler:** Başlık · form grid · Kaydet / İptal.
- **Bileşenler:** Input, Select (toprak, sulama, ürün), Button.
- **Veri / etiket:** Yok.
- **Durumlar:** validation · API error.
- **Kullanılabilirlik:** Zorunlu alanlar `*`; iptal onay istemez (veri yoksa).
- **MVP notu:** Mevcut `/farms/new`.

---

### F11 — Arazi Detayı ★

- **Amaç:** Tek arazinin hub ekranı; alt ekranlara köprü.
- **Birincil görev:** Özeti görmek ve ilgili işe gitmek.
- **Giriş / çıkış:** F08 → F11; deep-link → F12, F13, F14, F16, F18, F22, F26, F28, F29.
- **Layout:** Header (ad, meta) · özet kartlar · link grid.
- **Bölümler:** Kimlik satırı · durum özeti · “Bölgeler / Sensör / Lab / AI / Sulama” kısayolları · son olaylar.
- **Bileşenler:** FarmHeader, SummaryTiles, NavTiles, SourceBadge.
- **Veri / etiket:** Son nem + kaynak.
- **Durumlar:** 404 farm · loading.
- **Kullanılabilirlik:** Hub aşırı uzun form olmamalı; monolit parçalanırken bu ekran ince kalır.
- **MVP notu:** As-built `/farms/[id]` hub + deep-link’ler; bir miktar eski monolit içerik hâlâ sayfada olabilir — birincil UX ayrı rotalarda (devices/lab/ai/irrigation/…).

---

### F12 — Arazi Bölgeleri Yönetimi ★

- **Amaç:** Yönetim bölgelerini tanımlamak (tek sensör ≠ tüm arazi).
- **Birincil görev:** Bölge eklemek / listelemek.
- **Giriş / çıkış:** F11 → F12; lab/IoT eşlemede zone seçimi.
- **Layout:** Liste + sağda veya altta ekleme formu.
- **Bölümler:** Açıklama mikro metni · zone list · “Bölge ekle”.
- **Bileşenler:** ZoneList, Form (name, notes), Button.
- **Veri / etiket:** `zone_id` ilişkisi.
- **Durumlar:** empty · duplicate name error.
- **Kullanılabilirlik:** Mikro metin: “Bölgeler toprak, eğim veya sulama hattına göre ayrılır.”
- **MVP notu:** As-built `/farms/[id]/zones`.

---

### F13 — Dijital İkiz Haritası ★

- **Amaç:** Sınırlı nem/risk görselleştirmesi (tam dijital ikiz değil).
- **Birincil görev:** Bölge riskini ve sensör konumunu görmek.
- **Giriş / çıkış:** F11 / Veriler nav → F13; pin → F14.
- **Layout:** Tam genişlik canvas + sağ/alt legend.
- **Bölümler:** Başlık + “Sınırlı dijital ikiz” etiketi · şematik bölge kutuları · legend · sensör pinleri.
- **Bileşenler:** ZoneMap (MVP CSS grid/SVG), RiskLegend, SensorPin, SourceBadge.
- **Veri / etiket:** Bölge risk renkleri (`designsystem` §20); simülasyon etiketi.
- **Durumlar:** no zones → CTA F12 · no data gri bölge.
- **Kullanılabilirlik:** Renk + metin legend; Leaflet OSM harita paneli as-built.
- **MVP notu:** As-built `/farms/[id]/twin` — Leaflet/OSM + şematik twin; uydu/ısı haritası yok.

---

### F14 — Canlı Sensör Verileri ★

- **Amaç:** Son dinamik ölçümleri göstermek.
- **Birincil görev:** Nem (yüzey/derin), sıcaklık, hava, zaman damgası okumak.
- **Giriş / çıkış:** F13 / F11 / F18 → F14; stale → F16 veya cihaz kontrolü.
- **Layout:** Metrik kart grid + meta satırı.
- **Bölümler:** Son güncelleme · metrikler · kaynak · “Manuel gir” / “Cihazlar”.
- **Bileşenler:** MetricCard, Timestamp, SourceBadge, StaleBanner.
- **Veri / etiket:** `soil_moisture`, `soil_moisture_deep`, depths; `is_validated`.
- **Durumlar:** empty · stale (&gt;1–2 saat) · unvalidated.
- **Kullanılabilirlik:** Birimler görünür (% VWC, °C); çift derinlik etiketi.
- **MVP notu:** As-built `/farms/[id]/sensors/live`; simülasyon etiketi + “IoT simülasyon” CTA.

---

### F16 — Manuel Veri Girişi ★

- **Amaç:** Kullanıcının nem ve çevre verisi girmesi.
- **Birincil görev:** Form kaydı + analiz tetikleme.
- **Giriş / çıkış:** F17 / F11 → F16; başarı → F26 veya F11.
- **Layout:** Form 2 kolon desktop / 1 mobil.
- **Bölümler:** SourceBadge `manual` · alanlar · Kaydet ve analiz et · IoT simülasyon (ayrı, etiketli).
- **Bileşenler:** Number inputs, Button primary/secondary, ErrorAlert.
- **Veri / etiket:** `source_type: manual` zorunlu görünür.
- **Durumlar:** validation range · API error · success → prediction.
- **Kullanılabilirlik:** Zorunlu nem/sıcaklık/yağış/son sulama; aralık mesajları Türkçe.
- **MVP notu:** As-built `/farms/[id]/data/manual`; `source_type: manual`.

---

### F17 — Veri Kaynakları Merkezi ★

- **Amaç:** Dört+ kaynağı bilinçli seçtirmek.
- **Birincil görev:** Kaynak seçip ilgili giriş ekranına gitmek.
- **Giriş / çıkış:** Veriler nav → F17; kartlar → F16, F18/simülasyon, test set, F22.
- **Layout:** Kaynak kartları 2×2.
- **Bölümler:** Açıklama · kartlar (Manuel, IoT simülasyon, Test seti, Laboratuvar, Saha IoT).
- **Bileşenler:** SourceCard (ikon, kısa açıklama, uyarı), asla “gerçek IoT” iddiası simülasyonda.
- **Veri / etiket:** Her kart `source_type` gösterir.
- **Durumlar:** Yok (statik seçici).
- **Kullanılabilirlik:** Simülasyon kartında sarı uyarı şeridi.
- **MVP notu:** As-built `/farms/[id]/data/sources`.

---

### F18 — Sensör ve Cihazlar ★

- **Amaç:** Arazi cihaz filosunu görmek ve yönetmeye giriş.
- **Birincil görev:** Cihaz listesini filtrelemek; yeni cihaz veya detaya gitmek.
- **Giriş / çıkış:** `AppShell` Cihazlar / F11 → F18; CTA → F19; satır → F20; canlı → F14.
- **Layout:** App shell; KPI özet + filtre + masaüstü tablo / mobil kartlar.
- **Bölümler:** FarmSelector · “Kaynak: simülasyon” rozeti · KPI (toplam/aktif/uyarı) · arama/filtre · liste · empty CTA.
- **Bileşenler:** KpiCard, DeviceRow/Card, status chips, Link FAB (mobil).
- **Veri / etiket:** Tüm cihaz verisi simülasyon; `GET /devices/{farm_id}`, `.../summary`.
- **Durumlar:** empty → F19 · offline/warning vurgusu · API error.
- **Kullanılabilirlik:** Offline satırlar görünür; simülasyon gerçek sensör iddiası yok.
- **MVP notu:** As-built `/farms/[id]/devices`.

---

### F19 — Yeni Cihaz Bağla ★

- **Amaç:** Simüle cihaz kaydı oluşturmak (Field Node Lite alanları).
- **Birincil görev:** 4 adımlı sihirbazı tamamlayıp cihaz kaydetmek.
- **Giriş / çıkış:** F18 → F19; başarı → F20.
- **Layout:** App shell; adım göstergeli form (tür → konum → ağ → onay).
- **Bölümler:** Tür/ad/seri · zone/bölge/derinlik · bağlantı/örnekleme · özet + simülasyon uyarısı.
- **Bileşenler:** Stepper, Select/Input, PrimaryButton; isteğe bağlı test-connection.
- **Veri / etiket:** `POST /devices`; ağ bilgisi saklanmaz; etiket `simulation`.
- **Durumlar:** validation · loading · API error.
- **Kullanılabilirlik:** Adımlar arasında geri; onay adımında kaynak etiketi zorunlu metin.
- **MVP notu:** As-built `/farms/[id]/devices/new`.

---

### F20 — Cihaz Detayı *(IA: MVP dışı; UI as-built)*

- **Rota / API:** `/farms/[id]/devices/[deviceId]` · detail + simülasyon ölçümü + bağlantı testi.
- **MVP notu:** As-built; `source_label: simulation`.

### F21 — Kurulum ve Kalibrasyon *(IA: MVP dışı; UI as-built)*

- **Rota / API:** `.../calibrate` · yazılım ofseti; sapma durumu.
- **MVP notu:** As-built; ofset simülasyon/ingest okumalarına uygulanır.

---

### F22 — Laboratuvar Analizleri ★

- **Amaç:** Lab raporlarını IoT’den ayrı listelemek.
- **Birincil görev:** Duruma göre filtreleyip rapor seçmek veya yeni yüklemek.
- **Giriş / çıkış:** Lab nav / F11 → F22; CTA → F23; satır → F25 veya F24.
- **Layout:** App shell; KPI + filtre + tablo/kart.
- **Bölümler:** “Lab ≠ IoT sensör” rozeti · KPI · durum filtresi · rapor listesi · empty.
- **Bileşenler:** KpiCard, status tone chips, Link “+ Rapor yükle”.
- **Veri / etiket:** `lab_report` / `lab_manual`; `GET /lab-reports/{farm_id}`, summary.
- **Durumlar:** empty · verified/pending/missing · error.
- **Kullanılabilirlik:** Lab sürekli sensör yerine geçmez mesajı.
- **MVP notu:** As-built `/farms/[id]/lab`.

---

### F23 — Laboratuvar Raporu Yükle ★

- **Amaç:** Dosya adı + parametre taslağı oluşturmak (gerçek OCR yok).
- **Birincil görev:** Meta + dosya/manuel parametre → taslak kayıt → doğrulamaya gitmek.
- **Giriş / çıkış:** F22 → F23; taslak sonrası → F24.
- **Layout:** Çok adımlı form (meta → parametreler → özet).
- **Bölümler:** Lab adı/tarih/derinlik/bölge · dosya upload veya demo extract · parametre satırları (değer+birim) · kaydet.
- **Bileşenler:** File input, extract-demo CTA, parameter editors, PrimaryButton.
- **Veri / etiket:** `POST upload`, `extract-demo` (simüle), `POST /lab-reports` draft; OCR değildir.
- **Durumlar:** validation · upload error · loading.
- **Kullanılabilirlik:** “Kullanıcı onayı olmadan doğrulanmış sayılmaz” uyarısı.
- **MVP notu:** As-built `/farms/[id]/lab/new`.

---

### F24 — Değerleri Doğrula *(IA: MVP dışı; UI as-built)*

- **Rota:** `/farms/[id]/lab/[reportId]/verify` · ConfirmGate → `user_confirmed`.
- **Not:** Simüle çıkarım; gerçek OCR değil.

### F25 — Analiz Detayı *(IA: MVP dışı; UI as-built)*

- **Rota:** `/farms/[id]/lab/[reportId]` · parametreler + insights; gübre reçetesi yok.

---

### F26 — AI Önerileri ★

- **Amaç:** Sulama kararının özet görünümü.
- **Birincil görev:** Öneriyi okuyup detay veya sulamaya geçmek.
- **Giriş / çıkış:** F07 / F11 / predict sonrası → F26; Detay → F27; Sulama → F29.
- **Layout:** Öneri kartı + CTA grubu.
- **Bölümler:** Karar (gerekli mi) · süre · risk · güven · kısa neden · aksiyonlar.
- **Bileşenler:** AIRecommendationCard, RiskBadge, ConfidenceMeter, Buttons.
- **Veri / etiket:** Prediction; güven &lt; 60 → “Otomasyon önerilmiyor”.
- **Durumlar:** no reading · low confidence · irrigation not needed.
- **Kullanılabilirlik:** Kesinlik iddiası yok (“öneriliyor”).
- **MVP notu:** As-built `/farms/[id]/ai`.

---

### F27 — AI Öneri Detayı ve Açıklaması ★

- **Amaç:** Açıklanabilir AI (`designsystem` §21).
- **Birincil görev:** Nedenleri ve 72s tahmini anlamak.
- **Giriş / çıkış:** F26 → F27; geri F26; opsiyonel ConfirmGate → sanal sulama.
- **Layout:** Açıklama listesi + nem tahmin şeridi + veri eksikleri.
- **Bölümler:** Karar özeti · “Bu karar neden?” · 24/48/72h · uyarılar.
- **Bileşenler:** ExplainList, MoistureForecast, WarningList, Confirm modal.
- **Veri / etiket:** explanation, moisture_24/48/72h.
- **Durumlar:** low confidence panel · missing weather note.
- **Kullanılabilirlik:** En etkili faktörler numaralı liste; jargon yok.
- **MVP notu:** As-built `/farms/[id]/ai/[predictionId]`.

---

### F28 — Sulama Senaryo Simülatörü ★

- **Amaç:** Alternatifleri karşılaştırmak.
- **Birincil görev:** Senaryoları çalıştırıp önerileni görmek.
- **Giriş / çıkış:** F11 / F26 → F28; önerilen → F29.
- **Layout:** CTA “Senaryoları çalıştır” · karşılaştırma tablosu.
- **Bölümler:** Açıklama · tablo (nem, su, risk, stres, sonuç) · önerilen satır vurgusu.
- **Bileşenler:** ScenarioTable, RecommendedHighlight, Button.
- **Veri / etiket:** Mevcut nem referansı.
- **Durumlar:** no reading disabled · loading · error.
- **Kullanılabilirlik:** Mobilde yatay scroll veya kart yığını; önerilen metinle işaretli.
- **MVP notu:** As-built `/farms/[id]/scenarios`.

---

### F29 — Sulama Kontrol ve Planlama ★

- **Amaç:** Sanal vanayı güvenli kontrol etmek.
- **Birincil görev:** Onayla sulamayı başlatmak / durumu izlemek.
- **Giriş / çıkış:** F26 / F28 → F29; geçmiş aynı ekranda.
- **Layout:** Durum paneli · birincil CTA · geçmiş listesi · ConfirmModal.
- **Bölümler:** Vana durumu · süre/su tahmini · “Sulamayı başlat” · geçmiş.
- **Bileşenler:** ValveStatus, ConfirmGate modal, HistoryList, disabled CTA if !canIrrigate.
- **Veri / etiket:** `user_approved=true` API; confidence gate.
- **Durumlar:** blocked low confidence · not recommended · running · completed.
- **Kullanılabilirlik:** Modal metni süre + sonucu açıklar; vazgeç kolay.
- **MVP notu:** As-built `/farms/[id]/irrigation`.

---

## 6. Kalan 18 — kısa spesifikasyon

### Çiftçi (10)

| ID | Amaç | Birincil CTA | Rota iskeleti | Öncelik |
|----|------|--------------|---------------|---------|
| F03 | Rol seç | Devam | `/register/role` *(as-built)* | P1 |
| F04 | E-posta doğrula | Doğrula | `/register/verify` *(as-built; demo `123456`)* | P2 |
| F05 | Şifre sıfırlama | Link gönder | `/forgot-password` *(as-built)* | P1 |
| F10 | Arazi düzenle | Kaydet | `/farms/[id]/edit` *(as-built)* | P1 |
| F15 | Geçmiş ölçümler | Aralık | `/farms/[id]/sensors/history` *(as-built; tablo)* | P1 |
| F20 | Cihaz detayı | Test / kalibre | `/farms/[id]/devices/[deviceId]` *(as-built)* | P1 |
| F21 | Kalibrasyon ofseti | Kaydet | `.../calibrate` *(as-built)* | P2 |
| F24 | Lab değer onay | Onayla | `.../lab/[reportId]/verify` *(as-built)* | P1 |
| F25 | Lab detay | Aç | `.../lab/[reportId]` *(as-built)* | P1 |
| F30 | Rapor/uyarı/ayar hub | Sekme | `/farms/[id]/hub` *(as-built)* | P1 |

### Yönetici (8)

| ID | Amaç | Birincil CTA | Rota | Öncelik |
|----|------|--------------|------|---------|
| A01 | Platform KPI özeti | Kullanıcı / cihaz sayıları | `/admin` | P2 |
| A02 | Kullanıcı listele / rol / askıya al | Kullanıcı aç | `/admin/users` | P2 |
| A03 | Tüm çiftlikler arası arazi yönetimi | Arazi aç | `/admin/farms` | P2 |
| A04 | Cihaz filosu sağlık | Offline filtrele | `/admin/devices` | P2 |
| A05 | Abonelik paketleri | Paket düzenle | `/admin/billing` | P2 |
| A06 | Destek ticket | Yanıtla | `/admin/support` | P2 |
| A07 | Sistem analitikleri | Rapor indir | `/admin/analytics` | P2 |
| A08 | Entegrasyonlar (Supabase, MQTT, hava) | Kaydet | `/admin/settings` | P2 |

Admin UX: tablo ağırlıklı; çiftçi “3 soru” dilinden farklı, operasyonel ton. Çiftçi verisine admin erişimi denetim logu ile (ileride).

---

## 7. Rota / App Router eşlemesi

Kaynak: `frontend/src/app/**/page.tsx` + `AppShell` / `AdminShell` (as-built).

### Bugün (kod) — çiftçi / auth

| Rota | Ekran |
|------|-------|
| `/` | Landing |
| `/login` | F01 |
| `/register` | F02 |
| `/register/role` | F03 |
| `/register/verify` | F04 |
| `/forgot-password` | F05 |
| `/dashboard` | F07 |
| `/farms` | F08 |
| `/farms/new` | F09 (+ F06 onboarding rolü) |
| `/farms/[id]` | F11 (hub; kısmi legacy içerik kalabilir) |
| `/farms/[id]/edit` | F10 |
| `/farms/[id]/zones` | F12 |
| `/farms/[id]/twin` | F13 |
| `/farms/[id]/sensors/live` | F14 |
| `/farms/[id]/sensors/history` | F15 |
| `/farms/[id]/data/manual` | F16 |
| `/farms/[id]/data/sources` | F17 |
| `/farms/[id]/devices` | F18 |
| `/farms/[id]/devices/new` | F19 |
| `/farms/[id]/devices/[deviceId]` | F20 |
| `/farms/[id]/devices/[deviceId]/calibrate` | F21 |
| `/farms/[id]/lab` | F22 |
| `/farms/[id]/lab/new` | F23 |
| `/farms/[id]/lab/[reportId]/verify` | F24 |
| `/farms/[id]/lab/[reportId]` | F25 |
| `/farms/[id]/ai` | F26 |
| `/farms/[id]/ai/[predictionId]` | F27 |
| `/farms/[id]/scenarios` | F28 |
| `/farms/[id]/irrigation` | F29 |
| `/farms/[id]/hub` | F30 |
| `/subscription` | Abonelik plan seçimi (ödeme yok; F30/hub’dan link) |

### Bugün (kod) — yönetici

| Rota | Ekran |
|------|-------|
| `/admin` | A01 |
| `/admin/users` | A02 |
| `/admin/farms` | A03 |
| `/admin/devices` | A04 |
| `/admin/billing` | A05 |
| `/admin/support` | A06 |
| `/admin/analytics` | A07 |
| `/admin/settings` | A08 |

> MVP-20 rota ayrıştırması **büyük ölçüde tamam**. Ayrı `/onboarding/farm` yok (F06 = `/farms/new`). F11 üzerinde sınırlı legacy içerik kalabilir; birincil akışlar ayrı rotalarda.

---

## 8. Boş / yükleme / hata / yetkisiz matrisi

| Ekran grubu | Empty | Stale | Low confidence | Yetkisiz |
|-------------|-------|-------|----------------|----------|
| Auth | — | — | — | — |
| Dashboard / AI | Veri gir CTA | Banner | Otomasyon kapalı | — |
| Sensör / canlı | Cihaz bağla veya manuel | “Güncel değil” | — | Başka kullanıcı farm 404 |
| Lab | Rapor yükle | Eski rapor notu | — | — |
| Sulama | Öneri yok mesajı | — | CTA disabled | — |
| Admin | “Kayıt yok” | — | — | `role!=admin` → 403 / login |

---

## 9. Kullanılabilirlik kabul kriterleri

Doküman envanteri + as-built uyumu (ürün/UX kabulü; canlı prod URL ayrı):

- [x] 38 ekran envanterde; mobil ayrı sayılmıyor.
- [x] MVP-20’nin her biri layout + durum + CTA içeriyor (doküman + çoğu as-built rota).
- [x] Dashboard 3 soru çerçevesi as-built `/dashboard`.
- [x] Kaynak etiketi veri yüzeylerinde (manuel / simulation / lab) — bileşen adı `SourceBadge` olmayabilir; metin/rozet var.
- [x] Simülasyon “gerçek sensör” demiyor (copy + etiket).
- [x] Lab: birim + onay (`verify` / `user_confirmed`).
- [x] Sulama: ConfirmGate + güven &lt; 60 engeli (as-built F29/F27).
- [x] F13 sınırlı dijital ikiz (`/twin`).
- [x] Admin ayrı rol/shell (A01–A08 `/admin` + `AdminShell`).
- [ ] Dokunma alanı ≥ 44px tutarlılığı (tasarım hedefi; görsel QA kalan).
- [x] Empty / error / loading matris §8 + ekran notlarında tanımlı.

---

## 10. Sonraki adım (kod — kalan, doküman dışı)

Zaten mevcut: `AppShell` / `AdminShell`, MVP-20+ ayrık rotalar (devices, lab, ai, irrigation, twin, zones, sources, hub), admin A01–A08.

Kalan iyileştirmeler (opsiyonel):

1. F11 legacy monolit içeriğini tamamen temizlemek (deep-link hub’a indirgeme).
2. Twin’de risk ısı haritası / poligon çizimi — P2.
3. Ortak `SourceBadge` bileşenine konsolidasyon (metin rozetleri as-built’te dağınık).
4. Sunum provası; prod sertleştirme (Sentry/SMTP).

Bağlayıcı durum: [`Progress.md`](Progress.md). Tasarım token’ları: [`designsystem.md`](designsystem.md).
