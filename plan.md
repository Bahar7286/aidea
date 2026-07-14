# AGRITWIN AI — GELİŞTİRME PLANI

## 1. Planın Amacı

Bu geliştirme planının amacı, AgriTwin AI fikrini çalışan, canlıya alınmış ve jüriye gösterilebilir bir MVP’ye dönüştürmektir.

Planın temel odağı:

> Çiftçinin manuel veri girebildiği, IoT/bulut veri akışının simüle edildiği, yapay zekânın sulama ihtiyacı ve risk analizi yaptığı, farklı senaryoları karşılaştırdığı ve sanal sulama otomasyonunun çalıştığı web tabanlı bir prototip geliştirmek.

---

## 2. Geliştirme Stratejisi

AgriTwin AI ilk aşamada tam kapsamlı bir toprak dijital ikizi olarak geliştirilmeyecektir.

İlk sürüm şu kapsamla sınırlandırılacaktır:

- Toprak nemi
- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama bilgisi
- Sulama ihtiyacı tahmini
- 72 saatlik nem tahmini
- Senaryo simülasyonu
- Sanal sulama otomasyonu

### Temel ilke

> Önce çalışan uçtan uca akış, sonra gelişmiş özellikler.

---

## 3. Geliştirme Fazları

## Faz 0 — Hazırlık ve Kapsam Netleştirme

### Amaç

Projenin teknik ve ürün kapsamını kesinleştirmek.

### Görevler

- Problem tanımını netleştirmek
- MVP kapsamını sabitlemek
- Hedef kullanıcıyı belirlemek
- Kullanıcı akışını çizmek
- Ekran listesini oluşturmak
- Teknik mimariyi seçmek
- Veri şemasını oluşturmak
- Demo senaryosunu belirlemek
- Ekip görev dağılımını yapmak

### Çıktılar

- Canvas
- MVP dokümanı
- PRD
- Geliştirme planı
- Wireframe / ekran haritası (`ekran-haritasi.md`)
- Teknik mimari şeması
- Veri tabanı şeması

### Tamamlanma kriteri

- Ekip, MVP’ye dahil olan ve olmayan özelliklerde anlaşmış olmalı.
- Her görev için sorumlu belirlenmiş olmalı.
- Demo senaryosu yazılı hâle gelmiş olmalı.

---

## Faz 1 — UX Tasarımı ve Proje Altyapısı

### Amaç

Uygulamanın temel arayüzünü ve teknik iskeletini oluşturmak.

### Görevler

#### UX/UI

- [x] Ekran haritası ve UX spesifikasyonu (`ekran-haritasi.md` — 38 ekran, MVP-20 detay; as-built §7)
- [x] Design system shell / SourceBadge / ConfirmGate (`designsystem.md` §28A)
- [x] Kayıt / giriş / auth onboarding ekranları
- [x] Arazi oluşturma ve liste ekranları
- [x] Veri kaynağı seçim ekranı (F17)
- [x] Manuel veri giriş ekranı
- [x] Dashboard
- [x] Dijital ikiz görünümü (sınırlı nem/risk viz — F13)
- [x] AI öneri kartı (F26–F27)
- [x] Senaryo simülasyonu ekranı (F28)
- [x] IoT cihaz ekranı (F18–F21)
- [x] Sulama otomasyonu ekranı (F29)
- [x] Rapor / hub ekranı (F30)
- [x] Admin panel A01–A08
- [x] App Router MVP-20+ ayrıştırması (as-built; F11 hafif legacy kalabilir)

#### Frontend

- [x] Next.js App Router projesi
- [x] Sayfa yönlendirmeleri (`frontend/src/app/**/page.tsx`)
- [x] Temel bileşenler (AppShell, AdminShell, …)
- Form doğrulama iyileştirmeleri (sürekli)
- Responsive yapı (AppShell alt nav as-built)

#### Backend

- FastAPI projesini oluşturmak
- Ortam değişkenlerini ayarlamak
- Temel API yapısını kurmak
- Hata yönetimini eklemek
- Logging sistemini başlatmak

