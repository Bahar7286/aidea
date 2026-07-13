# AGRITWIN AI — DESIGN SYSTEM

## 1. Doküman Amacı

Bu doküman, AgriTwin AI ürününün tüm ekranlarında tutarlı, erişilebilir ve kullanıcı dostu bir görsel dil oluşturmak için hazırlanmıştır.

### Uygulanan tokenlar (mevcut kod)

`frontend/src/app/globals.css` içinde:

- `--primary: #2e7d32`
- `--risk-low / --risk-medium / --risk-high / --risk-critical`
- `.card`, `.btn`, `.input` yardımcı sınıfları

Aşağıdaki bölümlerin çoğu hedef tasarım sistemidir; shadcn/ui ve Recharts henüz eklenmemiştir.

Tasarım sistemi şu alanları kapsar:

- Marka kimliği
- Renk paleti
- Tipografi
- Boşluk sistemi
- Grid yapısı
- İkonografi
- Form bileşenleri
- Kartlar
- Tablolar
- Grafikler
- Uyarılar
- Risk seviyeleri
- IoT cihaz durumları
- AI öneri bileşenleri
- Dijital ikiz ekranları
- **Ekran haritası ve app shell** (detay: [`ekran-haritasi.md`](ekran-haritasi.md))
- Erişilebilirlik kuralları
- Responsive tasarım
- UX yazım dili
- Tasarım tokenları

---

## 2. Tasarım Vizyonu

AgriTwin AI’ın tasarımı şu üç temel ilkeye dayanmalıdır:

1. **Sade**
2. **Güvenilir**
3. **Veri odaklı**

Kullanıcıya karmaşık tarım ve sensör verileri gösterilirken teknik karmaşa yaratılmamalıdır.

Ana ekran şu üç soruya hızlı cevap vermelidir:

1. Toprağın durumu nasıl?
2. Ne yapmalıyım?
3. Neden yapmalıyım?

---

## 3. Marka Karakteri

AgriTwin AI markası şu özellikleri taşımalıdır:

- Bilimsel
- Sürdürülebilir
- Güven veren
- Yenilikçi
- Tarım odaklı
- Teknolojik
- Açıklanabilir
- Kullanıcı dostu

### Kaçınılması gereken marka algıları

- Aşırı futuristik
- Soğuk ve mekanik
- Fazla kurumsal
- Karmaşık
- Tarımdan kopuk
- Yapay zekâyı abartan

---

## 4. Logo Kullanımı

### Ana logo yapısı

- AgriTwin AI yazısı
- Toprak, yaprak, sensör veya dijital ikiz çağrışımı
- Basit ve ölçeklenebilir ikon
- Açık ve koyu zemin kullanımına uygun varyantlar

### Logo kuralları

- Logo oranı değiştirilmemeli.
- Logo üzerine efekt uygulanmamalı.
- Düşük kontrastlı zeminde kullanılmamalı.
- Minimum boşluk korunmalı.
- İkon tek başına favicon ve uygulama simgesi olarak kullanılabilir.

### Minimum boyut

- Web tam logo: 120 px genişlik
- İkon logo: 24 px
- Mobil başlık: 96 px genişlik

---

## 5. Renk Sistemi

Renk sistemi tarım ve teknoloji temasını birlikte yansıtmalıdır.

## 5.1. Ana renkler

### Primary Green

- Hex: `#2E7D32`
- Kullanım: Ana butonlar, aktif durumlar, marka vurgusu

### Primary Green Dark

- Hex: `#1B5E20`
- Kullanım: Hover, aktif menü, koyu vurgular

### Primary Green Light

- Hex: `#E8F5E9`
- Kullanım: Arka plan, seçili alanlar, bilgi kartları

---

## 5.2. İkincil renkler

### Soil Brown

- Hex: `#6D4C41`
- Kullanım: Toprak verileri, arazi bileşenleri

### Earth Sand

- Hex: `#D7CCC8`
- Kullanım: Yardımcı arka planlar

### Sky Blue

- Hex: `#1976D2`
- Kullanım: IoT bağlantıları, hava durumu, bilgi durumları

### Water Blue

- Hex: `#0288D1`
- Kullanım: Sulama, su tüketimi, nem grafikleri

---

## 5.3. Nötr renkler

### Neutral 900

- Hex: `#1F2937`
- Kullanım: Ana metin

### Neutral 700

