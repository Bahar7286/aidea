# AGRITWIN AI — İŞ GELİŞTİRME VE ÜRÜN CANVASI

> **Kapsam notu (okuma sırası):** Bu canvas strateji ve **uzun vadeli vizyon** içerir.  
> **Shipped MVP (as-built)** için bağlayıcı kaynaklar: `mvp.md`, `prd.md`, `Progress.md`, `techstack.md`, `AGENTS.md`, `.cursor/rules/agritwin-core.mdc`.  
>  
> **MVP as-built vs vizyon (kısa):** Canlı ürün nem/sulama karar destek prototipidir (auth, farm, simüle IoT, lab, senaryo, onaylı sanal sulama, Leaflet/OSM, Open-Meteo, kural+OpenRouter açıklama, malzemeler=kullanım kaydı, admin/abonelik UI). Uydu/drone/gübre **reçetesi**/verim/tam otomatik sulama canvas vizyonundadır — **shipped değildir**. Laboratuvar IoT’nin yerini almaz.

## 1. Proje Adı

**AgriTwin AI**

### Kısa Tanım

AgriTwin AI; çiftçinin manuel olarak girdiği tarla ve toprak verilerini, IoT ve bulut sistemlerinden alınan otomatik sensör verilerini ve hava durumu bilgilerini tek platformda birleştirerek toprağın dijital ikizini oluşturan, yapay zekâ ile sulama ihtiyacı ve toprak risklerini tahmin eden, farklı karar senaryolarını simüle eden ve otomasyon süreçlerini yöneten web tabanlı tarım teknolojisi platformudur.

---

## 2. Görünen Problem

Çiftçiler toprağın nem, sıcaklık, pH, tuzluluk ve diğer özelliklerini düzenli ve bütünleşik şekilde takip edememektedir.

Bu nedenle sulama ve toprak yönetimi kararları çoğunlukla:

- Kişisel deneyime,
- Genel hava tahminlerine,
- Belirli aralıklarla yapılan toprak analizlerine,
- Tek noktadan alınan ölçümlere,
- Gözleme

dayanmaktadır.

---

## 3. Gerçek Problem

Asıl problem yalnızca toprağa ait verilerin eksik olması değildir.

Gerçek problem:

> Çiftçinin, farklı kaynaklardan gelen toprak, hava, ürün ve sulama verilerini tek sistemde birleştirerek toprağın gelecekteki durumunu tahmin edebileceği ve aldığı kararların sonuçlarını önceden görebileceği güvenilir bir karar destek sistemine sahip olmamasıdır.

Bu nedenle çiftçi:

- Ne zaman sulama yapması gerektiğini,
- Ne kadar su kullanması gerektiğini,
- Hangi bölgenin daha fazla suya ihtiyaç duyduğunu,
- Sulamayı geciktirirse ne olacağını,
- Yağış ihtimalinin sulama kararını nasıl etkileyeceğini,
- Aşırı sulama veya kuruma riskini

ölçülebilir biçimde görememektedir.

---

## 4. Çözüm

AgriTwin AI, kullanıcı tarafından girilen manuel verileri, IoT/bulut sistemlerinden alınan otomatik sensör verilerini ve dış veri kaynaklarını tek platformda birleştirir.

Sistem:

- Toprağın mevcut durumunu gösterir.
- Geçmiş verileri analiz eder.
- Önümüzdeki 24, 48 ve 72 saat için nem değişimini tahmin eder.
- Sulama ihtiyacını hesaplar.
- Kuruma, aşırı sulama, tuzluluk ve sensör anomalisi risklerini belirler.
- Kullanıcıya açıklanabilir öneriler sunar.
- Farklı sulama senaryolarını simüle eder.
- Kullanıcı onayıyla sanal veya gerçek sulama otomasyonunu başlatır.
- Sulama sonrasında yeni durumu tekrar analiz eder.

---

## 5. Prototipin Net Kapsamı

İlk çalışan prototip, toprağın bütün fiziksel, kimyasal ve biyolojik yapısını modellemeye çalışmayacaktır.

MVP şu probleme odaklanacaktır:

> Toprak nemi, hava durumu, ürün türü ve sulama geçmişini analiz ederek sulama zamanını ve ihtiyacını tahmin etmek.

### MVP’nin yapacağı işler

