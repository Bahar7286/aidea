# AGRITWIN AI — PRODUCT REQUIREMENTS DOCUMENT (PRD)

## 1. Doküman Bilgileri

- **Ürün Adı:** AgriTwin AI
- **Doküman Türü:** Product Requirements Document (PRD)
- **Sürüm:** v1.0
- **Ürün Aşaması:** MVP / Çalışabilir Prototip
- **Ana Odak:** Toprak nemi ve sulama kararına odaklanan dijital ikiz
- **Hedef Platform:** Web uygulaması
- **Birincil Kullanıcı:** Çiftçi / sera üreticisi
- **İkincil Kullanıcı:** Ziraat mühendisi / tarım danışmanı

---

## 2. Ürün Özeti

AgriTwin AI; çiftçinin manuel olarak girdiği arazi, ürün ve toprak verilerini, IoT ve bulut sistemlerinden otomatik olarak alınan veya prototipte simüle edilen sensör verilerini ve ekip tarafından hazırlanmış test veri setlerini tek platformda birleştiren yapay zekâ destekli tarım karar sistemidir.

Ürün, toprağın mevcut durumunu dijital ortamda temsil eder, nem değişimini tahmin eder, sulama ihtiyacını analiz eder, riskleri sınıflandırır, farklı sulama senaryolarını karşılaştırır ve kullanıcı onayıyla sanal veya gerçek sulama otomasyonunu tetikler.

MVP’nin temel iddiası:

> AgriTwin AI, toprağın nem ve sulama davranışına odaklanan sınırlı fakat çalışan bir dijital ikiz prototipidir.

---

## 3. Problem Tanımı

Çiftçiler sulama kararlarını çoğunlukla:

- Kişisel deneyime,
- Gözleme,
- Sabit sulama takvimlerine,
- Genel hava tahminlerine,
- Tek seferlik ölçümlere

dayanarak vermektedir.

Bu yaklaşım:

- Gereğinden fazla su kullanımına,
- Yetersiz sulamaya,
- Bitki su stresine,
- Enerji maliyetinin artmasına,
- Toprak sağlığının bozulmasına,
- Verim kaybına

neden olabilir.

### Gerçek problem

> Çiftçi; toprak, ürün, hava ve sulama verilerini tek sistemde birleştirerek gelecekteki nem durumunu ve farklı sulama kararlarının sonuçlarını görebileceği güvenilir bir karar destek sistemine sahip değildir.

---

## 4. Ürün Vizyonu

AgriTwin AI’ın uzun vadeli vizyonu, tarım arazilerinin fiziksel, kimyasal ve biyolojik durumunu sürekli temsil eden, farklı tarımsal kararları uygulamadan önce simüle eden ve kaynak kullanımını optimize eden bütünleşik bir tarım dijital ikiz platformu oluşturmaktır.

MVP aşamasında bu vizyonun yalnızca sulama ve toprak nemi bileşeni geliştirilecektir.

---

## 5. Ürün Hedefleri

### Birincil hedefler

1. Kullanıcının arazi, ürün ve toprak verilerini sisteme girebilmesini sağlamak.
2. IoT ve bulut sistemlerinden veri geliyormuş gibi çalışan kontrollü bir veri akışı sunmak.
3. Kullanıcı verilerini doğrulamak ve veri güven skoru üretmek.
4. Sulama ihtiyacını tahmin etmek.
5. 24, 48 ve 72 saatlik nem tahmini sunmak.
6. Kuruma, aşırı sulama ve sensör anomalisi risklerini sınıflandırmak.
7. Kullanıcıya açıklanabilir AI önerisi göstermek.
8. Farklı sulama senaryolarını karşılaştırmak.
9. Kullanıcı onayıyla sanal sulama otomasyonu başlatmak.
10. Uygulamayı canlıya alınmış ve çalışan bir prototip olarak sunmak.

### İkincil hedefler

- Kullanıcının geçmiş sulama kayıtlarını görüntüleyebilmesi
- Tahmini su kullanımını ve tasarrufu görebilmesi
- Sensör bağlantı durumlarını takip edebilmesi
- Eksik veya hatalı veri durumunda uyarı alabilmesi