- Hex: `#374151`
- Kullanım: İkincil başlık

### Neutral 500

- Hex: `#6B7280`
- Kullanım: Yardımcı metin

### Neutral 300

- Hex: `#D1D5DB`
- Kullanım: Kenarlık

### Neutral 100

- Hex: `#F3F4F6`
- Kullanım: Hafif arka plan

### Neutral 50

- Hex: `#F9FAFB`
- Kullanım: Sayfa arka planı

### White

- Hex: `#FFFFFF`

---

## 5.4. Durum renkleri

### Success

- Hex: `#2E7D32`
- Kullanım: Normal toprak durumu, başarılı işlem

### Warning

- Hex: `#F9A825`
- Kullanım: Orta risk, veri eksikliği

### Error

- Hex: `#C62828`
- Kullanım: Kritik risk, sensör hatası

### Info

- Hex: `#1565C0`
- Kullanım: Bilgilendirme, IoT durumu

---

## 6. Risk Renkleri

Risk sistemi yalnızca renk ile anlatılmamalıdır. Metin ve ikon da kullanılmalıdır.

| Risk | Renk | Hex | İkon |
|---|---|---|---|
| Düşük | Yeşil | `#2E7D32` | Check Circle |
| Orta | Sarı | `#F9A825` | Alert Triangle |
| Yüksek | Turuncu | `#EF6C00` | Alert Circle |
| Kritik | Kırmızı | `#C62828` | X Circle |

### Kullanım örneği

**Kuruma Riski: Yüksek**

- Turuncu etiket
- Uyarı ikonu
- Kısa açıklama
- Önerilen aksiyon

---

## 7. Tipografi

## 7.1. Ana yazı tipi

### Inter

Kullanım alanları:

- Başlıklar
- Menü
- Kartlar
- Formlar
- Dashboard

### Alternatif

- Manrope
- Roboto
- Source Sans 3

### Karar

> Ana yazı tipi olarak Inter kullanılmalıdır.

---

## 7.2. Yazı boyutları

| Stil | Boyut | Satır Yüksekliği | Ağırlık |
|---|---:|---:|---:|
| Display | 40 px | 48 px | 700 |
| H1 | 32 px | 40 px | 700 |
| H2 | 24 px | 32 px | 700 |
| H3 | 20 px | 28 px | 600 |
| H4 | 18 px | 26 px | 600 |
| Body Large | 16 px | 24 px | 400 |
| Body | 14 px | 22 px | 400 |
| Small | 12 px | 18 px | 400 |
| Label | 12 px | 16 px | 600 |
| Caption | 11 px | 16 px | 400 |

---

## 8. Boşluk Sistemi

8 px tabanlı sistem kullanılmalıdır.

| Token | Değer |
|---|---:|
| space-1 | 4 px |
| space-2 | 8 px |
| space-3 | 12 px |
| space-4 | 16 px |
| space-5 | 24 px |
| space-6 | 32 px |
| space-7 | 40 px |
| space-8 | 48 px |
| space-9 | 64 px |

### Kullanım ilkesi

- Kart iç boşluğu: 16–24 px
- Sayfa bölümleri: 24–32 px
- Form alanları arası: 16 px
- Başlık ve açıklama arası: 8 px

---

## 9. Border Radius

| Token | Değer | Kullanım |
|---|---:|---|
| radius-sm | 6 px | Input, küçük etiket |
| radius-md | 10 px | Buton, kart |
| radius-lg | 16 px | Büyük panel |
| radius-xl | 24 px | Dashboard hero alanı |
| radius-full | 999 px | Badge, avatar |

---

## 10. Gölge Sistemi

### Shadow Small

```css
0 1px 2px rgba(0, 0, 0, 0.06)
```

### Shadow Medium

```css
0 4px 12px rgba(0, 0, 0, 0.08)
```

### Shadow Large

```css
0 12px 32px rgba(0, 0, 0, 0.12)
```

### Kullanım

- Küçük kartlarda hafif gölge
- Modal ve dialoglarda orta gölge
- Büyük açılır panellerde yüksek gölge

---

## 11. Grid Sistemi

### Masaüstü

- 12 kolon
- Maksimum genişlik: 1440 px
- Sayfa yan boşluk: 32 px

### Tablet

- 8 kolon
- Yan boşluk: 24 px

### Mobil

- 4 kolon
- Yan boşluk: 16 px