1. Kullanıcı kaydı oluşturma
2. Arazi ve ürün bilgisi ekleme
3. Manuel veri girişi
4. IoT/bulut veri akışı simülasyonu
5. Hazır test veri seti kullanımı
6. Veri doğrulama
7. Sulama ihtiyacı tahmini
8. 72 saatlik nem tahmini
9. Risk sınıflandırması
10. Senaryo simülasyonu
11. Sanal sulama otomasyonu
12. Raporlama ve geçmiş kayıtları gösterme

---

## 6. Hedef Kullanıcılar

### Birincil kullanıcılar

- Küçük ve orta ölçekli çiftçiler
- Sera üreticileri
- Damla sulama sistemi kullanan üreticiler
- Su maliyeti yüksek bölgelerde üretim yapan çiftçiler
- Kuraklık riski bulunan bölgelerdeki üreticiler

### İkincil kullanıcılar

- Tarım kooperatifleri
- Üretici birlikleri
- Ziraat mühendisleri
- Tarım danışmanları
- Sulama birlikleri
- Büyük tarım işletmeleri
- Belediyeler
- Tarım il ve ilçe müdürlükleri
- Üniversiteler ve araştırma merkezleri

### Erken benimseyenler

- Sera üreticileri
- Dijital tarım teknolojilerine açık çiftçiler
- Pilot projelere katılan üreticiler
- Kooperatif üyesi çiftçiler
- Domates, biber, salatalık, çilek ve bağ üreticileri

---

## 7. Veri Kaynakları

AgriTwin AI dört veri giriş yolunu hedefler (IoT laboratuvarın yerine geçmez). Ayrıntı: `veri-mimarisi.md`

1. Manuel tarla / ürün verisi  
2. IoT sensör (MVP: simülasyon)  
3. Test / demo veri seti  
4. Laboratuvar analizi (P1: rapor yükleme veya manuel lab; birim + onay)

### 7.1. Manuel veri girişi

Çiftçi veya tarım danışmanı platforma veri girebilir.

#### Kullanıcı bilgileri

- Ad soyad
- E-posta
- Kullanıcı tipi

#### Arazi bilgileri

- Arazi adı
- Konum
- Arazi büyüklüğü
- Arazi türü
- Sulama sistemi
- Toprak türü

#### Ürün bilgileri

- Ürün türü
- Ekim tarihi
- Gelişim dönemi
- Tahmini hasat tarihi

#### Toprak ve çevre verileri

- Toprak nemi
- Toprak sıcaklığı
- pH
- Elektriksel iletkenlik
- Tuzluluk
- Hava sıcaklığı
- Hava nemi
- Son sulama tarihi
- Son sulama süresi
- Kullanılan su miktarı

Tüm alanlar zorunlu olmayacaktır. Eksik veri olduğunda sistem analiz güven seviyesini düşürecektir.

---

### 7.2. IoT ve bulut sistemlerinden otomatik veri

Gerçek sistemde veriler şu kaynaklardan gelebilir:

- Toprak nem sensörü
- Toprak sıcaklık sensörü
- pH sensörü
- EC sensörü
- Tuzluluk sensörü
- Hava sıcaklığı ve nem sensörü
- Yağış sensörü
- Debi sensörü
- Sulama vanası
- ESP32
- LoRa
- Wi-Fi
- GSM
- MQTT
- IoT bulut platformları

Prototip aşamasında bu veri akışı simüle edilecektir.

#### IoT cihaz yönetim alanı

- Cihaz adı
- Cihaz kimliği
- API anahtarı
- Bağlantı durumu
- Son veri zamanı
- Aktif/pasif durumu
- Veri kaynağı
- Sensör tipi

---

### 7.3. Test veri seti

Test verileri sistem tarafından rastgele üretilmeyecektir.

Ekip tarafından önceden hazırlanmış kontrollü senaryolar kullanılacaktır.

#### Örnek senaryolar

- Normal toprak durumu
- Kuruma riski
- Aşırı sulama riski
- Tuzluluk riski
- Sensör anomalisi
- Sulama sonrası beklenmeyen durum

Bu veri setleri:

- Model eğitimi,
- Sistem testi,
- Demo,
- Risk sınıflandırması,
- Senaryo karşılaştırması

için kullanılacaktır.

---

## 8. Veri Doğrulama Katmanı

Sisteme gelen her veri doğrudan yapay zekâ modeline gönderilmeyecektir.

Önce şu kontroller yapılacaktır:

- Veri eksik mi?
- Veri gerçekçi aralıkta mı?
- Önceki ölçümle aşırı fark var mı?
- Veri güncel mi?
- Sensör bağlantısı aktif mi?
- Manuel ve otomatik veriler çelişiyor mu?
- Aynı veri tekrar gönderilmiş mi?
- Sensör arızası ihtimali var mı?

### Örnek uyarı

> Toprak nemi son beş dakika içinde %45 seviyesinden %3 seviyesine düştü. Sensör arızası veya veri hatası ihtimali bulunmaktadır.

---

## 9. Yapay Zekânın Görevleri

Yapay zekâ ile otomasyon birbirinden ayrı tutulacaktır.

### 9.1. Sulama ihtiyacı tahmini

Model şu girdileri kullanır:

- Toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama zamanı
- Son sulama süresi
- Son günlerdeki nem değişimi

#### Model çıktıları

- Sulama gerekli
- Sulama gereksiz
- Sulama ertelenebilir
- Sulama acil
- Tahmini sulama süresi
- Risk seviyesi
- Güven skoru

---

### 9.2. Nem seviyesi tahmini

Sistem:

- 24 saat,
- 48 saat,
- 72 saat

sonraki tahmini nem seviyelerini hesaplar.

---

### 9.3. Anomali tespiti

Yapay zekâ şu durumları tespit eder:

- Sensör arızası
- Olağan dışı nem düşüşü
- Aşırı sulama
- Sulama sonrası beklenmeyen nem değişimi
- Gerçekçi olmayan pH veya EC değeri
- Veri akış kesintisi

---

### 9.4. Risk sınıflandırması

Riskler şu seviyelerde gösterilir:

- Düşük
- Orta
- Yüksek
- Kritik

#### Risk türleri

- Kuruma riski
- Aşırı sulama riski
- Tuzlanma riski
- Bitki su stresi
- Sensör arızası riski
- Veri yetersizliği riski

---

### 9.5. Senaryo simülasyonu

Kullanıcı şu seçenekleri test edebilir:

- Şimdi sulama
- 12 saat sonra sulama
- 24 saat sonra sulama
- Sulama yapmama
- Sulama süresini azaltma
- Sulama süresini artırma

Sistem her senaryonun:

- Tahmini nem seviyesini,
- Su kullanımını,
- Risk seviyesini,
- Beklenen sonucu

karşılaştırır.

---

### 9.6. Açıklanabilir öneri üretimi

Sistem yalnızca sonuç vermeyecektir.

Örnek:

> Sulama öneriliyor. Çünkü toprak nemi %27 seviyesine düştü, son 24 saatte %8 azaldı, hava sıcaklığı yüksek ve önümüzdeki 48 saat içinde yağış beklenmiyor.

---

## 10. Otomasyonun Görevleri

Otomasyon katmanı şu işlemleri gerçekleştirir:

- IoT ve bulut sistemlerinden veri çekme
- Verileri belirli aralıklarla güncelleme
- Kritik durumda bildirim gönderme
- Kullanıcı onayı sonrası sulama başlatma
- Sulama süresini takip etme
- Sulamayı durdurma
- Kullanılan su miktarını kaydetme
- İşlem geçmişi oluşturma
- Yeni sensör verisini sisteme aktarma
- AI modelini yeniden çalıştırma

### İş akışı

1. Veri alınır.
2. Veri doğrulanır.
3. Yapay zekâ analiz yapar.
4. Sulama önerisi oluşturulur.
5. Kullanıcı öneriyi onaylar.
6. Otomasyon sanal veya gerçek vanayı açar.
7. Sulama süresi tamamlanır.
8. İşlem kaydedilir.
9. Yeni veri alınır.
10. Sistem yeniden analiz yapar.

---

## 11. Dijital İkiz Bileşeni

AgriTwin AI yalnızca sensör paneli değildir.

Dijital ikiz şu işlevleri yerine getirir:

- Gerçek tarla verilerini sanal modelde temsil eder.
- Toprağın mevcut durumunu gösterir.
- Geçmiş değişimleri izler.
- Gelecekteki durumu tahmin eder.
- Alternatif müdahaleleri simüle eder.
- Gerçek sonuçlarla modeli günceller.

### Dijital ikiz ekranında gösterilecekler

- Toprak nem haritası
- Sıcaklık durumu
- Risk bölgeleri
- Sensör durumu
- 72 saatlik tahmin
- Sulama geçmişi
- Senaryo sonuçları
- Toprak sağlık skoru
- Veri güven seviyesi