---

## 6. Hedef Dışı Kapsam

MVP’de aşağıdaki özellikler bulunmayacaktır:

- Gerçek uydu görüntüsü analizi
- Drone görüntüsü analizi
- Hastalık ve zararlı tespiti
- Gübre optimizasyonu / gübre reçetesi
- Verim tahmini
- Gerçek zamanlı pH/EC kalibrasyonu (sürekli IoT iddiası)
- Tam biyolojik toprak modeli
- Otonom tarla robotu
- Tam otomatik sulama
- Çoklu kooperatif yönetimi
- Kurumsal gelişmiş raporlama
- Gerçek saha için mevzuat ve sertifikasyon süreçleri

---

## 7. Kullanıcı Personaları

### Persona 1 — Küçük ve Orta Ölçekli Çiftçi

**İhtiyaçları:**

- Sulama zamanını doğru belirlemek
- Su ve enerji maliyetini azaltmak
- Karmaşık olmayan bir arayüz kullanmak
- Verinin ne anlama geldiğini anlayabilmek

**Sorunları:**

- Teknik verileri yorumlayamama
- Sensör maliyeti
- İnternet erişimi
- Sisteme güven problemi

### Persona 2 — Sera Üreticisi

**İhtiyaçları:**

- Nem değişimini sık takip etmek
- Bitki gelişim dönemine uygun sulama yapmak
- Otomasyon kullanmak
- Sulama geçmişini görmek

### Persona 3 — Ziraat Mühendisi / Tarım Danışmanı

**İhtiyaçları:**

- Birden fazla arazinin verisini görmek
- Çiftçiye veri temelli öneri sunmak
- Riskleri erken fark etmek
- Veri güvenilirliğini kontrol etmek

---

## 8. Temel Kullanıcı Hikâyeleri

### Kayıt ve arazi yönetimi

- Bir kullanıcı olarak hesap oluşturmak istiyorum, böylece kendi arazilerimi yönetebilirim.
- Bir çiftçi olarak arazi bilgilerini girmek istiyorum, böylece analizler arazime özel yapılabilsin.
- Bir kullanıcı olarak ürün türünü ve gelişim dönemini seçmek istiyorum, böylece sulama önerileri daha doğru olsun.

### Veri girişi

- Bir çiftçi olarak sensör verilerini manuel girmek istiyorum.
- Bir kullanıcı olarak IoT/bulut veri kaynağı bağlamak istiyorum.
- Bir jüri veya test kullanıcısı olarak hazır demo veri setini seçmek istiyorum.

### Analiz

- Bir kullanıcı olarak toprağın mevcut nem durumunu görmek istiyorum.
- Bir kullanıcı olarak 72 saatlik nem tahminini görmek istiyorum.
- Bir kullanıcı olarak sulama gerekli mi sorusuna net cevap almak istiyorum.
- Bir kullanıcı olarak AI kararının nedenini görmek istiyorum.

### Senaryo simülasyonu

- Bir kullanıcı olarak şimdi sulama ile 24 saat bekleme seçeneklerini karşılaştırmak istiyorum.
- Bir kullanıcı olarak farklı sulama sürelerinin etkisini görmek istiyorum.

### Otomasyon

- Bir kullanıcı olarak AI önerisini onaylayıp sulamayı başlatmak istiyorum.
- Bir kullanıcı olarak sanal vananın durumunu görmek istiyorum.
- Bir kullanıcı olarak sulama geçmişini incelemek istiyorum.

---

## 9. Fonksiyonel Gereksinimler

## 9.1. Kimlik Doğrulama

### Gereksinimler

- Kullanıcı kayıt olabilmeli.
- Kullanıcı giriş yapabilmeli.
- Kullanıcı güvenli şekilde çıkış yapabilmeli.
- Şifreler hashlenerek saklanmalı.
- Kullanıcı rolü kaydedilmeli.

### Kabul kriterleri

- Geçerli e-posta ile kayıt tamamlanmalı.
- Aynı e-posta ile ikinci hesap açılamamalı.
- Hatalı girişte kullanıcı uyarılmalı.

---

## 9.2. Arazi Yönetimi

### Gereksinimler