### Dashboard yerleşimi

- Sol menü: 240 px
- Ana içerik: esnek
- Sağ yardımcı panel: opsiyonel 320 px

---

## 12. Navigasyon

## 12.1. Masaüstü menü

Menü öğeleri:

- Dashboard
- Arazilerim
- Veri Kaynakları
- Dijital İkiz
- AI Önerileri
- Senaryolar
- Sulama
- Cihazlar
- Raporlar
- Ayarlar

### Aktif durum

- Açık yeşil arka plan
- Koyu yeşil ikon
- Kalın metin

---

## 12.2. Mobil navigasyon

Alt menü:

- Ana Sayfa
- Araziler
- AI
- Sulama
- Profil

---

## 13. Butonlar

## 13.1. Primary Button

Kullanım:

- Kaydet
- Analiz Et
- Sulamayı Başlat
- Arazi Ekle

Stil:

- Arka plan: Primary Green
- Metin: White
- Hover: Primary Green Dark
- Radius: 10 px
- Min height: 44 px

---

## 13.2. Secondary Button

Kullanım:

- Senaryo Karşılaştır
- Veriyi Yenile
- Cihaz Test Et

Stil:

- Beyaz arka plan
- Yeşil kenarlık
- Yeşil metin

---

## 13.3. Destructive Button

Kullanım:

- Sil
- Otomasyonu Durdur
- Cihaz Bağlantısını Kaldır

Stil:

- Kırmızı arka plan
- Beyaz metin

---

## 13.4. Ghost Button

Kullanım:

- Detay
- Düzenle
- Geçmişi Gör

---

## 14. Form Bileşenleri

### Form ilkeleri

- Etiket her zaman input üzerinde yer almalı.
- Placeholder, etiket yerine kullanılmamalı.
- Zorunlu alanlar `*` ile belirtilmeli.
- Hata mesajı input altında gösterilmeli.
- Birim bilgisi görünür olmalı.

### Örnek

**Toprak Nemi**

`[ 34 ] %`

### Input durumları

- Default
- Focus
- Filled
- Error
- Disabled
- Read-only

---

## 15. Select ve Dropdown

Kullanım alanları:

- Toprak türü
- Ürün türü
- Gelişim dönemi
- Sulama tipi
- Veri kaynağı

### Kurallar

- Arama desteği olmalı.
- Seçim sonrası değer görünür kalmalı.
- Çok uzun listelerde kategori kullanılmalı.

---

## 16. Kart Sistemi

## 16.1. Metric Card

Kullanım:

- Toprak nemi
- Hava sıcaklığı
- Yağış ihtimali
- Risk seviyesi

İçerik:

- Başlık
- Ana değer
- Birim
- Trend
- Durum etiketi

---

## 16.2. AI Recommendation Card

İçerik:

- AI önerisi
- Risk seviyesi
- Güven skoru
- Kararın gerekçesi
- Önerilen aksiyon

Örnek:

**Sulama Öneriliyor**

Toprak nemi %28 seviyesinde ve son 24 saatte %7 düştü.

- Güven skoru: %86
- Önerilen süre: 14 dakika
- Risk: Yüksek

---

## 16.3. Device Card

İçerik:

- Cihaz adı
- Cihaz tipi
- Bağlantı durumu
- Son veri zamanı
- Son değer
- Durum etiketi

---

## 16.4. Scenario Card

İçerik:

- Senaryo adı
- Tahmini nem
- Su kullanımı
- Risk
- Önerilen/önerilmeyen etiketi

---

## 17. Durum Etiketleri

### Veri Kaynağı Etiketleri

- Manuel
- IoT
- IoT Simülasyonu
- Test Verisi
- Dosya Yükleme

### Cihaz Durumları

- Aktif
- Pasif
- Bağlı
- Bağlantı Kesildi
- Veri Bekleniyor
- Simülasyon

### AI Durumları

- Analiz Hazır
- Veri Yetersiz
- Düşük Güven
- Yeniden Analiz Gerekli
- Kritik Uyarı

---

## 18. IoT Cihaz Durumu Renkleri

| Durum | Renk |
|---|---|
| Aktif | Yeşil |
| Pasif | Gri |
| Bağlantı Kesildi | Kırmızı |
| Veri Bekleniyor | Sarı |
| Simülasyon | Mavi |

---

## 19. Grafik Sistemi

### Kullanılacak grafikler

