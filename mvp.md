# AGRITWIN AI — MVP DOKÜMANI

> **Kapsam notu:** Bu doküman MVP hedefini tanımlar. Bağlayıcı uygulama durumu için `Progress.md` ve çalışan kod (`frontend/`, `backend/`) esas alınır. Uydu, drone, **gübre reçetesi**, verim MVP dışıdır. Laboratuvar raporu IoT’nin yerini almaz; P1’de tamamlayıcı veri kaynağıdır (`veri-mimarisi.md`).

## 1. MVP Adı

**AgriTwin AI MVP**

### Kısa Tanım

AgriTwin AI MVP; çiftçinin manuel olarak girdiği arazi, ürün ve toprak verilerini, IoT/bulut sistemlerinden simüle edilen sensör verilerini, hazır test veri setlerini ve (P1) laboratuvar analiz sonuçlarını tek platformda birleştirerek sulama ihtiyacını, kuruma riskini ve sensör anomalilerini yapay zekâ ile analiz eden; farklı sulama senaryolarını simüle eden ve sanal sulama otomasyonu sunan web tabanlı çalışan prototiptir.

---

## 2. MVP’nin Temel Amacı

MVP’nin amacı, toprağın bütün fiziksel, kimyasal ve biyolojik yapısını modellemek değildir.

İlk sürüm şu soruya cevap vermelidir:

> Bu arazi şu anda sulanmalı mı, ne kadar süre sulanmalı ve bu kararın gerekçesi nedir?

Bu nedenle MVP yalnızca şu kullanım alanına odaklanacaktır:

> **Toprak nemi ve sulama kararına odaklanan dijital ikiz prototipi**

---

## 3. Çözülen Problem

Çiftçiler sulama kararlarını çoğu zaman:

- Gözleme,
- Kişisel deneyime,
- Sabit sulama saatlerine,
- Genel hava tahminlerine,
- Tek ölçümlük verilere

göre vermektedir.

Bu durum:

- Gereğinden fazla su kullanımına,
- Yetersiz sulamaya,
- Enerji maliyetinin artmasına,
- Bitki stresine,
- Toprak yapısının bozulmasına,
- Verim kaybına

neden olabilir.

### MVP’nin çözdüğü net problem

> Kullanıcıya ait arazi ve ürün verileri ile toprak nemi, sıcaklık, yağış ihtimali ve sulama geçmişi birlikte değerlendirilemediği için sulama kararları eksik bilgiye dayanmaktadır.

---

## 4. MVP Kapsamı

### MVP’de bulunacak özellikler

1. Kullanıcı kayıt ve giriş sistemi
2. Arazi oluşturma
3. Ürün bilgisi ekleme
4. Manuel veri girişi
5. IoT/bulut veri akışı simülasyonu
6. Test veri seti ile sistem testi
7. Veri doğrulama
8. Yapay zekâ destekli sulama ihtiyacı tahmini
9. 24, 48 ve 72 saatlik nem tahmini
10. Risk sınıflandırması
11. Sensör anomalisi tespiti
12. Açıklanabilir AI önerisi
13. Sulama senaryo simülasyonu
14. Sanal vana/pompa otomasyonu
15. Sulama geçmişi
16. Su kullanımı ve tahmini tasarruf raporu
17. Canlıya alınmış web uygulaması

---

## 5. MVP Dışında Bırakılan Özellikler

İlk sürümde aşağıdaki özellikler geliştirilmeyecektir:

- Gerçek uydu görüntüsü analizi
- Drone görüntüsü analizi
- Gerçek zamanlı pH kalibrasyonu
- Gübre optimizasyonu
- Hastalık tespiti
- Verim tahmini
- Erozyon analizi
- Toprağın tam biyolojik modeli
- Çoklu çiftlik kurumsal paneli
- Gerçek tarla robotu
- Tam otomatik sulama
- Gelişmiş dijital ikiz simülasyon motoru