Kullanıcı şu bilgileri girebilmeli:

- Arazi adı
- Konum
- Alan büyüklüğü
- Arazi türü
- Toprak türü
- Sulama sistemi
- Ürün türü
- Ekim tarihi
- Gelişim dönemi

### Kabul kriterleri

- Kullanıcı en az bir arazi oluşturabilmeli.
- Arazi bilgileri düzenlenebilmeli.
- Eksik zorunlu alanlarda kayıt engellenmeli.

---

## 9.3. Veri Kaynağı Seçimi

### Gereksinimler

Platform şu veri kaynaklarını desteklemelidir (birleştirilebilir):

- Manuel veri
- IoT/bulut bağlantısı (MVP: simülasyon)
- Test/demo veri seti
- Laboratuvar analizi (rapor yükleme veya manuel lab girişi) — P1

Kaynak etiketi UI ve API’de görünür olmalıdır (`source_type`).

Mimari referans: `veri-mimarisi.md`

### Kabul kriterleri

- Seçilen / aktif veri kaynakları dashboard üzerinde görünmeli.
- Kullanıcı birden fazla kaynaktan veri ekleyebilmeli.
- Yeni veri geldiğinde sistem yeniden analiz edebilmeli.
- Laboratuvar kaydı kullanıcı onayı olmadan otomatik yazılmamalı.

---

## 9.4. Manuel Veri Girişi

### Gereksinimler

Kullanıcı şu verileri girebilmeli:

- Toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali
- pH
- EC
- Tuzluluk
- Son sulama zamanı
- Sulama süresi
- Su miktarı

### Kabul kriterleri

- Veri aralıkları kontrol edilmeli.
- Gerçekçi olmayan değerler reddedilmeli veya uyarı verilmelidir.
- Eksik opsiyonel verilerde analiz devam edebilmelidir.
- Sistem veri güven skoru üretmelidir.

---

## 9.4b. Laboratuvar Analizi (P1)

### Gereksinimler

- “Toprak Analizi Ekle” ekranı
- Rapor yükleme: PDF, JPG, PNG, Excel, CSV
- Manuel lab sonuç girişi
- Rapor meta: lab adı, rapor no, analiz/numune tarihi, derinlik, bölge
- Parametre kaydı: değer + **birim** (+ yöntem opsiyonel)
- MVP lab paketi: pH, EC/tuz, organik madde, kireç, fosfor, potasyum
- Otomatik metin çıkarma yalnızca öneri; kullanıcı onayı zorunlu
- Gübre reçetesi üretilmez

### Kabul kriterleri

- Birimsiz parametre kaydı reddedilmeli veya birim seçimi zorunlu olmalı.
- Kullanıcı onaylamadan lab verisi kalıcı olmamalı.
- Lab kaynağı `lab_report` veya `lab_manual` olarak etiketlenmeli.
- Son 12 ay içindeki lab raporu veri güven skoruna olumlu katkı vermeli.

Referans: `veri-mimarisi.md`

---

## 9.5. IoT/Bulut Veri Akışı

### Gereksinimler

- Cihaz ekleme ekranı olmalı.
- Cihaz adı ve türü girilebilmeli.
- API anahtarı alanı olmalı.
- Bağlantı testi yapılabilmeli.
- Son veri zamanı gösterilmeli.
- Prototipte kontrollü simülasyon verisi belirli aralıklarla sisteme aktarılmalı.

### Kabul kriterleri

- En az bir sensör aktif gösterilmeli.
- Bağlantı kesildiğinde uyarı oluşmalı.
- Yeni veri geldiğinde dashboard otomatik güncellenmeli.

---

## 9.6. Veri Doğrulama

### Gereksinimler

Sistem:

- Eksik veri kontrolü yapmalı.
- Veri aralığı kontrolü yapmalı.
- Ani sıçramaları tespit etmeli.
- Eski verileri işaretlemeli.
- Çelişkili verileri uyarı olarak göstermeli.

### Kabul kriterleri

- Ani nem değişimi uyarı üretmeli.
- 24 saatten eski veri “güncel değil” olarak işaretlenmeli.
- Veri güven skoru yüzde olarak gösterilmeli.