- Çizgi grafik
- Alan grafik
- Bar grafik
- Gauge
- Isı haritası
- Senaryo karşılaştırma grafiği

### Grafik renkleri

- Nem: Water Blue
- Sıcaklık: Turuncu
- Yağış: Sky Blue
- Risk: Risk renkleri
- Sulama: Primary Green

### Kurallar

- En fazla 4 ana veri serisi
- Açıklama ve birim görünür olmalı
- Tooltip kullanılmalı
- Mobilde yatay kaydırma veya sadeleştirme yapılmalı
- Renk dışında çizgi biçimi veya ikon desteği olmalı

---

## 20. Dijital İkiz Görselleştirmesi

Dijital ikiz ekranı yalnızca grafiklerden oluşmamalıdır.

### Gösterilecek bileşenler

- Tarla bölge görünümü
- Nem yoğunluk katmanı
- Risk bölgeleri
- Sensör konumları
- Sulama alanları
- 72 saatlik tahmin
- Senaryo öncesi/sonrası karşılaştırması

### Bölge renkleri

- Sağlıklı: Yeşil
- İzlenmeli: Sarı
- Kuruma riski: Turuncu
- Kritik: Kırmızı
- Veri yok: Gri

---

## 21. AI Açıklanabilirlik Bileşeni

Kullanıcı AI kararının nedenini anlayabilmelidir.

### Gösterilecek bilgiler

- Karar
- Güven skoru
- En etkili 3 faktör
- Veri eksikleri
- Risk seviyesi
- Kullanıcının yapabileceği aksiyon

### Örnek

**Bu karar neden verildi?**

1. Toprak nemi düşük
2. Son 24 saatte hızlı nem kaybı var
3. Yağış beklenmiyor

---

## 22. Uyarı Sistemi

### Bilgi Uyarısı

Mavi ton

Örnek:

> IoT verisi 10 dakika önce güncellendi.

### Başarı Uyarısı

Yeşil ton

Örnek:

> Sulama başarıyla tamamlandı.

### Uyarı

Sarı ton

Örnek:

> Veri güven skoru düşük. pH ve EC verileri eksik.

### Kritik Uyarı

Kırmızı ton

Örnek:

> Sensör anomalisi tespit edildi.

---

## 23. Modal ve Dialog

Kullanım alanları:

- Sulamayı başlatma onayı
- Cihaz silme
- Arazi silme
- Kritik uyarı
- Veri kaynağı değiştirme

### Kurallar

- Başlık net olmalı.
- Riskli işlem açıklanmalı.
- Birincil ve ikincil aksiyon ayrılmalı.
- Kapatma seçeneği görünür olmalı.

---

## 24. Tablo Sistemi

Kullanım alanları:

- Sensör verileri
- Sulama geçmişi
- AI tahmin geçmişi
- Cihaz listesi
- Test senaryoları

### Özellikler

- Sıralama
- Filtreleme
- Arama
- Sayfalama
- CSV dışa aktarma
- Durum etiketleri

---

## 25. Empty State

Veri olmadığında boş ekran gösterilmemelidir.

### Örnek

**Henüz sensör verisi yok**

Bir veri kaynağı bağlayın veya manuel veri girin.

Butonlar:

- Veri Gir
- IoT Bağla
- Demo Senaryosu Kullan

---

## 26. Loading State

### Kullanım

- Dashboard yüklenirken
- AI analiz edilirken
- IoT bağlantısı test edilirken
- Senaryo simüle edilirken

### Bileşenler

- Skeleton
- Progress bar
- Spinner
- Durum mesajı

### Örnek mesaj

> Toprak verileri analiz ediliyor...

---

## 27. Error State

Hata mesajı teknik olmamalıdır.

### Kötü örnek

`500 Internal Server Error`

### Doğru örnek

> Veriler şu anda analiz edilemedi. Lütfen bağlantınızı kontrol edip tekrar deneyin.

---

## 28. Responsive Tasarım

### Mobil

- Kartlar tek kolon
- Grafikler sadeleştirilmiş
- Alt navigasyon
- Büyük dokunma alanları
- Formlar tek kolon

### Tablet

- Kartlar iki kolon
- Menü daraltılabilir
- Grafikler esnek

### Masaüstü

- 3–4 kolon dashboard
- Sabit sol menü
- Detaylı grafikler
- Yan bilgi paneli