Bu özellikler yol haritasında gösterilecek ancak MVP’ye dahil edilmeyecektir.

---

## 6. Hedef Kullanıcı

### Birincil kullanıcı

- Küçük ve orta ölçekli çiftçi
- Sera üreticisi
- Damla sulama sistemi kullanan üretici
- Dijital tarıma açık erken kullanıcı

### İkincil kullanıcı

- Ziraat mühendisi
- Tarım danışmanı
- Kooperatif yöneticisi
- Tarımsal pilot proje ekibi

---

## 7. Kullanıcı Akışı

### Adım 1 — Kayıt

Kullanıcı:

- Ad soyad
- E-posta
- Şifre
- Kullanıcı tipi

bilgilerini girer.

### Adım 2 — Arazi oluşturma

Kullanıcı:

- Arazi adı
- Konum
- Alan büyüklüğü
- Arazi türü
- Toprak türü
- Sulama sistemi

bilgilerini girer.

### Adım 3 — Ürün bilgisi ekleme

Kullanıcı:

- Ürün türü
- Ekim tarihi
- Gelişim dönemi
- Tahmini hasat tarihi

bilgilerini girer.

### Adım 4 — Veri kaynağı seçme

Kullanıcı şu kaynaklardan veri ekler (birden fazla kaynak birleşebilir):

- Manuel veri girişi
- IoT/bulut bağlantısı (MVP: simülasyon)
- Demo/test veri seti
- Laboratuvar analizi (P1: rapor yükleme veya manuel lab girişi)

Ayrıntılı mimari: `veri-mimarisi.md`

### Adım 5 — Analiz

Sistem:

- Veriyi doğrular.
- Sulama ihtiyacını tahmin eder.
- Risk seviyesini belirler.
- 72 saatlik nem tahmini üretir.
- Açıklanabilir öneri gösterir.

### Adım 6 — Senaryo simülasyonu

Kullanıcı:

- Şimdi sulama
- 12 saat sonra sulama
- 24 saat sonra sulama
- Sulama yapmama

senaryolarını karşılaştırır.

### Adım 7 — Otomasyon

Kullanıcı öneriyi onaylarsa:

- Sanal vana açılır.
- Sulama süresi başlar.
- Tahmini su kullanımı hesaplanır.
- Yeni nem değeri sisteme aktarılır.
- Sistem yeniden analiz yapar.

---

## 8. Veri Kaynakları

AgriTwin AI dört veri giriş yolunu hedefler. IoT laboratuvarın yerine geçmez.

Ayrıntı: [`veri-mimarisi.md`](veri-mimarisi.md)

### 8.1. Manuel veri girişi

Kullanıcı şu verileri girebilir:

- Toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Hava nemi
- pH
- EC
- Tuzluluk
- Son sulama tarihi
- Son sulama süresi
- Kullanılan su miktarı
- Yağış ihtimali

Tüm alanlar zorunlu olmayacaktır.

Eksik veri olduğunda sistem:

- Veri güven skorunu düşürür.
- Kullanıcıya eksik alanları gösterir.
- Analizin sınırlı olduğunu belirtir.

---

### 8.2. IoT/bulut veri akışı simülasyonu

Gerçek sistemde veriler şu kaynaklardan alınabilir:

- Toprak nem sensörü
- Toprak sıcaklık sensörü
- Hava sıcaklığı ve nem sensörü
- pH sensörü
- EC sensörü
- Debi sensörü
- ESP32
- MQTT
- LoRa
- Wi-Fi
- IoT bulut platformu

MVP’de bu entegrasyon simüle edilecektir.

Sistem:

- IoT cihazı bağlıymış gibi veri alır.
- Belirli aralıklarla kontrollü veri gönderir.
- Son veri zamanını gösterir.
- Cihaz bağlantı durumunu gösterir.
- Veri kesintisini tespit eder.

### Örnek IoT cihaz kartı