---

## 9.7. AI Sulama Tahmini

### Gereksinimler

Model şu girdileri kullanmalı:

- Toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama zamanı
- Nem değişim trendi

Model şu çıktıları üretmeli:

- Sulama gerekli mi?
- Sulama aciliyeti
- Önerilen sulama süresi
- Risk seviyesi
- Güven skoru
- Açıklama

### Kabul kriterleri

- Her analizde en az bir karar üretilebilmeli.
- Karar metni kullanıcıya anlaşılır biçimde gösterilmeli.
- Güven skoru gösterilmeli.
- Veri eksikse kararın sınırlı olduğu belirtilmeli.

---

## 9.8. Nem Tahmini

### Gereksinimler

- 24 saatlik tahmin
- 48 saatlik tahmin
- 72 saatlik tahmin

### Kabul kriterleri

- Tahmin grafiği gösterilmeli.
- Her zaman dilimi için tahmini nem değeri bulunmalı.
- Tahmin çıktısı risk seviyesine bağlanmalı.

---

## 9.9. Risk Analizi

### Risk türleri

- Kuruma riski
- Aşırı sulama riski
- Bitki su stresi
- Sensör arızası
- Veri yetersizliği

### Risk seviyeleri

- Düşük
- Orta
- Yüksek
- Kritik

### Kabul kriterleri

- En az bir risk türü hesaplanmalı.
- Risk seviyesi renk ve metinle gösterilmeli.
- Kritik riskte uyarı kartı görünmeli.

---

## 9.10. Senaryo Simülasyonu

### Gereksinimler

Kullanıcı şu seçenekleri seçebilmeli:

- Şimdi sulama
- 12 saat sonra sulama
- 24 saat sonra sulama
- Sulama yapmama
- Sulama süresini azaltma
- Sulama süresini artırma

### Çıktılar

- Tahmini nem
- Tahmini su kullanımı
- Risk seviyesi
- Beklenen sonuç

### Kabul kriterleri

- En az iki senaryo karşılaştırılabilmeli.
- Sonuçlar tablo veya grafik üzerinde gösterilmeli.
- Sistem önerilen senaryoyu işaretlemeli.

---

## 9.11. Sanal Sulama Otomasyonu

### Gereksinimler

- Sulamayı başlat butonu
- Sulamayı durdur butonu
- Vana durumu
- Sulama süresi
- Kullanılan su miktarı
- İşlem kaydı

### Kabul kriterleri

- Kullanıcı onayı olmadan otomasyon başlamamalı.
- Başlatıldığında vana “açık” görünmeli.
- Süre tamamlandığında vana “kapalı” olmalı.
- Sulama olayı geçmişe kaydedilmeli.
- Sulama sonrası veri güncellenmeli.

---

## 9.12. Dashboard

### Gösterilecek bileşenler

- Mevcut toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Yağış ihtimali
- Risk seviyesi
- AI önerisi
- Güven skoru
- Veri kaynağı
- Son güncelleme zamanı
- Sensör durumu
- 72 saatlik tahmin

### Kabul kriterleri

- Dashboard tek ekranda temel durumu gösterebilmeli.
- Kritik bilgiler ilk bakışta anlaşılabilmeli.
- Mobil ve masaüstünde kullanılabilir olmalı.

---

## 10. Yapay Zekâ Gereksinimleri

### Model yaklaşımı

MVP’de hibrit yapı kullanılacaktır:

> Kural tabanı + makine öğrenmesi + güvenlik sınırları

### Model seçenekleri

- Random Forest
- XGBoost
- Regresyon
- Isolation Forest

### AI görevleri

- Sulama ihtiyacı sınıflandırması
- Nem tahmini
- Risk sınıflandırması
- Anomali tespiti
- Açıklanabilir öneri

### Açıklanabilirlik

Sistem önerinin nedenini göstermelidir.

Örnek:

> Sulama öneriliyor çünkü mevcut nem %28, son 24 saatte %7 düşüş var, sıcaklık yüksek ve yağış beklenmiyor.

### Güvenlik sınırları