### Mobil ≠ ayrı ekran

Mobil görünümler [`ekran-haritasi.md`](ekran-haritasi.md) envanterinde **ayrı ekran olarak sayılmaz**; aynı F/A kimliğinin responsive varyasyonudur. Toplam ana ekran sayısı **38** (30 çiftçi + 8 yönetici).

---

## 28A. Ekran haritası, app shell ve sayfa iskeleti

Tam envanter, MVP-20 UX spesifikasyonları ve rota eşlemesi: [`ekran-haritasi.md`](ekran-haritasi.md).

### App shell — çiftçi

| Bölge | Masaüstü | Mobil |
|-------|----------|-------|
| Birincil nav | Sol sidebar ~240px (`AppShell`) | Alt bar ~56px, 5 öğe |
| Nav öğeleri (IA hedef) | Genel bakış, Araziler, Veriler, Cihazlar, Lab, AI, Sulama, Merkez | Özet, Araziler, Veriler, AI, Daha fazla |
| Nav öğeleri (as-built) | Genel Bakış, Araziler, Dijital İkiz, Cihazlar, Sensörler, Laboratuvar, AI Önerileri, Sulama, Raporlar (`/hub`), Arazi detay | Ana Sayfa, Araziler, Sensör, AI, Diğer |
| İçerik padding | 24–32px | 16px |
| Max content | 1200px (formlar 640–720px) | Tam genişlik |

### App shell — yönetici

- Ayrı `/admin` shell (`AdminShell`); çiftçi alt nav’ı kullanılmaz.
- Sol menü (as-built): Genel Bakış, Kullanıcılar, Çiftlikler, Cihaz filosu, Abonelik, Destek, Raporlar, Ayarlar.
- Mobil alt: Özet · Çiftlik · Cihaz · Diğer.
- Tablo ve filtre odaklı; “3 soru” dashboard dili zorunlu değil.
- Admin değilse bootstrap CTA veya çiftçi paneline dönüş.

### Sayfa iskeleti (PageHeader kalıbı)

```text
┌ PageHeader ─────────────────────────────┐
│ Başlık · kısa alt metin · PrimaryAction │
├─────────────────────────────────────────┤
│ Content (1–3 kolon)                     │
│ [opsiyonel ContextPanel]                │
└─────────────────────────────────────────┘
```

- Her sayfada **tek birincil CTA**.
- Empty / loading / error durumları `ekran-haritasi.md` §8 ile uyumlu.
- Arazi bağlamı gereken sayfalarda breadcrumb: Arazilerim → {Arazi} → {Ekran}.

### SourceBadge (veri kaynağı etiketi)

Tüm sensör, AI ve canlı veri yüzeylerinde zorunlu. As-built’te ad çoğu yerde inline rozet/metin (`Kaynak: simulation` vb.); ortak bileşen adı şart değil.

| `source_type` | Etiket (TR) | Görsel ipucu |
|---------------|-------------|--------------|
| `manual` | Manuel giriş | Nötr |
| `simulation` | IoT simülasyonu | Uyarı tonu (sarı/amber) — asla “gerçek sensör” |
| `test_dataset` | Test veri seti | Nötr / bilgi |
| `iot` | Saha IoT | Birincil yeşil |
| `lab_report` / `lab_manual` | Laboratuvar | Bilgi tonu; “Lab ≠ IoT” |

### ConfirmGate (onay kapısı)

Kritik aksiyonlarda modal zorunlu (as-built: F29 sulama, F27 detay sulama, F24 lab verify):

1. **Sulama başlat** — süre, beklenen nem etkisi, vazgeç; API `user_approved=true`.
2. **Lab kaydı** — “Değerleri ve birimleri doğruladım”; `user_confirmed` olmadan kayıt yok.
3. Güven skoru &lt; 60 iken sulama birincil CTA **disabled** + kısa gerekçe.

Dijital ikiz görselleştirme kuralları: §20. AI açıklama: §21.

---

## 29. Erişilebilirlik

### Temel kurallar

- Minimum kontrast oranı WCAG AA
- Sadece renkle bilgi verilmemeli
- Tüm inputlarda label olmalı
- Klavye ile erişim desteklenmeli
- Focus görünür olmalı
- İkonların açıklaması olmalı
- Minimum dokunma alanı 44x44 px
- Grafiklerde metin alternatifi bulunmalı

---

## 30. UX Yazım Dili