| Cihaz | Durum | Son Veri |
|---|---|---|
| Nem Sensörü 01 | Aktif | %34 |
| Toprak Sıcaklık Sensörü | Aktif | 24.2°C |
| pH Sensörü | Simülasyon | 6.8 |
| Sulama Vanası | Beklemede | Kapalı |

---

### 8.3. Test veri seti

Ekip tarafından önceden hazırlanmış test senaryoları kullanılacaktır.

#### Test senaryoları

1. Normal toprak durumu
2. Kuruma riski
3. Aşırı sulama riski
4. Sensör anomalisi
5. Tuzluluk riski
6. Sulama sonrası beklenmeyen değişim

Bu veriler:

- Model testi
- Demo
- Kullanıcı akışı
- Risk analizi
- Senaryo karşılaştırması

için kullanılacaktır.

---

### 8.4. Laboratuvar analizleri (P1)

IoT ile sürekli güvenilir ölçülmeyen parametreler laboratuvar raporu veya manuel lab girişi ile eklenir:

- pH, EC / toplam tuz, organik madde, kireç, fosfor, potasyum (MVP lab paketi)
- Her parametrede **değer + birim + (mümkünse) yöntem + derinlik + tarih** zorunlu
- Rapor yükleme (PDF/JPG/PNG/Excel/CSV) veya form ile manuel giriş
- Otomatik OCR varsa yalnızca öneri üretir; **kullanıcı onayı olmadan kaydedilmez**
- Gübre reçetesi üretilmez — yalnızca sulama bağlamında yorum / eksik veri uyarısı

Detay: `veri-mimarisi.md` §3–4.

---

## 9. Gerekli Veriler

### Zorunlu veriler

- Toprak nemi
- Hava sıcaklığı
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama zamanı

### İkinci seviye veriler

- Toprak sıcaklığı
- Hava nemi
- Sulama süresi
- Arazi büyüklüğü
- Sulama yöntemi
- Son su miktarı

### Opsiyonel veriler

- pH
- EC
- Tuzluluk
- Organik madde
- Fosfor / potasyum / kireç (laboratuvar; birimli)
- NPK değerleri (gelişmiş paket — P2)

---

## 10. Yapay Zekânın MVP’deki Görevleri

### 10.1. Sulama ihtiyacı tahmini

Model şu sorulara cevap verir:

- Sulama gerekli mi?
- Sulama ertelenebilir mi?
- Kaç saat içinde sulama gerekebilir?
- Tahmini sulama süresi nedir?

### Girdiler

- Toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama zamanı
- Nem değişim eğilimi

### Çıktılar

- Sulama gerekli / değil
- Risk seviyesi
- Tahmini sulama süresi
- Güven skoru
- Açıklama

---

### 10.2. Nem tahmini

Sistem:

- 24 saat
- 48 saat
- 72 saat

sonraki nem seviyesini tahmin eder.

### Örnek çıktı

| Zaman | Tahmini Nem |
|---|---:|
| Şimdi | %34 |
| 24 saat sonra | %29 |
| 48 saat sonra | %25 |
| 72 saat sonra | %21 |

---

### 10.3. Risk sınıflandırması

Risk seviyeleri:

- Düşük
- Orta
- Yüksek
- Kritik

Risk türleri:

- Kuruma riski
- Aşırı sulama riski
- Bitki su stresi
- Sensör arızası
- Veri yetersizliği

---

### 10.4. Anomali tespiti

Sistem şu durumları tespit eder:

- Nem değerinde ani sıçrama
- Gerçekçi olmayan pH değeri
- Sulama sonrası nem artmaması
- Veri akışının kesilmesi
- Aynı sensörden çelişkili ölçüm gelmesi

---

### 10.5. Senaryo analizi

Kullanıcı şu senaryoları karşılaştırabilir:

- Şimdi sulama
- 12 saat bekleme
- 24 saat bekleme
- Sulama süresini azaltma
- Sulama süresini artırma
- Sulama yapmama

Her senaryo için:

- Tahmini nem
- Risk seviyesi
- Su kullanımı
- Beklenen sonuç

gösterilir.

---

### 10.6. Açıklanabilir öneri

Sistem yalnızca “sula” demeyecektir.

### Örnek

> Sulama öneriliyor. Çünkü toprak nemi %28 seviyesinde, son 24 saatte %7 düştü, hava sıcaklığı yüksek ve önümüzdeki 48 saat içinde yağış beklenmiyor.

---

## 11. Otomasyonun MVP’deki Görevleri

Otomasyon katmanı:

- IoT verisini belirli aralıklarla çeker.
- Veriyi günceller.
- Kritik durumda bildirim üretir.
- Kullanıcı onayı sonrası sanal vanayı açar.
- Sulama süresini başlatır.
- Sulamayı durdurur.
- Kullanılan suyu kaydeder.
- Yeni nem değerini sisteme aktarır.
- AI analizini yeniden başlatır.

### Örnek iş akışı

1. Veri alınır.
2. Veri doğrulanır.
3. AI analiz yapar.
4. Sulama önerisi oluşur.
5. Kullanıcı onay verir.
6. Sanal vana açılır.
7. Sulama süresi tamamlanır.
8. İşlem kaydedilir.
9. Yeni veri alınır.
10. Sistem yeniden analiz yapar.

---

## 12. MVP Ekranları

> **Ekran envanteri:** Toplam **38** ana ekran (30 çiftçi + 8 yönetici). Mobil ayrı sayılmaz.  
> Öncelikli prototip: **20 ekran**. Tam UX/UI: [`ekran-haritasi.md`](ekran-haritasi.md) · token’lar: [`designsystem.md`](designsystem.md).  
> **As-built:** Çoğu F/A ekranı ayrı App Router sayfasıdır (`ekran-haritasi.md` §7); admin `/admin/*`.

### 12.0. MVP öncelikli 20

Giriş · Hesap oluştur · İlk arazi · Dashboard · Arazilerim · Yeni arazi · Arazi detayı · Bölgeler · Dijital ikiz haritası (sınırlı) · Canlı sensör · Manuel veri · Veri kaynakları · Cihazlar · Yeni cihaz · Lab listesi · Lab yükle · AI önerileri · AI detay · Senaryo simülatörü · Sulama kontrolü.

### 12.1. Kayıt ve giriş

- Ad soyad
- E-posta
- Şifre
- Kullanıcı tipi

### 12.2. Arazi oluşturma

- Arazi adı
- Konum
- Alan
- Toprak türü
- Sulama tipi
- Ürün türü

### 12.3. Veri kaynağı seçimi

- Manuel veri
- IoT/bulut
- Test verisi
- Laboratuvar analizi (P1)

### 12.3b. Toprak Analizi Ekle (P1)

- Rapor yükle / manuel lab sonucu
- Laboratuvar adı, tarihler, derinlik, bölge
- Temel parametreler + birim
- “Belgeden çıkarılan değerleri kontrol edin” onayı

### 12.4. Dashboard

- Mevcut nem
- Sıcaklık
- Yağış ihtimali
- Risk seviyesi
- AI önerisi
- Güven skoru
- Son güncelleme

### 12.5. Dijital ikiz ekranı

- Toprak nem durumu
- Tarla bölge görünümü
- 72 saatlik tahmin
- Risk alanları
- Sensör durumu

### 12.6. AI öneri ekranı

- Karar
- Gerekçe
- Güven skoru
- Eksik veriler
- Risk açıklaması

### 12.7. Senaryo ekranı

- Şimdi sulama
- Bekleme
- Sulama yapmama
- Süre değiştirme
- Sonuç karşılaştırma

### 12.8. IoT cihaz ekranı

- Cihaz adı
- Bağlantı durumu
- Son veri zamanı
- API durumu
- Aktif/pasif

### 12.9. Sulama otomasyonu