#### Veritabanı

- Supabase/PostgreSQL bağlantısı kurmak
- Tabloları oluşturmak
- Migration yapısını hazırlamak
- Test verilerini eklemek

### Çıktılar

- Çalışan frontend iskeleti
- Çalışan backend
- Veritabanı bağlantısı
- Temel sayfalar
- İlk canlı geliştirme ortamı

### Tamamlanma kriteri

- Frontend backend ile iletişim kurabilmeli.
- Kullanıcı arayüzünde temel sayfalar açılabilmeli.
- Veritabanına örnek kayıt eklenebilmeli.

---

## Faz 2 — Kullanıcı ve Arazi Yönetimi

### Amaç

Kullanıcının sisteme kayıt olup kendi arazisini oluşturabilmesini sağlamak.

### Görevler

#### Kimlik doğrulama

- Kullanıcı kayıt API’si
- Giriş API’si
- Şifre hashleme
- Token tabanlı oturum
- Çıkış işlemi
- Yetkilendirme kontrolü

#### Arazi yönetimi

- Arazi oluşturma
- Arazi listeleme
- Arazi detay görüntüleme
- Arazi güncelleme
- Arazi silme
- Kullanıcı-arazi ilişkisi

#### Ürün yönetimi

- Ürün türü seçimi
- Ekim tarihi
- Gelişim dönemi
- Tahmini hasat tarihi

### Kabul kriterleri

- Kullanıcı kayıt olabilmeli.
- Giriş yapabilmeli.
- En az bir arazi oluşturabilmeli.
- Yalnızca kendi arazilerini görebilmeli.
- Arazi ve ürün bilgilerini güncelleyebilmeli.

---

## Faz 3 — Veri Girişi ve Veri Kaynakları

### Amaç

Platforma üç farklı kaynaktan veri alınmasını sağlamak.

### 3.1. Manuel veri girişi

#### Görevler

- Manuel veri giriş formu
- Veri aralık kontrolü
- Zorunlu alan kontrolü
- Opsiyonel alan desteği
- Veri kaynağı etiketi
- Kayıt zamanı
- Kullanıcı doğrulama mesajı

#### Girilecek veriler

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

### 3.2. IoT/bulut veri akışı simülasyonu

#### Görevler

- IoT cihaz ekleme ekranı
- Cihaz kimliği alanı
- API anahtarı alanı
- Bağlantı testi
- Simülasyon veri üretici servisi
- Zamanlanmış veri aktarımı
- Son veri zamanı
- Bağlantı durumu
- Veri kesintisi uyarısı

#### Teknik seçenekler

- MQTT
- REST API
- Python scheduler
- Background worker

### 3.3. Test veri seti

#### Görevler

- Hazır test senaryolarını oluşturmak
- Veri tabanına eklemek
- Senaryo seçme ekranı
- Seçilen senaryoyu aktif veri olarak yüklemek

#### Test senaryoları

- Normal durum
- Kuruma riski
- Aşırı sulama
- Sensör anomalisi
- Tuzluluk riski
- Sulama sonrası beklenmeyen sonuç

### Kabul kriterleri

- Kullanıcı manuel veri girebilmeli.
- IoT simülasyon verisi sisteme akabilmeli.
- Hazır senaryo seçilebilmeli.
- Her veri kaynağı açıkça etiketlenmeli.
- Veriler zaman damgasıyla kaydedilmeli.

---

## Faz 4 — Veri Doğrulama Katmanı

### Amaç

Hatalı, eksik veya gerçekçi olmayan verilerin AI modeline doğrudan gönderilmesini önlemek.

### Görevler

- Zorunlu veri kontrolü
- Veri aralık kontrolü
- Eksik veri kontrolü
- Eski veri kontrolü
- Ani değişim kontrolü
- Çelişkili veri kontrolü
- Veri güven skoru
- Veri kalite uyarıları

### Örnek kurallar