### Ton

- Açık
- Kısa
- Yargılamayan
- Teknik ama anlaşılır
- Güven veren

### Kaçınılması gereken dil

- Kesinlik iddiası
- Tehditkâr dil
- Fazla teknik jargon
- Kullanıcıyı suçlayan mesajlar

### Doğru örnek

> Toprak nemi düşük. Önümüzdeki 18 saat içinde sulama öneriliyor.

### Yanlış örnek

> Sulama yapmazsanız ürününüz zarar görecek.

---

## 31. Mikro Metinler

### Başarılı işlem

> Arazi başarıyla oluşturuldu.

### Düşük güven

> Analiz sınırlı veriyle oluşturuldu.

### Veri eksikliği

> Daha doğru analiz için pH ve EC verilerini ekleyebilirsiniz.

### IoT simülasyonu

> Bu veri akışı demo amacıyla simüle edilmektedir.

### Sulama onayı

> Sulamayı 14 dakika boyunca başlatmak istiyor musunuz?

---

## 32. Tasarım Tokenları

### Renk Tokenları

```css
--color-primary: #2E7D32;
--color-primary-dark: #1B5E20;
--color-primary-light: #E8F5E9;

--color-soil: #6D4C41;
--color-sand: #D7CCC8;
--color-water: #0288D1;
--color-sky: #1976D2;

--color-success: #2E7D32;
--color-warning: #F9A825;
--color-error: #C62828;
--color-info: #1565C0;

--color-neutral-900: #1F2937;
--color-neutral-700: #374151;
--color-neutral-500: #6B7280;
--color-neutral-300: #D1D5DB;
--color-neutral-100: #F3F4F6;
--color-neutral-50: #F9FAFB;
--color-white: #FFFFFF;
```

### Spacing Tokenları

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 40px;
--space-8: 48px;
--space-9: 64px;
```

### Radius Tokenları

```css
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 16px;
--radius-xl: 24px;
--radius-full: 999px;
```

---

## 33. Örnek Tailwind Ayarları

```js
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: "#2E7D32",
        dark: "#1B5E20",
        light: "#E8F5E9",
      },
      soil: "#6D4C41",
      water: "#0288D1",
      sky: "#1976D2",
      warning: "#F9A825",
      danger: "#C62828",
    },
    borderRadius: {
      sm: "6px",
      md: "10px",
      lg: "16px",
      xl: "24px",
    },
  },
}
```

---

## 34. Ana Ekran Hiyerarşisi

### Üst alan

- Arazi adı
- Veri kaynağı
- Son güncelleme
- Risk durumu

### Birinci bölüm

- Toprak nemi
- AI önerisi
- Sulama ihtiyacı
- Güven skoru

### İkinci bölüm

- 72 saatlik tahmin
- Sensör durumları
- Yağış ihtimali

### Üçüncü bölüm

- Senaryo simülasyonu
- Sulama otomasyonu
- Geçmiş işlemler

---

## 35. Tasarım Kalite Kontrol Listesi

- [ ] Renkler tokenlardan geliyor
- [ ] Tipografi tutarlı
- [ ] Riskler yalnızca renkle gösterilmiyor
- [ ] Input etiketleri var
- [ ] Mobil görünüm test edildi
- [ ] AI kararının nedeni görünür
- [ ] IoT simülasyonu etiketi var
- [ ] Kritik aksiyonlarda onay var
- [ ] Empty state tasarlandı
- [ ] Error state tasarlandı
- [ ] Loading state tasarlandı
- [ ] Kontrast kontrolü yapıldı
- [ ] Buton yükseklikleri en az 44 px
- [ ] Grafiklerde birim ve açıklama var
- [ ] Veri kaynağı açıkça gösteriliyor

---

## 36. Sonuç

AgriTwin AI tasarım sistemi, tarım verilerini teknik karmaşa yaratmadan kullanıcıya sunmayı amaçlar.

Ekran envanteri ve UX spesifikasyonları: [`ekran-haritasi.md`](ekran-haritasi.md) (38 ekran; MVP öncelikli 20).

Tasarımın başarısı şu soruya bağlıdır:

> Kullanıcı ana ekrana baktığında toprağın durumunu, ne yapması gerektiğini ve bu kararın nedenini birkaç saniye içinde anlayabiliyor mu?

Cevap evetse tasarım sistemi görevini yerine getiriyor demektir.