- Vana durumu
- Pompa durumu
- Başlat
- Durdur
- Sulama süresi
- Su miktarı

### 12.10. Raporlama

- Su kullanımı
- Sulama geçmişi
- Nem değişimi
- AI öneri geçmişi
- Tahmini su tasarrufu

---

## 13. MVP Teknik Mimarisi

### Frontend

- Next.js veya React
- Alternatif hızlı çözüm: Streamlit

### Backend

- Python
- FastAPI

### Veritabanı

- Supabase
- PostgreSQL
- Alternatif: SQLite

### Yapay zekâ

- Random Forest
- XGBoost
- Regresyon
- Isolation Forest

### IoT simülasyonu

- MQTT
- REST API
- Zamanlanmış Python scripti

### Canlıya alma

- Frontend: Vercel
- Backend: Render veya Railway
- Veritabanı: Supabase

---

## 14. Veri Tabanı Şeması

### Users

- id
- name
- email
- password_hash
- role

### Farms

- id
- user_id
- name
- location
- area
- soil_type
- irrigation_type

### Crops

- id
- farm_id
- crop_type
- planting_date
- growth_stage

### SensorReadings

- id
- farm_id
- source_type
- timestamp
- soil_moisture
- soil_temperature
- air_temperature
- air_humidity
- ph
- ec
- salinity
- rainfall_probability

### Predictions

- id
- farm_id
- irrigation_needed
- irrigation_duration
- risk_level
- confidence_score
- explanation

### IrrigationEvents

- id
- farm_id
- start_time
- duration
- water_amount
- status

### Devices

- id
- farm_id
- device_name
- device_type
- connection_status
- last_data_time

---

## 15. Model Geliştirme Yaklaşımı

### Aşama 1 — Kural tabanlı motor

İlk çalışan sürüm için:

- Nem düşük
- Sıcaklık yüksek
- Yağış ihtimali düşük
- Son sulama eski

ise sulama önerisi üretilir.

Bu bölüm güvenlik ve başlangıç mantığı için kullanılacaktır.

### Aşama 2 — Test verisi ile makine öğrenmesi

Ekip tarafından hazırlanan veri setiyle:

- Random Forest
- XGBoost
- Regresyon

modelleri eğitilir.

### Aşama 3 — Hibrit karar yapısı

En doğru MVP yapısı:

> Kural tabanı + makine öğrenmesi + güvenlik sınırları

---

## 16. Demo Senaryosu

### Demo başlangıcı

Kullanıcı “Domates Serası” adlı araziyi oluşturur.

### Veri kaynağı

IoT/bulut seçilir.

### Gelen test verileri

- Toprak nemi: %34
- Toprak sıcaklığı: 25°C
- Hava sıcaklığı: 33°C
- Hava nemi: %42
- Yağış ihtimali: %5
- Son sulama: 36 saat önce

### AI çıktısı

> Kuruma riski yüksek. Önümüzdeki 18 saat içinde sulama öneriliyor.

### Senaryo 1 — 24 saat bekleme

- Tahmini nem: %24
- Risk: Kritik
- Bitki stresi: Yüksek

### Senaryo 2 — Şimdi sulama

- Tahmini sulama süresi: 14 dakika
- Tahmini su kullanımı: 90 litre
- Sulama sonrası nem: %46
- Risk: Düşük

### Otomasyon

- Kullanıcı “Sulamayı Başlat” butonuna basar.
- Sanal vana açılır.
- Süre başlar.
- İşlem kaydedilir.
- Nem verisi güncellenir.
- Sistem yeniden analiz yapar.

---

## 17. Başarı Kriterleri

### Teknik başarı

- Kullanıcı kayıt akışı çalışıyor mu?
- Arazi oluşturma çalışıyor mu?
- Manuel veri girişi çalışıyor mu?
- IoT simülasyon verisi geliyor mu?
- AI tahmini üretilebiliyor mu?
- Senaryo simülasyonu çalışıyor mu?
- Sanal otomasyon tetikleniyor mu?
- Veriler veritabanına kaydediliyor mu?
- Uygulama canlıda erişilebilir mi?