- Toprak nemi 0–100 aralığında olmalı.
- Hava nemi 0–100 aralığında olmalı.
- pH 0–14 aralığında olmalı.
- Son veri 24 saatten eskiyse “güncel değil” uyarısı verilmeli.
- Nem değeri kısa sürede aşırı değişirse anomali işaretlenmeli.

### Çıktılar

- Veri güven skoru
- Uyarı listesi
- Analize uygun/veri yetersiz kararı

### Kabul kriterleri

- Hatalı veri yakalanmalı.
- Eksik veri durumunda kullanıcı bilgilendirilmeli.
- AI modeline yalnızca doğrulanmış veri gönderilmeli.

---

## Faz 5 — Yapay Zekâ ve Karar Motoru

### Amaç

Sulama ihtiyacını, riskleri ve gelecekteki nem seviyesini tahmin etmek.

### 5.1. Kural tabanlı motor

#### Görevler

- Temel sulama karar kuralları
- Risk eşikleri
- Veri eksikliği durumları
- Güvenlik sınırları
- Açıklama üretimi

#### Örnek kural

- Nem düşük
- Sıcaklık yüksek
- Yağış ihtimali düşük
- Son sulama eski

ise sulama öner.

### 5.2. Makine öğrenmesi modeli

#### Görevler

- Test veri setini hazırlamak
- Özellik mühendisliği
- Eğitim/test ayrımı
- Random Forest modeli
- XGBoost modeli
- Regresyon modeli
- Performans karşılaştırması
- En uygun modeli seçmek
- Modeli API’ye bağlamak

### 5.3. Anomali tespiti

#### Görevler

- Isolation Forest veya kural tabanlı anomali tespiti
- Ani nem değişimi
- Veri kesintisi
- Gerçekçi olmayan ölçüm
- Sulama sonrası beklenmeyen sonuç

### 5.4. Açıklanabilir AI

#### Görevler

- Karar gerekçesi üretmek
- En etkili değişkenleri göstermek
- Güven skoru üretmek
- Düşük güven durumunda uyarı vermek

### Kabul kriterleri

- Sistem sulama gerekli/gereksiz kararı üretmeli.
- 24, 48 ve 72 saatlik tahmin üretmeli.
- Risk seviyesi göstermeli.
- Kararın gerekçesi açıklanmalı.
- Düşük güvenli öneriler işaretlenmeli.

---

## Faz 6 — Dijital İkiz ve Senaryo Simülasyonu

### Amaç

Kullanıcının farklı sulama kararlarının olası sonuçlarını karşılaştırabilmesini sağlamak.

### Görevler

- Mevcut durum modeli
- Geçmiş veri grafiği
- 72 saatlik tahmin grafiği
- Tarla/bölge görünümü
- Nem durumu görselleştirmesi
- Risk alanı gösterimi
- Senaryo motoru
- Senaryo karşılaştırma tablosu

### Senaryolar

- Şimdi sulama
- 12 saat sonra sulama
- 24 saat sonra sulama
- Sulama yapmama
- Sulama süresini azaltma
- Sulama süresini artırma

### Her senaryo için gösterilecekler

- Tahmini nem
- Tahmini su kullanımı
- Risk seviyesi
- Bitki stresi
- Önerilen karar

### Kabul kriterleri

- En az iki senaryo karşılaştırılabilmeli.
- Sonuçlar grafik veya tabloyla gösterilmeli.
- Sistem önerilen senaryoyu vurgulamalı.

---

## Faz 7 — Sulama Otomasyonu

### Amaç

AI önerisi sonrasında kullanıcı onaylı sanal sulama akışını çalıştırmak.

### Görevler

- Sulamayı başlat butonu
- Sulamayı durdur butonu
- Sanal vana durumu
- Pompa durumu
- Sulama süresi
- Geri sayım
- Su miktarı hesaplama
- Sulama olayı kaydı
- Sulama sonrası veri güncelleme
- AI yeniden analiz

### İş akışı