---

## 12. Temel Arayüz Sayfaları

### 12.1. Kayıt ve giriş

- Kullanıcı kaydı
- Rol seçimi
- Giriş yapma

### 12.2. Arazi oluşturma

- Arazi adı
- Konum
- Alan büyüklüğü
- Toprak türü
- Ürün türü
- Sulama tipi

### 12.3. Veri kaynağı seçimi

- Manuel veri girişi
- IoT/bulut bağlantısı
- Demo/test verisi
- Dosyadan veri yükleme

### 12.4. Ana dashboard

- Mevcut nem
- Hava durumu
- Sulama ihtiyacı
- Risk seviyesi
- AI önerisi
- Veri güven skoru
- Son güncelleme zamanı

### 12.5. Dijital ikiz ekranı

- Tarla haritası
- Bölgesel nem
- Kuruma riski
- Tahmin grafikleri

### 12.6. Yapay zekâ önerileri

- Öneri
- Gerekçe
- Güven skoru
- Eksik veriler
- Risk açıklaması

### 12.7. Senaryo simülasyonu

- Şimdi sulama
- Bekleme
- Sulama süresi değiştirme
- Sonuç karşılaştırma

### 12.8. IoT cihaz yönetimi

- Cihaz ekleme
- API anahtarı
- Bağlantı testi
- Son veri zamanı
- Aktif/pasif sensör

### 12.9. Sulama otomasyonu

- Vana durumu
- Pompa durumu
- Başlat
- Durdur
- Sulama süresi
- Su miktarı

### 12.10. Raporlama

- Günlük su kullanımı
- Tahmini su tasarrufu
- Nem değişimi
- Sulama geçmişi
- AI öneri geçmişi
- Sensör hata kayıtları

---

## 13. Benzersiz Değer Önerisi

> AgriTwin AI, çiftçiye yalnızca toprağın bugünkü durumunu göstermez; toprağın gelecekte nasıl değişeceğini tahmin eder, farklı sulama kararlarını uygulamadan önce simüle eder ve veriye dayalı sulama yönetimi sağlar.

### Temel faydalar

- Daha az su kullanımı
- Daha düşük enerji maliyeti
- Daha doğru sulama kararı
- Daha az bitki stresi
- Toprak sağlığının korunması
- Sensör hatalarının erken fark edilmesi
- Veriye dayalı tarım yönetimi
- Çiftçinin karar belirsizliğinin azalması

---

## 14. Mevcut Alternatifler

- Manuel toprak kontrolü
- Sabit saatli sulama
- Basit nem sensörleri
- Hava durumu uygulamaları
- Laboratuvar analizleri
- Ziraat mühendisi danışmanlığı
- Eşik değerine göre çalışan otomasyon sistemleri

### Mevcut çözümlerin eksikleri

- Veriler dağınıktır.
- Geleceğe yönelik tahmin yapılmaz.
- Senaryo simülasyonu yoktur.
- Sensör ve kullanıcı verileri birlikte kullanılmaz.
- Çiftçiye açıklanabilir karar desteği sunulmaz.
- Çoğu sistem yalnızca mevcut durumu gösterir.

---

## 15. Gelir Modeli

### Donanım geliri

- Sensör kitleri
- ESP32
- Vana ve pompa kontrol birimi
- Kurulum
- Bakım

### Abonelik geliri

#### Temel paket

- Manuel veri girişi
- Dashboard
- Temel risk uyarıları

#### Akıllı paket

- IoT entegrasyonu
- AI tahmini
- Senaryo simülasyonu
- Otomasyon yönetimi

#### Kurumsal paket

- Çoklu tarla yönetimi
- Kooperatif paneli
- Gelişmiş raporlama
- API entegrasyonu
- Çoklu kullanıcı

### Hizmet geliri

- Kurulum
- Sensör kalibrasyonu
- Teknik bakım
- Veri analizi
- Tarımsal danışmanlık entegrasyonu

---

## 16. Müşteri Kanalları

- Tarım kooperatifleri
- Ziraat odaları
- Tarım fuarları
- Üniversiteler
- Tarım danışmanları
- Belediyeler
- Tarım müdürlükleri
- Saha demonstrasyonları
- Dijital pazarlama
- Çiftçi referansları
- Pilot sera ve tarla çalışmaları

### Pazara giriş yaklaşımı