- Kritik veri eksikliğinde otomasyon önerilmemeli.
- Gerçekçi olmayan veriler model girişine alınmamalı.
- Düşük güven skorunda kullanıcı onayı zorunlu olmalı.

---

## 11. Veri Gereksinimleri

### Zorunlu veriler

- Toprak nemi
- Hava sıcaklığı
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama zamanı

### Opsiyonel veriler

- Toprak sıcaklığı
- Hava nemi
- pH
- EC
- Tuzluluk
- Su miktarı
- Sulama süresi

### Veri kaynakları

- Manuel giriş
- IoT simülasyonu
- Test veri seti
- Gelecekte gerçek sensör API’leri

---

## 12. Veri Tabanı Gereksinimleri

### Users

- id
- name
- email
- password_hash
- role
- created_at

### Farms

- id
- user_id
- name
- location
- area
- soil_type
- irrigation_type
- created_at

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
- rainfall_probability
- ph
- ec
- salinity

### Predictions

- id
- farm_id
- irrigation_needed
- irrigation_duration
- risk_level
- confidence_score
- explanation
- created_at

### IrrigationEvents

- id
- farm_id
- start_time
- end_time
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

### LabReports (P1)

- id, farm_id, zone_id (nullable)
- lab_name, report_number
- analysis_date, sample_date
- sample_depth_cm, sample_region
- file_path, file_type
- source_type (`lab_report` | `lab_manual`)
- user_confirmed
- created_at

### LabParameters (P1)

- id, report_id
- parameter_code, value, unit, method
- extracted_auto

Ayrıntı: `veri-mimarisi.md` §12.

---

## 13. Teknik Mimari

### Frontend

- Next.js veya React
- Alternatif hızlı MVP: Streamlit

### Backend

- Python
- FastAPI

### Veritabanı

- Supabase / PostgreSQL
- Alternatif: SQLite

### Yapay zekâ

- Python
- Scikit-learn
- XGBoost

### IoT simülasyonu

- MQTT
- REST API
- Zamanlanmış Python scripti

### Canlıya alma

- Frontend: Vercel
- Backend: Render veya Railway
- Veritabanı: Supabase

---

## 14. API Gereksinimleri

### Kimlik doğrulama

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Arazi

- `POST /farms`
- `GET /farms`
- `GET /farms/{id}`
- `PUT /farms/{id}`
- `DELETE /farms/{id}`

### Sensör verisi

- `POST /sensor-readings/{farm_id}`
- `GET /sensor-readings/{farm_id}`
- `POST /iot/simulate`
- `GET /datasets` / `POST /datasets/load` (`source_type: test_dataset`)

### Tahmin ve anomali

- `POST /predict/irrigation` (query: `farm_id`)
- `GET /predictions/{farm_id}`
- `GET /anomalies/{farm_id}`

### Senaryo

- `POST /simulate/scenario`

### Sulama

- `POST /irrigation/start` (`user_approved=true` zorunlu; güven skoru &lt; 60 reddedilir)
- `POST /irrigation/stop`
- `GET /irrigation/history/{farm_id}`

### Cihaz / IoT

- `POST /devices`
- `GET /devices/{farm_id}`
- `POST /devices/test-connection`
- `POST /iot/simulate` (`source_type: simulation`)
- `GET /datasets` / `POST /datasets/load` (`source_type: test_dataset`)
- `POST /iot/ingest` (Field Node JSON; `simulation` true/false → `simulation`/`iot`)

### Bölgeler ve laboratuvar (P1)

- `POST /zones`
- `GET /zones/{farm_id}`
- `POST /lab-reports` (`user_confirmed=true` + birimli parametreler zorunlu)
- `GET /lab-reports/{farm_id}`
- `POST /lab-reports/{id}/confirm`

Referans: `veri-mimarisi.md`, `iot-mimarisi.md`
---

## 15. Kullanıcı Deneyimi Gereksinimleri

### Ekran envanteri