1. AI sulama önerisi üretir.
2. Kullanıcı öneriyi onaylar.
3. Sanal vana açılır.
4. Sulama süresi başlar.
5. Tahmini su miktarı hesaplanır.
6. Süre tamamlanır.
7. Vana kapanır.
8. Olay kaydedilir.
9. Nem değeri güncellenir.
10. AI yeniden analiz yapar.

### Kabul kriterleri

- Kullanıcı onayı olmadan otomasyon başlamamalı.
- Vana durumu görünür olmalı.
- İşlem geçmişe kaydedilmeli.
- Sulama sonrası risk seviyesi güncellenmeli.

---

## Faz 8 — Dashboard ve Raporlama

### Amaç

Kullanıcının toprağın durumunu, AI kararını ve geçmiş işlemleri tek ekranda görebilmesini sağlamak.

### Dashboard bileşenleri

- Mevcut nem
- Toprak sıcaklığı
- Hava sıcaklığı
- Yağış ihtimali
- Risk seviyesi
- AI önerisi
- Güven skoru
- Veri kaynağı
- Son güncelleme
- Sensör durumu
- 72 saatlik tahmin

### Raporlama

- Günlük su kullanımı
- Sulama geçmişi
- Nem değişimi
- AI öneri geçmişi
- Anomali kayıtları
- Tahmini su tasarrufu

### Kabul kriterleri

- Kullanıcı ana durumu tek ekranda anlayabilmeli.
- Geçmiş kayıtlar filtrelenebilmeli.
- Grafikler okunabilir olmalı.
- Kritik riskler görünür olmalı.

---

## Faz 9 — Test ve Kalite Güvence

### Amaç

MVP’nin hatasız, tutarlı ve sunuma hazır çalışmasını sağlamak.

### Test türleri

#### Fonksiyonel test

- Kayıt
- Giriş
- Arazi oluşturma
- Veri girişi
- IoT akışı
- AI tahmini
- Senaryo simülasyonu
- Sulama otomasyonu

#### Veri testi

- Eksik veri
- Hatalı veri
- Aşırı değer
- Eski veri
- Çelişkili veri

#### AI testi

- Normal senaryo
- Kuruma riski
- Aşırı sulama
- Sensör anomalisi
- Düşük güven skoru

#### UX testi

- Kullanıcı öneriyi anlayabiliyor mu?
- Ekranlar karmaşık mı?
- Ana görevler kolay tamamlanıyor mu?
- Mobil görünüm kullanılabilir mi?

#### Performans testi

- Dashboard yüklenme süresi
- Tahmin süresi
- API cevap süresi
- Eşzamanlı kullanıcı testi

### Kabul kriterleri

- Kritik hata bulunmamalı.
- Demo akışı kesintisiz çalışmalı.
- Tahmin 5 saniye içinde üretilmeli.
- Dashboard 3 saniye içinde yüklenmeli.

---

## Faz 10 — Canlıya Alma

### Amaç

Uygulamayı erişilebilir bir URL üzerinden çalışır hâle getirmek.

### Görevler

- Frontend deploy
- Backend deploy
- Veritabanı prod ayarı
- Ortam değişkenleri
- HTTPS
- Domain veya demo URL
- Log takibi
- Hata izleme
- Yedekleme
- Demo kullanıcı hesabı

### Önerilen servisler

- Frontend: Vercel
- Backend: Render veya Railway
- Veritabanı: Supabase
- Alternatif hızlı çözüm: Streamlit Cloud

### Kabul kriterleri

- Uygulama dış ağdan açılabilmeli.
- Demo hesabı çalışmalı.
- API bağlantıları aktif olmalı.
- Veriler kalıcı saklanmalı.

---

## Faz 11 — Demo ve Sunum Hazırlığı

### Amaç

Jüriye kısa, net ve hatasız bir demo sunmak.

### Demo akışı