> Pilot saha kurulumu → su tasarrufu ölçümü → çiftçi referansı → kooperatif yayılımı → kurumsal müşteriler

---

## 17. Temel Ortaklar

- Çiftçiler
- Kooperatifler
- Ziraat mühendisleri
- Toprak bilimciler
- Üniversiteler
- Sensör üreticileri
- Sulama sistemi firmaları
- IoT bulut sağlayıcıları
- Telekom şirketleri
- Belediyeler
- Tarım ve Orman Bakanlığı birimleri
- Teknokentler
- Bulut hizmet sağlayıcıları

---

## 18. Temel Kaynaklar

- Tarım ve toprak veri setleri
- Test veri setleri
- Yapay zekâ modelleri
- IoT entegrasyon altyapısı
- Web uygulaması
- Veritabanı
- Sensör prototipleri
- Pilot tarım alanları
- Ziraat uzmanlığı
- Yazılım geliştirme ekibi
- Bulut altyapısı

---

## 19. Temel Faaliyetler

- Veri toplama
- Veri doğrulama
- Model geliştirme
- Model test etme
- IoT entegrasyonu
- Arayüz geliştirme
- Senaryo motoru geliştirme
- Sulama otomasyonu
- Kullanıcı testleri
- Pilot çalışma
- Teknik destek
- Saha doğrulaması
- İş modeli geliştirme

---

## 20. Maliyet Yapısı

- Yazılım geliştirme
- Yapay zekâ model geliştirme
- Bulut altyapısı
- Veritabanı
- IoT entegrasyonu
- Sensör ve donanım
- Kurulum
- Bakım
- Teknik destek
- Saha testleri
- Kullanıcı eğitimi
- Veri güvenliği
- Sensör kalibrasyonu

---

## 21. Rekabet Avantajı

AgriTwin AI’ın rekabet avantajı:

- Manuel veri ve IoT verisini birlikte kullanması
- Hazır test senaryolarıyla çalışabilir demo sunması
- Gelecekteki nem durumunu tahmin etmesi
- Sulama senaryolarını karşılaştırması
- Anomali tespiti yapması
- Açıklanabilir yapay zekâ önerileri sunması
- Otomasyonla doğrudan bağlantı kurması
- Küçük çiftçilere uyarlanabilir olması
- Modüler ve ölçeklenebilir yapısı

---

## 22. Riskler ve Önlemler

### Sensör hatası

**Risk:** Yanlış veri nedeniyle yanlış öneri oluşabilir.

**Önlem:** Veri doğrulama, çoklu sensör kontrolü ve anomali tespiti.

### Eksik veri

**Risk:** Model güvenilirliği düşebilir.

**Önlem:** Veri güven skoru ve zorunlu olmayan alanlar için uyarı sistemi.

### Yanlış AI önerisi

**Risk:** Ürün zarar görebilir.

**Önlem:** İlk aşamada kullanıcı onaylı otomasyon.

### Kullanıcı direnci

**Risk:** Çiftçi sistemi kullanmayabilir.

**Önlem:** Basit arayüz, sade öneri ve ekonomik fayda gösterimi.

### Yüksek donanım maliyeti

**Risk:** Küçük çiftçiler erişemeyebilir.

**Önlem:** Kooperatif, kiralama ve abonelik modeli.

### İnternet bağlantısı

**Risk:** Veri aktarımı kesilebilir.

**Önlem:** Çevrimdışı kayıt, LoRa ve GSM desteği.

---

## 23. Başarı Göstergeleri

### Teknik göstergeler

- Tahmin doğruluğu
- Sensör veri sürekliliği
- Veri doğrulama başarı oranı
- Anomali tespit doğruluğu
- Sistem çalışma süresi

### Çevresel göstergeler

- Su tüketimindeki azalma
- Gereksiz sulama sayısındaki düşüş
- Enerji kullanımındaki azalma
- Toprak nem dengesindeki iyileşme

### Kullanıcı göstergeleri

- Kullanıcı kayıt sayısı
- Aktif kullanıcı oranı
- Öneri uygulama oranı
- Kullanıcı memnuniyeti
- Veri giriş sıklığı

### Ticari göstergeler

- Pilot kullanıcı sayısı
- Ücretli müşteriye dönüşüm
- Abonelik yenileme oranı
- Müşteri edinme maliyeti
- Kooperatif anlaşması sayısı

---

## 24. MVP Teknik Mimarisi

### As-built (shipped)