- Toplam **38** ana ekran: F01–F30 (çiftçi) + A01–A08 (yönetici).
- Mobil = responsive varyasyon; ayrı ekran sayılmaz.
- MVP öncelikli **20** ekranın UX/UI spesifikasyonu: [`ekran-haritasi.md`](ekran-haritasi.md).
- Görsel dil ve shell kalıpları: [`designsystem.md`](designsystem.md) §28A.
- Yönetici paneli ayrı `role=admin` shell (`/admin/...`); **as-built** `AdminShell` + A01–A08.
- As-built App Router eşlemesi: [`ekran-haritasi.md`](ekran-haritasi.md) §7 (MVP-20+ rotalar ayrılmış; F11 hub + hafif legacy).

### Temel UX ilkeleri

- Arayüz sade olmalı.
- Teknik terimler açıklanmalı.
- Kritik kararlar tek bakışta anlaşılmalı.
- Renkler yalnızca dekorasyon için değil, durum göstermek için kullanılmalı.
- Kullanıcı önerinin nedenini görebilmeli.
- Tüm kritik aksiyonlar onay istemeli.
- Veri kaynağı (`SourceBadge`) açıkça etiketlenmeli.
- Simülasyon “gerçek sensör” olarak sunulmamalı.

### Ana ekran soruları

Kullanıcı şu üç sorunun cevabını tek ekranda görmelidir:

1. Toprağın durumu nasıl?
2. Ne yapmalıyım?
3. Neden yapmalıyım?

---

## 16. Performans Gereksinimleri

- Dashboard 3 saniye içinde yüklenmeli.
- Tahmin sonucu 5 saniye içinde gelmeli.
- Yeni IoT verisi 10 saniye içinde görünmeli.
- Kullanıcı aksiyonları hata durumunda anlamlı mesaj vermeli.
- Uygulama en az 50 eşzamanlı demo kullanıcısını desteklemeli.

---

## 17. Güvenlik Gereksinimleri

- Şifreler düz metin saklanmamalı.
- Kullanıcı yalnızca kendi arazilerini görmeli.
- API erişimleri yetkilendirilmeli.
- Kritik otomasyon aksiyonları onay istemeli.
- Veri kaynağı açıkça etiketlenmeli.
- Test verisi gerçek veri gibi sunulmamalı.
- IoT simülasyonu “simülasyon” olarak işaretlenmeli.

---

## 18. Başarı Metrikleri

### Teknik metrikler

- Kayıt akışının çalışma oranı
- Arazi oluşturma başarı oranı
- Veri girişi başarı oranı
- Tahmin API cevap süresi
- Sistem çalışma süresi
- IoT simülasyon veri sürekliliği

### AI metrikleri

- Sulama sınıflandırma doğruluğu
- Nem tahmin hatası
- Anomali tespit doğruluğu
- Güven skorunun tutarlılığı

### Kullanıcı metrikleri

- Görev tamamlama oranı
- Kullanıcının öneriyi anlama oranı
- Senaryo kullanım oranı
- Otomasyon onay oranı
- Kullanıcı memnuniyeti

### Etki metrikleri

- Tahmini su tasarrufu
- Önlenen gereksiz sulama sayısı
- Karar verme süresindeki azalma

---

## 19. Kabul Kriterleri

MVP başarılı sayılacaktır, eğer:

1. Kullanıcı kayıt olup giriş yapabiliyorsa.
2. En az bir arazi oluşturabiliyorsa.
3. Manuel veri girebiliyorsa.
4. IoT simülasyon verisi sisteme akıyorsa.
5. AI sulama önerisi üretiyorsa.
6. 72 saatlik nem tahmini gösteriliyorsa.
7. En az iki senaryo karşılaştırılabiliyorsa.
8. Sanal sulama başlatılıp durdurulabiliyorsa.
9. Sulama geçmişi kaydediliyorsa.
10. Uygulama canlı bir URL üzerinden erişilebiliyorsa.

---

## 20. Demo Akışı

1. Kullanıcı kayıt olur.
2. “Domates Serası” adlı araziyi oluşturur.
3. Toprak ve ürün bilgilerini girer.
4. IoT/bulut veri kaynağını seçer.
5. Kontrollü test verisi sisteme gelir.
6. Dashboard mevcut durumu gösterir.
7. AI kuruma riskini “yüksek” olarak belirler.
8. Sistem 18 saat içinde sulama önerir.
9. Kullanıcı “24 saat bekle” senaryosunu çalıştırır.
10. Sistem nemin kritik seviyeye düşeceğini gösterir.
11. Kullanıcı “şimdi sulama” seçeneğini seçer.
12. Sanal vana açılır.
13. Sulama süresi ve su miktarı kaydedilir.
14. Nem değeri güncellenir.
15. AI yeniden analiz yapar.
16. Risk seviyesi düşer.
17. Tahmini su tasarrufu gösterilir.