1. Kullanıcı giriş yapar.
2. Arazi oluşturur.
3. IoT veri kaynağını seçer.
4. Kontrollü test verisi sisteme gelir.
5. Dashboard kuruma riskini gösterir.
6. AI sulama önerisi verir.
7. Kullanıcı 24 saat bekleme senaryosunu çalıştırır.
8. Risk kritik seviyeye çıkar.
9. Kullanıcı şimdi sulama senaryosunu seçer.
10. Sanal vana açılır.
11. Sulama tamamlanır.
12. Nem değeri güncellenir.
13. Risk seviyesi düşer.
14. Tahmini su tasarrufu gösterilir.

### Sunum sırası

- Problem
- Gerçek problem
- Çözüm
- AI’nin rolü
- Veri kaynakları
- Dijital ikiz
- Canlı demo
- Etki
- İş modeli
- Yol haritası

---

## 4. Önerilen Sprint Planı

## Sprint 1 — Temel altyapı

- Proje kurulumu
- Veritabanı
- Kayıt/giriş
- Arazi oluşturma
- Temel dashboard

## Sprint 2 — Veri katmanı

- Manuel veri girişi
- Test verisi
- IoT simülasyonu
- Veri doğrulama

## Sprint 3 — AI katmanı

- Kural tabanlı motor
- ML modeli
- Risk sınıflandırması
- Açıklanabilir öneri

## Sprint 4 — Dijital ikiz

- 72 saatlik tahmin
- Senaryo simülasyonu
- Grafikler
- Dijital ikiz ekranı

## Sprint 5 — Otomasyon ve raporlama

- Sanal sulama
- Olay kaydı
- Su kullanımı
- Rapor ekranı

## Sprint 6 — Test ve canlıya alma

- Hata düzeltme
- UX iyileştirme
- Deploy
- Demo provası

---

## 5. Ekip Görev Dağılımı

## Ürün yöneticisi

- Kapsam yönetimi
- PRD takibi
- Önceliklendirme
- Sprint yönetimi
- Demo akışı

## Frontend geliştirici

- Kullanıcı ekranları
- Dashboard
- Senaryo ekranı
- IoT cihaz ekranı
- Responsive tasarım

## Backend geliştirici

- API
- Veritabanı
- Kimlik doğrulama
- Veri akışı
- Otomasyon işlemleri

## AI/veri geliştirici

- Test veri seti
- Veri işleme
- Model geliştirme
- Risk analizi
- Açıklanabilir AI

## IoT/otomasyon sorumlusu

- IoT simülasyonu
- MQTT/REST veri akışı
- Cihaz yönetimi
- Sanal vana

## UX ve sunum sorumlusu

- Arayüz tasarımı
- Kullanıcı testi
- Sunum tasarımı
- Hikâyeleştirme
- Demo senaryosu

---

## 6. Önceliklendirme

### P0 — Zorunlu

- Kayıt/giriş / demo-login
- Arazi oluşturma
- Manuel veri girişi
- IoT simülasyonu
- Veri doğrulama
- Sulama tahmini
- 72 saatlik tahmin
- Senaryo simülasyonu
- Sanal sulama
- Canlıya alma — **tamam** (Vercel + Render)

## P1 — Önemli

- [x] Laboratuvar raporu / manuel lab girişi (API + UI; dosya zorunlu; gerçek OCR yok)
- [x] Yönetim bölgeleri (`/zones`)
- [x] Field Node JSON ingest (`POST /iot/ingest`, çift derinlik)
- [x] Agro malzemeler (reçetesiz kullanım kaydı)
- [x] Open-Meteo + Leaflet OSM
- [x] OpenRouter hibrit açıklama (opsiyonel)
- Anomali tespiti (temel tamam; veri kesintisi kısmi)
- Güven skoru (lab puanı — kısmi)
- Sulama geçmişi (tamam)
- Su tasarrufu raporu (hub KPI tamam)
- Cihaz bağlantı ekranı (tamam)
- Field Node Lite firmware (donanım — `iot-mimarisi.md`)

## P2 — Sonraki sürüm