### Model başarısı

- Sulama ihtiyacı sınıflandırma doğruluğu
- Nem tahmin hatası
- Anomali tespit başarısı
- Güven skorunun tutarlılığı

### Kullanıcı deneyimi başarısı

- Kullanıcı sistemi yardımsız kullanabiliyor mu?
- Öneriyi anlayabiliyor mu?
- Veri kaynağını seçebiliyor mu?
- Senaryoları karşılaştırabiliyor mu?
- Sulama işlemini başlatabiliyor mu?

### Çevresel başarı

- Tahmini su tasarrufu
- Gereksiz sulamanın önlenmesi
- Sulama karar süresinin azalması

---

## 18. Ekip Görev Dağılımı

### Frontend sorumlusu

- Kayıt ekranları
- Dashboard
- Senaryo ekranı
- IoT cihaz ekranı

### Backend sorumlusu

- API
- Veritabanı
- Kullanıcı yönetimi
- Veri akışı

### AI/veri sorumlusu

- Test veri seti
- Model eğitimi
- Risk sınıflandırması
- Açıklanabilir öneri

### IoT/otomasyon sorumlusu

- IoT veri simülasyonu
- MQTT veya REST akışı
- Sanal vana
- Sulama olayları

### Ürün ve sunum sorumlusu

- Kullanıcı senaryosu
- İş modeli
- Demo akışı
- Jüri sunumu

---

## 19. MVP Geliştirme Sırası

### 1. Aşama

- Kullanıcı kayıt
- Arazi oluşturma
- Manuel veri girişi

### 2. Aşama

- Veritabanı
- Dashboard
- Veri doğrulama

### 3. Aşama

- Test veri seti
- Kural tabanlı öneri motoru
- İlk AI tahmini

### 4. Aşama

- 72 saatlik nem tahmini
- Risk sınıflandırması
- Açıklanabilir öneri

### 5. Aşama

- IoT veri akışı simülasyonu
- Cihaz yönetim ekranı

### 6. Aşama

- Senaryo simülasyonu
- Sanal sulama otomasyonu

### 7. Aşama

- Canlıya alma
- Test
- Demo senaryosu
- Hata düzeltme

---

## 20. MVP Sonrası Yol Haritası

### Faz 2

- Gerçek sensör bağlantısı
- Gerçek hava durumu API’si
- Pilot sera testi
- Gerçek sulama otomasyonu

### Faz 3

- pH ve EC analizi
- Tuzluluk riski
- Toprak sağlık puanı

### Faz 4

- Uydu ve drone entegrasyonu
- Verim tahmini
- Gübreleme önerisi

### Faz 5

- Çoklu tarla yönetimi
- Kooperatif paneli
- Kurumsal kullanım
- Bölgesel tarım karar sistemi

---

## 21. MVP’nin Tek Cümlelik Tanımı

> AgriTwin AI MVP, çiftçinin manuel verilerini ve IoT/bulut sistemlerinden gelen sensör verilerini birleştirerek sulama ihtiyacını ve toprak risklerini yapay zekâ ile tahmin eden, farklı sulama kararlarını simüle eden ve sanal sulama otomasyonu sunan canlı web prototipidir.

---

## 22. Kritik Stratejik Not

MVP’nin amacı “tam dijital ikiz yaptık” demek değildir.

Doğru iddia şudur:

> AgriTwin AI MVP, toprağın nem ve sulama davranışına odaklanan sınırlı fakat çalışan bir dijital ikiz prototipidir.

Bu yaklaşım:

- Daha gerçekçidir.
- Daha savunulabilirdir.
- Daha hızlı geliştirilebilir.
- Jüriye çalışan demo sunmayı mümkün kılar.
- Yapay zekâ ve otomasyon ayrımını net biçimde gösterir.