---

## 21. Geliştirme Öncelikleri

### P0 — Zorunlu

- Kayıt ve giriş
- Arazi oluşturma
- Manuel veri girişi
- IoT veri simülasyonu
- Dashboard
- Kural tabanlı öneri motoru
- AI tahmini
- 72 saatlik nem tahmini
- Senaryo simülasyonu
- Sanal sulama
- Canlıya alma

### P1 — Önemli

- Laboratuvar raporu yükleme / manuel lab girişi (birim + onay)
- Veri güven skoru (lab puanı dahil)
- Anomali tespiti
- Sulama geçmişi
- Su tasarrufu raporu
- Sanal yönetim bölgeleri (basit isimlerle)

### P2 — Sonraki sürüm

- Gerçek IoT bağlantısı
- Gerçek hava durumu API’si
- Lab OCR / lab API entegrasyonu
- Mikroelement / gelişmiş lab paketi
- Çoklu tarla yönetimi
- Gelişmiş raporlama
- Gübre önerisi (ayrı ürün kararı; reçetesiz yorumdan fazlası)

---

## 22. Riskler

### Veri kalitesi

**Risk:** Test verisi gerçek saha koşullarını tam temsil etmeyebilir.

**Önlem:** Prototip iddiası açıkça belirtilmeli, gerçek saha doğrulaması sonraki faza bırakılmalı.

### Model güvenilirliği

**Risk:** Yapay veriyle eğitilen model gerçek ortamda zayıf kalabilir.

**Önlem:** Model karar destek sistemi olarak konumlandırılmalı.

### Kapsam büyümesi

**Risk:** Proje çok fazla modül içerirse tamamlanamaz.

**Önlem:** Sulama kararına odaklanılmalı.

### IoT yanılsaması

**Risk:** Simülasyon gerçek entegrasyon gibi sunulursa güven kaybı oluşur.

**Önlem:** Arayüzde “IoT simülasyonu” etiketi kullanılmalı.

### Kullanıcı deneyimi

**Risk:** Teknik veriler çiftçiyi zorlayabilir.

**Önlem:** Sade dil ve açıklanabilir öneriler kullanılmalı.

---

## 23. Yol Haritası

### Faz 1 — MVP

- Manuel veri
- IoT simülasyonu
- Sulama tahmini
- Senaryo simülasyonu
- Sanal otomasyon

### Faz 2 — Pilot

- Gerçek sensör entegrasyonu
- Gerçek hava durumu API’si
- Küçük sera testi
- Kullanıcı geri bildirimi

### Faz 3 — Gelişmiş toprak analizi

- pH
- EC
- Tuzluluk
- Toprak sağlık skoru

### Faz 4 — Gelişmiş dijital ikiz

- Uydu
- Drone
- Verim tahmini
- Gübreleme önerisi

### Faz 5 — Ölçekleme

- Kooperatif paneli
- Çoklu tarla yönetimi
- Kurumsal API
- Bölgesel karar destek sistemi

---

## 24. Sonuç

AgriTwin AI PRD’si, ürünün ilk sürümünü dar, ölçülebilir ve çalışabilir bir kapsamda tanımlar.

MVP’nin temel değeri:

- Veriyi toplamak,
- Veriyi doğrulamak,
- Sulama ihtiyacını tahmin etmek,
- Kararın nedenini açıklamak,
- Senaryoları karşılaştırmak,
- Kullanıcı onayıyla otomasyonu çalıştırmak

üzerine kuruludur.

Ürünün ilk sürümünde amaç tam kapsamlı bir tarım dijital ikizi geliştirmek değil; toprağın nem ve sulama davranışına odaklanan, çalışan ve doğrulanabilir bir dijital ikiz prototipi ortaya koymaktır.