- Gerçek sensör entegrasyonu / MQTT
- Gerçek OCR / lab API
- Gerçek ödeme
- ML (Scikit-learn / XGBoost)
- Uydu ve drone
- Gübre reçetesi (ayrı ürün)

---

## 7. Bağımlılıklar

| Görev | Bağımlılık |
|---|---|
| AI tahmini | Veri şeması ve test veri seti |
| Dashboard | Backend API ve veritabanı |
| IoT simülasyonu | SensorReadings yapısı |
| Senaryo motoru | Tahmin modeli |
| Otomasyon | AI önerisi ve kullanıcı onayı |
| Raporlama | Sulama ve tahmin geçmişi |
| Canlıya alma | Tüm P0 görevleri |

---

## 8. Ana Riskler

### Kapsam büyümesi

**Risk:** Çok fazla özellik eklenmesi.

**Önlem:** P0 dışındaki özellikleri sonraya bırakmak.

### Yapay veri bağımlılığı

**Risk:** Modelin gerçek sahada çalışacağının sanılması.

**Önlem:** Prototip ve saha doğrulaması ayrımını açıkça belirtmek.

### IoT simülasyonunun yanlış sunulması

**Risk:** Gerçek bağlantı varmış gibi görünmesi.

**Önlem:** Arayüzde “simülasyon” etiketi.

### AI güvenilirliği

**Risk:** Yanlış sulama önerisi.

**Önlem:** Kullanıcı onayı ve güvenlik kuralları.

### Demo hatası

**Risk:** Canlı sunumda sistemin bozulması.

**Önlem:** Kontrollü demo verisi ve yedek demo videosu.

---

## 9. Tamamlanma Tanımı

Bir özellik tamamlanmış sayılır, eğer:

- Kod geliştirilmişse
- Test edilmişse (mümkünse otomatik test)
- Hata kontrolü yapılmışsa
- Veritabanıyla çalışıyorsa
- Arayüzde görünüyorsa (API-only özellikler `Progress.md`’de “API” olarak işaretlenir)
- Kabul kriterlerini karşılıyorsa
- Demo akışına dahil edilebiliyorsa
- `Progress.md` güncellenmişse

Not: §10 checklist’te `[x]` olan maddeler as-built MVP’ye göredir. Canlı URL ve demo hesap tamam; sunum provası açıktır.

---

## 10. MVP Tamamlanma Kontrol Listesi

- [x] Kullanıcı kayıt sistemi
- [x] Giriş sistemi
- [x] Arazi oluşturma
- [x] Ürün bilgisi ekleme
- [x] Manuel veri girişi
- [x] IoT simülasyonu
- [x] Test veri seti
- [x] Veri doğrulama
- [x] Veri güven skoru
- [x] AI sulama tahmini
- [x] 24/48/72 saat nem tahmini
- [x] Risk sınıflandırması
- [x] Anomali tespiti
- [x] Açıklanabilir öneri
- [x] Senaryo simülasyonu
- [x] Sanal vana
- [x] Sulama geçmişi
- [x] Su kullanımı raporu (hub KPI)
- [x] Laboratuvar analizi (manuel + dosya + birim + onay) — gerçek OCR P2
- [ ] Lab OCR (gerçek) — P2
- [x] IoT Field Node mimari dokümanı (`iot-mimarisi.md`)
- [x] `POST /iot/ingest` + yönetim bölgeleri
- [x] Dashboard
- [x] Canlı URL
- [x] Demo hesabı
- [ ] Sunum demosu

---

## 11. Sonuç

AgriTwin AI geliştirme planının temel stratejisi, geniş kapsamlı ve tamamlanması zor bir dijital ikiz yerine, sulama kararına odaklanan çalışan bir prototip geliştirmektir.

Başarı ölçütü özellik sayısı değildir.

Başarı ölçütü:

> Kullanıcının veri girebildiği, sistemin veriyi analiz ettiği, AI’nin sulama önerisi ürettiği, senaryoların karşılaştırıldığı ve otomasyonun çalıştığı uçtan uca deneyimin kesintisiz biçimde gösterilebilmesidir.