- Frontend: Next.js + TypeScript + Tailwind + Recharts + Leaflet/OSM
- Backend: FastAPI + JWT
- DB: SQLite (yerel) / Supabase Postgres (prod)
- AI: Kural motoru + opsiyonel OpenRouter açıklama (ML vizyon / P2)
- IoT: REST simülasyon + ingest (MQTT vizyon)
- Hava: Open-Meteo
- Deploy: Vercel + Render + Supabase

### Vizyon / sonraki (canvas)

- Random Forest / XGBoost / Isolation Forest (eğitimli modeller)
- MQTT broker + gerçek saha düğümü
- Uydu / drone katmanları (MVP dışı)

---

## 25. Veri Tabanı Yapısı

### Users

- id
- name
- email
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

### Weather

- id
- farm_id
- timestamp
- rainfall_probability
- temperature
- humidity

### Predictions

- id
- farm_id
- irrigation_needed
- irrigation_duration
- risk_level
- explanation
- confidence_score

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

## 26. Demo Senaryosu

1. Kullanıcı sisteme kayıt olur.
2. “Domates Serası” adlı araziyi oluşturur.
3. Toprak, ürün ve sulama bilgilerini girer.
4. Veri kaynağı olarak IoT bağlantısını seçer.
5. Sistem kontrollü IoT test verisini alır.
6. Dashboard mevcut nemi ve sıcaklığı gösterir.
7. Yapay zekâ kuruma riskini hesaplar.
8. Sistem 24 saat içinde sulama önerir.
9. Kullanıcı 24 saat bekleme senaryosunu çalıştırır.
10. Sistem nem seviyesinin kritik düzeye düşeceğini gösterir.
11. Kullanıcı sulamayı başlatır.
12. Sanal vana açılır.
13. Sulama süresi ve su miktarı kaydedilir.
14. Nem seviyesi güncellenir.
15. Yapay zekâ yeniden analiz yapar.
16. Sistem tahmini su tasarrufunu gösterir.

---

## 27. Prototipte Yapay Zekâ ve Otomasyon Ayrımı

| Katman | Görev |
|---|---|
| Veri kaynağı | Manuel giriş, IoT/bulut verisi, test veri seti |
| Veri doğrulama | Eksik, hatalı ve olağan dışı verileri kontrol eder |
| Yapay zekâ | Tahmin, risk analizi, anomali tespiti, senaryo karşılaştırması |
| Dijital ikiz | Gerçek durumu temsil eder, geleceği tahmin eder, senaryoları simüle eder |
| Otomasyon | Veri çeker, bildirim gönderir, sulamayı başlatır ve kaydeder |

---

## 28. Stratejik Karar

AgriTwin AI için ilk aşamada alınması gereken karar:

> Tam kapsamlı toprak dijital ikizi geliştirmek yerine, sulama kararına odaklanan çalışan bir dijital ikiz MVP’si geliştirmek.

### Gerekçe

- Kapsam yönetilebilir.
- Çalışan prototip hazırlanabilir.
- Yapay zekâ kullanımı net gösterilir.
- IoT entegrasyonu simüle edilebilir.
- Kullanıcı veri girişi test edilebilir.
- Çevresel etki ölçülebilir.
- Sistem daha sonra genişletilebilir.

---

## 29. Uzun Vadeli Yol Haritası

### Faz 1

- Manuel veri girişi
- IoT simülasyonu
- Sulama tahmini
- Sanal otomasyon

### Faz 2

- Gerçek IoT entegrasyonu
- Nem ve sıcaklık sensörleri
- Hava durumu API’si
- Gerçek saha testi

### Faz 3

- pH ve EC analizi
- Tuzluluk riski
- Toprak sağlık puanı
- Gelişmiş dijital ikiz

### Faz 4

- Uydu ve drone entegrasyonu
- Bölgesel analiz
- Verim tahmini
- Gübreleme önerisi

### Faz 5

- Kooperatif paneli
- Çoklu tarla yönetimi
- Kamu ve kurumsal kullanım
- Bölgesel tarım karar platformu

---

## 30. Tek Cümlelik Proje Tanımı

> AgriTwin AI, çiftçinin manuel verilerini ve IoT/bulut sensör verilerini birleştirerek toprağın dijital ikizini oluşturan, sulama ihtiyacını ve toprak risklerini yapay zekâ ile tahmin eden, karar senaryolarını simüle eden ve sulama otomasyonunu yöneten web tabanlı tarım platformudur.